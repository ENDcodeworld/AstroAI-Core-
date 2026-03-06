#!/usr/bin/env python3
"""
NASA Data Fetcher for AstroAI-Core Project

This script provides automated data fetching from various NASA APIs:
- NASA Exoplanet Archive (TESS & Kepler data)
- NASA Image and Video Library (Hubble images)
- NASA Planetary Data System

Features:
- Error handling with exponential backoff
- Retry mechanism for failed requests
- JSON output formatting
- Rate limiting compliance

Author: AstroAI-Core Team
Date: 2026-03-06
"""

import json
import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class NASAAPIFetcher:
    """NASA API data fetcher with error handling and retry logic."""
    
    def __init__(self, api_key: str, max_retries: int = 3, base_delay: float = 1.0):
        """
        Initialize the fetcher.
        
        Args:
            api_key: NASA API key
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries (seconds)
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AstroAI-Core/1.0',
            'Accept': 'application/json'
        })
    
    def _request_with_retry(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make HTTP request with exponential backoff retry.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            JSON response as dict or None if all retries failed
        """
        if params is None:
            params = {}
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                delay = self.base_delay * (2 ** attempt)
                print(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                print(f"Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
        
        print(f"All {self.max_retries} retry attempts failed for {url}")
        return None
    
    def fetch_apod(self, date: Optional[str] = None) -> Optional[Dict]:
        """
        Fetch Astronomy Picture of the Day.
        
        Args:
            date: Date in YYYY-MM-DD format (default: today)
            
        Returns:
            APOD data or None
        """
        url = "https://api.nasa.gov/planetary/apod"
        params = {'api_key': self.api_key}
        if date:
            params['date'] = date
        
        return self._request_with_retry(url, params)
    
    def fetch_exoplanets(self, count: int = 20) -> List[Dict]:
        """
        Fetch exoplanet data from NASA Exoplanet Archive.
        
        Args:
            count: Number of planets to fetch
            
        Returns:
            List of exoplanet records
        """
        url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
        query = f"""
            SELECT TOP {count}
                pl_name, hostname, discoverymethod,
                pl_orbper, pl_radj, pl_massj, pl_eqt, sy_dist
            FROM ps
        """
        params = {
            'query': query,
            'format': 'json'
        }
        
        result = self._request_with_retry(url, params)
        if result and isinstance(result, list):
            return result
        return []
    
    def fetch_kepler_planets(self, count: int = 15) -> List[Dict]:
        """
        Fetch Kepler exoplanet data specifically.
        
        Args:
            count: Number of planets to fetch
            
        Returns:
            List of Kepler planet records
        """
        url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
        query = f"""
            SELECT TOP {count}
                pl_name, hostname, pl_orbper, pl_radj,
                pl_massj, pl_eqt, discoverymethod
            FROM ps
            WHERE hostname LIKE 'Kepler%'
        """
        params = {
            'query': query,
            'format': 'json'
        }
        
        result = self._request_with_retry(url, params)
        if result and isinstance(result, list):
            return result
        return []
    
    def fetch_hubble_images(self, query: str = "hubble deep space", count: int = 10) -> List[Dict]:
        """
        Fetch Hubble images from NASA Image and Video Library.
        
        Args:
            query: Search query
            count: Number of images to fetch
            
        Returns:
            List of image metadata
        """
        url = "https://images-api.nasa.gov/search"
        params = {
            'q': query,
            'media_type': 'image'
        }
        
        result = self._request_with_retry(url, params)
        if not result or 'collection' not in result:
            return []
        
        images = []
        items = result['collection']['items'][:count]
        
        for item in items:
            image_data = {
                'nasa_id': item['data'][0]['nasa_id'],
                'title': item['data'][0]['title'],
                'description': item['data'][0]['description'][:500] if len(item['data'][0]['description']) > 500 else item['data'][0]['description'],
                'date_created': item['data'][0].get('date_created', 'Unknown'),
                'center': item['data'][0].get('center', 'Unknown'),
                'keywords': item['data'][0].get('keywords', []),
                'media_type': item['data'][0]['media_type'],
                'image_url': None,
                'thumbnail_url': None
            }
            
            for link in item['links']:
                if link['rel'] == 'canonical':
                    image_data['image_url'] = link['href']
                elif link['rel'] == 'preview':
                    image_data['thumbnail_url'] = link['href']
            
            images.append(image_data)
        
        return images
    
    def fetch_mars_weather(self) -> Optional[Dict]:
        """
        Fetch Mars weather data from InSight lander.
        
        Returns:
            Mars weather data or None
        """
        url = "https://api.nasa.gov/insight_weather/"
        params = {
            'api_key': self.api_key,
            'feedtype': 'json',
            'ver': '1.0'
        }
        
        return self._request_with_retry(url, params)
    
    def fetch_asteroid_neows(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch near-Earth asteroid data from NEOws.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of asteroid records
        """
        url = "https://api.nasa.gov/neo/rest/v1/feed"
        params = {
            'api_key': self.api_key,
            'start_date': start_date,
            'end_date': end_date
        }
        
        result = self._request_with_retry(url, params)
        if result and 'near_earth_objects' in result:
            asteroids = []
            for date, objects in result['near_earth_objects'].items():
                asteroids.extend(objects)
            return asteroids
        return []
    
    def save_json(self, data: Any, filepath: str) -> bool:
        """
        Save data to JSON file.
        
        Args:
            data: Data to save
            filepath: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {filepath}")
            return True
        except Exception as e:
            print(f"✗ Failed to save {filepath}: {e}")
            return False


def main():
    """Main function to demonstrate data fetching."""
    # API Key (should be loaded from environment in production)
    API_KEY = "RKKPoomDvkCh0COjlDbWZ1deUAwuA68wzvYFhvoo"
    
    # Initialize fetcher
    fetcher = NASAAPIFetcher(api_key=API_KEY)
    
    print("=" * 60)
    print("NASA Data Fetcher - AstroAI-Core")
    print("=" * 60)
    print()
    
    # Test APOD
    print("1. Fetching Astronomy Picture of the Day...")
    apod = fetcher.fetch_apod()
    if apod:
        print(f"   Title: {apod.get('title', 'N/A')}")
        print(f"   Date: {apod.get('date', 'N/A')}")
    print()
    
    # Test Exoplanet data
    print("2. Fetching Exoplanet data...")
    exoplanets = fetcher.fetch_exoplanets(count=20)
    print(f"   Retrieved {len(exoplanets)} exoplanets")
    if exoplanets:
        fetcher.save_json(exoplanets, 'data/samples/exoplanets_sample.json')
    print()
    
    # Test Kepler data
    print("3. Fetching Kepler planet data...")
    kepler = fetcher.fetch_kepler_planets(count=15)
    print(f"   Retrieved {len(kepler)} Kepler planets")
    if kepler:
        fetcher.save_json(kepler, 'data/samples/kepler_sample.json')
    print()
    
    # Test Hubble images
    print("4. Fetching Hubble images...")
    hubble = fetcher.fetch_hubble_images(query="hubble deep space", count=10)
    print(f"   Retrieved {len(hubble)} Hubble images")
    if hubble:
        fetcher.save_json(hubble, 'data/samples/hubble_images.json')
    print()
    
    print("=" * 60)
    print("Data fetching complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
