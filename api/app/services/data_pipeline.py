"""
Data Pipeline for AstroAI-Core

Handles data processing, cleaning, validation, and database storage.

Features:
- Data cleaning and standardization
- Format conversion (JSON → Database)
- Data quality checks
- Incremental update mechanism

Author: AstroAI-Core Team
Date: 2026-03-06
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models.exoplanet import Exoplanet
from app.models.star import Star
from app.models.image import Image


class DataQuality(Enum):
    """Data quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"


@dataclass
class ProcessingResult:
    """Result of data processing operation."""
    success: bool
    records_processed: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    errors: List[str] = field(default_factory=list)
    quality_score: DataQuality = DataQuality.GOOD


class DataPipeline:
    """
    Data processing pipeline for astronomical data.
    
    Handles:
    - Data cleaning and normalization
    - Schema validation
    - Database insertion with upsert logic
    - Incremental updates
    - Quality scoring
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        Initialize data pipeline.
        
        Args:
            db_session: Optional database session
        """
        self.db_session = db_session
        self._session_owner = False
    
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        if self.db_session is None:
            self.db_session = await async_session_maker()
            self._session_owner = True
        return self.db_session
    
    async def close(self):
        """Close database session if we own it."""
        if self._session_owner and self.db_session:
            await self.db_session.close()
            self.db_session = None
            self._session_owner = False
    
    def _clean_string(self, value: Any, max_length: int = 255) -> str:
        """Clean and truncate string value."""
        if value is None:
            return ""
        cleaned = str(value).strip()
        return cleaned[:max_length] if len(cleaned) > max_length else cleaned
    
    def _clean_numeric(self, value: Any, default: float = 0.0) -> float:
        """Clean numeric value."""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _clean_boolean(self, value: Any, default: bool = False) -> bool:
        """Clean boolean value."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes')
    
    def _validate_exoplanet_data(self, planet: Dict) -> Tuple[bool, DataQuality]:
        """
        Validate exoplanet data quality.
        
        Returns:
            Tuple of (is_valid, quality_score)
        """
        issues = []
        score = DataQuality.EXCELLENT
        
        # Required fields
        if not planet.get('pl_name'):
            issues.append("Missing planet name")
            return False, DataQuality.INVALID
        
        # Check key measurements
        has_radius = planet.get('pl_radj') is not None
        has_mass = planet.get('pl_massj') is not None
        has_period = planet.get('pl_orbper') is not None
        has_distance = planet.get('sy_dist') is not None
        
        if not has_radius and not has_mass:
            issues.append("Missing both radius and mass")
            score = DataQuality.POOR
        elif not has_radius or not has_mass:
            score = DataQuality.FAIR
        
        if not has_period:
            issues.append("Missing orbital period")
            score = DataQuality.FAIR if score != DataQuality.POOR else score
        
        if not has_distance:
            issues.append("Missing system distance")
        
        return True, score
    
    def _validate_star_data(self, star: Dict) -> Tuple[bool, DataQuality]:
        """Validate star data quality."""
        if not star.get('hostname'):
            return False, DataQuality.INVALID
        
        # Check for key stellar parameters
        has_distance = star.get('sy_dist') is not None
        has_magnitude = star.get('sy_vmag') is not None
        
        if has_distance and has_magnitude:
            return True, DataQuality.EXCELLENT
        elif has_distance or has_magnitude:
            return True, DataQuality.GOOD
        else:
            return True, DataQuality.FAIR
    
    def _validate_image_data(self, image: Dict) -> Tuple[bool, DataQuality]:
        """Validate image metadata quality."""
        if not image.get('nasa_id'):
            return False, DataQuality.INVALID
        
        has_url = image.get('image_url') is not None
        has_title = bool(image.get('title'))
        has_description = bool(image.get('description'))
        
        if has_url and has_title:
            return True, DataQuality.EXCELLENT
        elif has_title:
            return True, DataQuality.GOOD
        else:
            return True, DataQuality.FAIR
    
    async def process_exoplanets(
        self,
        planets: List[Dict],
        batch_size: int = 100
    ) -> ProcessingResult:
        """
        Process and store exoplanet data.
        
        Args:
            planets: List of exoplanet dictionaries
            batch_size: Batch size for database operations
            
        Returns:
            ProcessingResult with statistics
        """
        result = ProcessingResult(success=True)
        result.records_processed = len(planets)
        
        session = await self.get_session()
        
        try:
            for i, planet in enumerate(planets):
                try:
                    # Validate
                    is_valid, quality = self._validate_exoplanet_data(planet)
                    if not is_valid:
                        result.records_skipped += 1
                        result.errors.append(f"Invalid planet {i}: {planet.get('pl_name', 'unknown')}")
                        continue
                    
                    # Clean and prepare data
                    exoplanet_data = {
                        'name': self._clean_string(planet.get('pl_name'), 100),
                        'hostname': self._clean_string(planet.get('hostname'), 100),
                        'discovery_method': self._clean_string(planet.get('discoverymethod'), 50),
                        'orbital_period': self._clean_numeric(planet.get('pl_orbper')),
                        'radius_jupiter': self._clean_numeric(planet.get('pl_radj')),
                        'mass_jupiter': self._clean_numeric(planet.get('pl_massj')),
                        'equilibrium_temp': self._clean_numeric(planet.get('pl_eqt')),
                        'distance_ly': self._clean_numeric(planet.get('sy_dist')),
                        'visual_magnitude': self._clean_numeric(planet.get('sy_vmag')),
                        'discovery_year': self._extract_year(planet.get('pl_disc')),
                        'data_source': self._clean_string(planet.get('data_source', 'Unknown'), 50),
                        'quality_score': quality.value,
                        'raw_data': planet,
                        'fetched_at': datetime.fromisoformat(planet.get('fetched_at', datetime.now().isoformat())) if planet.get('fetched_at') else datetime.now()
                    }
                    
                    # Upsert logic
                    existing = await self._find_exoplanet_by_name(session, exoplanet_data['name'])
                    
                    if existing:
                        await self._update_exoplanet(session, existing.id, exoplanet_data)
                        result.records_updated += 1
                    else:
                        await self._insert_exoplanet(session, exoplanet_data)
                        result.records_inserted += 1
                    
                    # Commit in batches
                    if (i + 1) % batch_size == 0:
                        await session.commit()
                        
                except Exception as e:
                    result.errors.append(f"Error processing planet {i}: {str(e)}")
                    result.records_skipped += 1
            
            # Final commit
            await session.commit()
            result.success = len(result.errors) == 0
            
        except Exception as e:
            await session.rollback()
            result.success = False
            result.errors.append(f"Batch processing failed: {str(e)}")
        
        return result
    
    async def process_stars(
        self,
        stars: List[Dict],
        batch_size: int = 100
    ) -> ProcessingResult:
        """
        Process and store star data.
        
        Args:
            stars: List of star dictionaries
            batch_size: Batch size for database operations
            
        Returns:
            ProcessingResult with statistics
        """
        result = ProcessingResult(success=True)
        result.records_processed = len(stars)
        
        session = await self.get_session()
        
        try:
            for i, star in enumerate(stars):
                try:
                    is_valid, quality = self._validate_star_data(star)
                    if not is_valid:
                        result.records_skipped += 1
                        continue
                    
                    star_data = {
                        'name': self._clean_string(star.get('hostname'), 100),
                        'constellation': self._clean_string(star.get('constellation'), 50),
                        'spectral_type': self._clean_string(star.get('spectral_type'), 20),
                        'distance_ly': self._clean_numeric(star.get('sy_dist')),
                        'visual_magnitude': self._clean_numeric(star.get('sy_vmag')),
                        'mass_solar': self._clean_numeric(star.get('st_mass')),
                        'radius_solar': self._clean_numeric(star.get('st_rad')),
                        'temperature': self._clean_numeric(star.get('st_teff')),
                        'data_source': self._clean_string(star.get('data_source', 'Unknown'), 50),
                        'quality_score': quality.value,
                        'raw_data': star
                    }
                    
                    existing = await self._find_star_by_name(session, star_data['name'])
                    
                    if existing:
                        await self._update_star(session, existing.id, star_data)
                        result.records_updated += 1
                    else:
                        await self._insert_star(session, star_data)
                        result.records_inserted += 1
                    
                    if (i + 1) % batch_size == 0:
                        await session.commit()
                        
                except Exception as e:
                    result.errors.append(f"Error processing star {i}: {str(e)}")
                    result.records_skipped += 1
            
            await session.commit()
            result.success = len(result.errors) == 0
            
        except Exception as e:
            await session.rollback()
            result.success = False
            result.errors.append(f"Batch processing failed: {str(e)}")
        
        return result
    
    async def process_images(
        self,
        images: List[Dict],
        batch_size: int = 50
    ) -> ProcessingResult:
        """
        Process and store image metadata.
        
        Args:
            images: List of image dictionaries
            batch_size: Batch size for database operations
            
        Returns:
            ProcessingResult with statistics
        """
        result = ProcessingResult(success=True)
        result.records_processed = len(images)
        
        session = await self.get_session()
        
        try:
            for i, image in enumerate(images):
                try:
                    is_valid, quality = self._validate_image_data(image)
                    if not is_valid:
                        result.records_skipped += 1
                        continue
                    
                    image_data = {
                        'nasa_id': self._clean_string(image.get('nasa_id'), 100),
                        'title': self._clean_string(image.get('title'), 500),
                        'description': self._clean_string(image.get('description'), 5000),
                        'image_url': self._clean_string(image.get('image_url'), 1000),
                        'thumbnail_url': self._clean_string(image.get('thumbnail_url'), 1000),
                        'date_created': self._parse_date(image.get('date_created')),
                        'center': self._clean_string(image.get('center'), 100),
                        'keywords': image.get('keywords', []),
                        'media_type': self._clean_string(image.get('media_type'), 50),
                        'data_source': self._clean_string(image.get('data_source', 'Unknown'), 50),
                        'quality_score': quality.value,
                        'raw_data': image
                    }
                    
                    existing = await self._find_image_by_nasa_id(session, image_data['nasa_id'])
                    
                    if existing:
                        await self._update_image(session, existing.id, image_data)
                        result.records_updated += 1
                    else:
                        await self._insert_image(session, image_data)
                        result.records_inserted += 1
                    
                    if (i + 1) % batch_size == 0:
                        await session.commit()
                        
                except Exception as e:
                    result.errors.append(f"Error processing image {i}: {str(e)}")
                    result.records_skipped += 1
            
            await session.commit()
            result.success = len(result.errors) == 0
            
        except Exception as e:
            await session.rollback()
            result.success = False
            result.errors.append(f"Batch processing failed: {str(e)}")
        
        return result
    
    def _extract_year(self, disc_string: Any) -> Optional[int]:
        """Extract year from discovery date string."""
        if not disc_string:
            return None
        try:
            # Try parsing various date formats
            disc_str = str(disc_string)
            if len(disc_str) >= 4:
                return int(disc_str[:4])
        except (ValueError, TypeError):
            pass
        return None
    
    def _parse_date(self, date_string: Any) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_string:
            return None
        try:
            # Handle ISO format
            if 'T' in str(date_string):
                return datetime.fromisoformat(str(date_string).replace('Z', '+00:00'))
            # Handle YYYY-MM-DD
            return datetime.strptime(str(date_string), '%Y-%m-%d')
        except (ValueError, TypeError):
            return None
    
    async def _find_exoplanet_by_name(self, session: AsyncSession, name: str) -> Optional[Any]:
        """Find exoplanet by name."""
        from sqlalchemy import select
        result = await session.execute(
            select(Exoplanet).where(Exoplanet.name == name)
        )
        return result.scalar_one_or_none()
    
    async def _insert_exoplanet(self, session: AsyncSession, data: Dict):
        """Insert new exoplanet."""
        exoplanet = Exoplanet(**data)
        session.add(exoplanet)
    
    async def _update_exoplanet(self, session: AsyncSession, planet_id: int, data: Dict):
        """Update existing exoplanet."""
        from sqlalchemy import update
        await session.execute(
            update(Exoplanet)
            .where(Exoplanet.id == planet_id)
            .values(**data)
        )
    
    async def _find_star_by_name(self, session: AsyncSession, name: str) -> Optional[Any]:
        """Find star by name."""
        from sqlalchemy import select
        result = await session.execute(
            select(Star).where(Star.name == name)
        )
        return result.scalar_one_or_none()
    
    async def _insert_star(self, session: AsyncSession, data: Dict):
        """Insert new star."""
        star = Star(**data)
        session.add(star)
    
    async def _update_star(self, session: AsyncSession, star_id: int, data: Dict):
        """Update existing star."""
        from sqlalchemy import update
        await session.execute(
            update(Star)
            .where(Star.id == star_id)
            .values(**data)
        )
    
    async def _find_image_by_nasa_id(self, session: AsyncSession, nasa_id: str) -> Optional[Any]:
        """Find image by NASA ID."""
        from sqlalchemy import select
        result = await session.execute(
            select(Image).where(Image.nasa_id == nasa_id)
        )
        return result.scalar_one_or_none()
    
    async def _insert_image(self, session: AsyncSession, data: Dict):
        """Insert new image."""
        image = Image(**data)
        session.add(image)
    
    async def _update_image(self, session: AsyncSession, image_id: int, data: Dict):
        """Update existing image."""
        from sqlalchemy import update
        await session.execute(
            update(Image)
            .where(Image.id == image_id)
            .values(**data)
        )
    
    async def get_incremental_update_stats(self) -> Dict[str, Any]:
        """
        Get statistics for incremental updates.
        
        Returns:
            Dictionary with last update times and counts
        """
        session = await self.get_session()
        
        try:
            from sqlalchemy import select, func
            
            # Get latest timestamps
            exoplanet_latest = await session.execute(
                select(func.max(Exoplanet.fetched_at))
            )
            star_latest = await session.execute(
                select(func.max(Star.created_at))
            )
            image_latest = await session.execute(
                select(func.max(Image.created_at))
            )
            
            # Get counts
            exoplanet_count = await session.execute(
                select(func.count(Exoplanet.id))
            )
            star_count = await session.execute(
                select(func.count(Star.id))
            )
            image_count = await session.execute(
                select(func.count(Image.id))
            )
            
            return {
                'exoplanets': {
                    'count': exoplanet_count.scalar(),
                    'last_update': exoplanet_latest.scalar()
                },
                'stars': {
                    'count': star_count.scalar(),
                    'last_update': star_latest.scalar()
                },
                'images': {
                    'count': image_count.scalar(),
                    'last_update': image_latest.scalar()
                }
            }
        except Exception as e:
            return {'error': str(e)}


async def run_pipeline(
    exoplanets: Optional[List[Dict]] = None,
    stars: Optional[List[Dict]] = None,
    images: Optional[List[Dict]] = None
) -> Dict[str, ProcessingResult]:
    """
    Run complete data pipeline.
    
    Args:
        exoplanets: List of exoplanet data
        stars: List of star data
        images: List of image data
        
    Returns:
        Dictionary with results for each data type
    """
    pipeline = DataPipeline()
    results = {}
    
    try:
        if exoplanets:
            results['exoplanets'] = await pipeline.process_exoplanets(exoplanets)
        
        if stars:
            results['stars'] = await pipeline.process_stars(stars)
        
        if images:
            results['images'] = await pipeline.process_images(images)
        
    finally:
        await pipeline.close()
    
    return results
