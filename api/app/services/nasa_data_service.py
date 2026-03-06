"""
NASA Data Service for AstroAI-Core

Provides comprehensive data fetching from NASA APIs:
- TESS Exoplanet Data
- Kepler Light Curve Data
- Hubble Image Metadata
- Data caching mechanism

Author: AstroAI-Core Team
Date: 2026-03-06
"""

import json
import time
import hashlib
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

import aiohttp
from aiohttp import ClientError, ClientTimeout

from app.core.config import settings


class CacheEntry:
    """Cache entry with expiration."""
    
    def __init__(self, data: Any, ttl_seconds: int = 3600):
        self.data = data
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class NASAAPIError(Exception):
    """Custom exception for NASA API errors."""
    pass


class NASAApiService:
    """
    Async NASA API service with caching support.
    
    Features:
    - TESS exoplanet data fetching
    - Kepler light curve data
    - Hubble image metadata
    - Automatic caching with TTL
    - Exponential backoff retry
    - Rate limiting
    """
    
    # API Endpoints
    EXOPLANET_ARCHIVE_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    NASA_IMAGE_LIBRARY_URL = "https://images-api.nasa.gov/search"
    NASA_APOD_URL = "https://api.nasa.gov/planetary/apod"
    
    # Default cache TTL (seconds)
    DEFAULT_TTL = 3600  # 1 hour
    EXOPLANET_TTL = 86400  # 24 hours
    IMAGE_TTL = 7200  # 2 hours
    
    # Rate limiting
    REQUEST_DELAY = 0.5  # seconds between requests
    MAX_RETRIES = 3
    BASE_DELAY = 1.0
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Initialize NASA API service.
        
        Args:
            api_key: NASA API key (defaults from settings)
            cache_dir: Directory for file-based cache
        """
        self.api_key = api_key or settings.NASA_API_KEY
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./data/cache")
        self.cache: Dict[str, CacheEntry] = {}
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Session for HTTP requests
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_request_time: float = 0
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'AstroAI-Core/1.0',
                    'Accept': 'application/json'
                },
                timeout=timeout
            )
        return self._session
    
    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _generate_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key from endpoint and parameters."""
        key_string = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get data from memory cache."""
        entry = self.cache.get(key)
        if entry and not entry.is_expired():
            return entry.data
        elif entry:
            del self.cache[key]
        return None
    
    def _save_to_cache(self, key: str, data: Any, ttl: int):
        """Save data to memory cache."""
        self.cache[key] = CacheEntry(data, ttl)
        
        # Also save to file cache
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'data': data,
                    'expires_at': (datetime.now() + timedelta(seconds=ttl)).isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save file cache: {e}")
    
    def _load_from_file_cache(self, key: str) -> Optional[Any]:
        """Load data from file cache."""
        cache_file = self.cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                expires_at = datetime.fromisoformat(cached['expires_at'])
                if datetime.now() < expires_at:
                    return cached['data']
                else:
                    cache_file.unlink()  # Remove expired cache
        except Exception:
            pass
        return None
    
    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.REQUEST_DELAY:
            await asyncio.sleep(self.REQUEST_DELAY - elapsed)
        self._last_request_time = time.time()
    
    async def _request_with_retry(
        self,
        url: str,
        params: Optional[Dict] = None,
        use_cache: bool = True,
        cache_ttl: int = DEFAULT_TTL
    ) -> Optional[Dict]:
        """
        Make HTTP request with exponential backoff retry and caching.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            use_cache: Whether to use caching
            cache_ttl: Cache TTL in seconds
            
        Returns:
            JSON response as dict or None
        """
        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(url, params or {})
            cached_data = self._get_from_cache(cache_key)
            if cached_data is None:
                cached_data = self._load_from_file_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        # Rate limiting
        await self._rate_limit()
        
        session = await self._get_session()
        
        for attempt in range(self.MAX_RETRIES):
            try:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Save to cache
                    if use_cache:
                        self._save_to_cache(cache_key, data, cache_ttl)
                    
                    return data
                    
            except (ClientError, asyncio.TimeoutError) as e:
                delay = self.BASE_DELAY * (2 ** attempt)
                print(f"Request failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(delay)
        
        raise NASAAPIError(f"All retry attempts failed for {url}")
    
    async def fetch_tess_exoplanets(
        self,
        count: int = 100,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Fetch TESS exoplanet data from NASA Exoplanet Archive.
        
        Args:
            count: Number of planets to fetch
            use_cache: Whether to use caching
            
        Returns:
            List of TESS exoplanet records
        """
        query = f"""
            SELECT TOP {count}
                pl_name, hostname, discoverymethod,
                pl_orbper, pl_orbpererr1, pl_orbpererr2,
                pl_radj, pl_radjerr1, pl_radjerr2,
                pl_massj, pl_massjerr1, pl_massjerr2,
                pl_eqt, sy_dist, sy_vmag,
                pl_disc, pl_disc_ref,
                tess_magnitude, tess_tmag
            FROM ps
            WHERE discoverymethod = 'Transit'
            AND hostname LIKE '%TESS%'
            ORDER BY pl_disc DESC
        """
        
        params = {
            'query': query,
            'format': 'json'
        }
        
        try:
            result = await self._request_with_retry(
                self.EXOPLANET_ARCHIVE_URL,
                params,
                use_cache=use_cache,
                cache_ttl=self.EXOPLANET_TTL
            )
            
            if result and isinstance(result, list):
                # Add metadata
                for planet in result:
                    planet['data_source'] = 'TESS'
                    planet['fetched_at'] = datetime.now().isoformat()
                return result
            return []
            
        except NASAAPIError as e:
            print(f"Failed to fetch TESS exoplanets: {e}")
            return []
    
    async def fetch_kepler_light_curves(
        self,
        kepler_id: Optional[str] = None,
        count: int = 50,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Fetch Kepler light curve data.
        
        Args:
            kepler_id: Specific Kepler object ID (optional)
            count: Number of light curves to fetch
            use_cache: Whether to use caching
            
        Returns:
            List of Kepler light curve records
        """
        where_clause = "WHERE hostname LIKE 'Kepler%'"
        if kepler_id:
            where_clause = f"WHERE pl_name = '{kepler_id}'"
        
        query = f"""
            SELECT TOP {count}
                pl_name, hostname,
                pl_orbper, pl_orbpererr1,
                pl_radj, pl_massj,
                pl_eqt, sy_dist,
                koi_period, koi_duration,
                koi_depth, koi_snr,
                kepler_name, kepler_id
            FROM ps
            {where_clause}
            ORDER BY koi_snr DESC
        """
        
        params = {
            'query': query,
            'format': 'json'
        }
        
        try:
            result = await self._request_with_retry(
                self.EXOPLANET_ARCHIVE_URL,
                params,
                use_cache=use_cache,
                cache_ttl=self.EXOPLANET_TTL
            )
            
            if result and isinstance(result, list):
                for record in result:
                    record['data_source'] = 'Kepler'
                    record['fetched_at'] = datetime.now().isoformat()
                return result
            return []
            
        except NASAAPIError as e:
            print(f"Failed to fetch Kepler data: {e}")
            return []
    
    async def fetch_hubble_images(
        self,
        query: str = "hubble deep space",
        count: int = 20,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Fetch Hubble image metadata from NASA Image Library.
        
        Args:
            query: Search query
            count: Number of images to fetch
            use_cache: Whether to use caching
            
        Returns:
            List of image metadata dictionaries
        """
        params = {
            'q': query,
            'media_type': 'image'
        }
        
        try:
            result = await self._request_with_retry(
                self.NASA_IMAGE_LIBRARY_URL,
                params,
                use_cache=use_cache,
                cache_ttl=self.IMAGE_TTL
            )
            
            if not result or 'collection' not in result:
                return []
            
            images = []
            items = result['collection']['items'][:count]
            
            for item in items:
                data = item.get('data', [{}])[0]
                image_data = {
                    'nasa_id': data.get('nasa_id', ''),
                    'title': data.get('title', ''),
                    'description': data.get('description', '')[:1000],
                    'date_created': data.get('date_created', ''),
                    'center': data.get('center', 'Unknown'),
                    'keywords': data.get('keywords', []),
                    'media_type': data.get('media_type', 'image'),
                    'image_url': None,
                    'thumbnail_url': None,
                    'data_source': 'Hubble',
                    'fetched_at': datetime.now().isoformat()
                }
                
                # Extract image URLs
                for link in item.get('links', []):
                    if link.get('rel') == 'canonical':
                        image_data['image_url'] = link['href']
                    elif link.get('rel') == 'preview':
                        image_data['thumbnail_url'] = link['href']
                
                images.append(image_data)
            
            return images
            
        except NASAAPIError as e:
            print(f"Failed to fetch Hubble images: {e}")
            return []
    
    async def fetch_apod(self, date: Optional[str] = None) -> Optional[Dict]:
        """
        Fetch Astronomy Picture of the Day.
        
        Args:
            date: Date in YYYY-MM-DD format (default: today)
            
        Returns:
            APOD data dictionary
        """
        params = {'api_key': self.api_key}
        if date:
            params['date'] = date
        
        try:
            result = await self._request_with_retry(
                self.NASA_APOD_URL,
                params,
                use_cache=True,
                cache_ttl=86400  # 24 hours
            )
            return result
        except NASAAPIError as e:
            print(f"Failed to fetch APOD: {e}")
            return None
    
    async def fetch_all_exoplanets(
        self,
        tess_count: int = 100,
        kepler_count: int = 100
    ) -> Dict[str, List[Dict]]:
        """
        Fetch all exoplanet data (TESS + Kepler).
        
        Args:
            tess_count: Number of TESS planets
            kepler_count: Number of Kepler planets
            
        Returns:
            Dictionary with 'tess' and 'kepler' keys
        """
        tess_data, kepler_data = await asyncio.gather(
            self.fetch_tess_exoplanets(tess_count),
            self.fetch_kepler_light_curves(count=kepler_count)
        )
        
        return {
            'tess': tess_data,
            'kepler': kepler_data
        }
    
    def save_to_json(self, data: Any, filepath: str) -> bool:
        """
        Save data to JSON file.
        
        Args:
            data: Data to save
            filepath: Output file path
            
        Returns:
            True if successful
        """
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"Failed to save JSON: {e}")
            return False
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear()
        # Clear file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception:
                pass


# Convenience function for quick usage
async def get_nasa_service() -> NASAApiService:
    """Get NASA API service instance."""
    return NASAApiService()
