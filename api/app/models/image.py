"""
Image database model for AstroAI-Core

Stores astronomical image metadata from NASA Image Library
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Index, ARRAY
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Image(Base):
    """
    Image model representing astronomical images and their metadata.
    
    Data sources:
    - NASA Image and Video Library
    - Hubble Space Telescope
    - James Webb Space Telescope
    - Other NASA missions
    """
    
    __tablename__ = 'images'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identification
    nasa_id = Column(String(100), nullable=False, index=True, unique=True, comment="NASA unique identifier")
    title = Column(String(500), nullable=False, comment="Image title")
    description = Column(Text, nullable=True, comment="Image description")
    
    # URLs
    image_url = Column(String(1000), nullable=True, comment="Full resolution image URL")
    thumbnail_url = Column(String(1000), nullable=True, comment="Thumbnail image URL")
    manifest_url = Column(String(1000), nullable=True, comment="Manifest JSON URL")
    
    # Metadata
    date_created = Column(DateTime(timezone=True), nullable=True, comment="Image creation date")
    date_published = Column(DateTime(timezone=True), nullable=True, comment="Publication date")
    
    # Organization
    center = Column(String(100), nullable=True, comment="NASA center responsible (e.g., 'GSFC', 'JPL')")
    mission = Column(String(100), nullable=True, comment="Mission name (e.g., 'Hubble', 'JWST')")
    media_type = Column(String(50), nullable=True, default='image', comment="Media type")
    
    # Keywords and tags
    keywords = Column(PG_ARRAY(String), nullable=True, comment="Search keywords")
    
    # Technical details
    telescope = Column(String(100), nullable=True, comment="Telescope/instrument used")
    filter = Column(String(100), nullable=True, comment="Filter used")
    exposure_time = Column(String(100), nullable=True, comment="Exposure time")
    resolution = Column(String(50), nullable=True, comment="Image resolution")
    
    # Astronomical data
    target_name = Column(String(200), nullable=True, comment="Astronomical target name")
    target_type = Column(String(50), nullable=True, comment="Target type (Galaxy, Nebula, Star, etc.)")
    constellation = Column(String(50), nullable=True, comment="Constellation containing target")
    right_ascension = Column(String(50), nullable=True, comment="Right ascension (J2000)")
    declination = Column(String(50), nullable=True, comment="Declination (J2000)")
    redshift = Column(Float, nullable=True, comment="Redshift value (for galaxies)")
    distance_ly = Column(Float, nullable=True, comment="Distance in light years")
    
    # Processing status
    is_processed = Column(Boolean, default=False, comment="Whether image has been processed by AI")
    analysis_results = Column(JSON, nullable=True, comment="AI analysis results")
    
    # Data quality
    quality_score = Column(String(20), nullable=True, default='good', comment="Data quality assessment")
    
    # Metadata
    data_source = Column(String(50), nullable=True, comment="Source of data")
    raw_data = Column(JSON, nullable=True, comment="Original JSON metadata from API")
    local_path = Column(String(500), nullable=True, comment="Local file path if downloaded")
    file_size_bytes = Column(Integer, nullable=True, comment="File size in bytes")
    created_at = Column(DateTime(timezone=True), default=func.now(), comment="Record creation time")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), comment="Last update time")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_images_center', 'center'),
        Index('idx_images_mission', 'mission'),
        Index('idx_images_target_type', 'target_type'),
        Index('idx_images_constellation', 'constellation'),
        Index('idx_images_date_created', 'date_created'),
        Index('idx_images_is_processed', 'is_processed'),
        Index('idx_images_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Image(nasa_id='{self.nasa_id}', title='{self.title[:50]}...')>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'nasa_id': self.nasa_id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'thumbnail_url': self.thumbnail_url,
            'manifest_url': self.manifest_url,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_published': self.date_published.isoformat() if self.date_published else None,
            'center': self.center,
            'mission': self.mission,
            'media_type': self.media_type,
            'keywords': self.keywords,
            'telescope': self.telescope,
            'target_name': self.target_name,
            'target_type': self.target_type,
            'constellation': self.constellation,
            'distance_ly': self.distance_ly,
            'is_processed': self.is_processed,
            'analysis_results': self.analysis_results,
            'quality_score': self.quality_score,
            'data_source': self.data_source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_nasa_data(cls, data: dict) -> 'Image':
        """
        Create Image instance from NASA API data.
        
        Args:
            data: Dictionary from NASA Image Library
            
        Returns:
            Image instance
        """
        return cls(
            nasa_id=data.get('nasa_id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            image_url=data.get('image_url'),
            thumbnail_url=data.get('thumbnail_url'),
            date_created=cls._parse_date(data.get('date_created')),
            center=data.get('center', ''),
            keywords=data.get('keywords', []),
            media_type=data.get('media_type', 'image'),
            data_source=data.get('data_source', 'NASA'),
            raw_data=data
        )
    
    @staticmethod
    def _parse_date(date_string) -> DateTime:
        """Parse date string to datetime."""
        if not date_string:
            return None
        try:
            from datetime import datetime
            if 'T' in str(date_string):
                return datetime.fromisoformat(str(date_string).replace('Z', '+00:00'))
            return datetime.strptime(str(date_string), '%Y-%m-%d')
        except (ValueError, TypeError):
            return None
