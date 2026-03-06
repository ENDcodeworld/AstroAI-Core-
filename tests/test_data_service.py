"""
Unit tests for NASA Data Service

Tests data fetching, caching, and processing functionality.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
import json
import sys
from pathlib import Path

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'api'))

from app.services.nasa_data_service import (
    NASAApiService,
    NASAAPIError,
    CacheEntry
)
from app.services.data_pipeline import (
    DataPipeline,
    DataQuality,
    ProcessingResult,
    run_pipeline
)


class TestCacheEntry:
    """Test cache entry functionality."""
    
    def test_cache_entry_creation(self):
        """Test creating a cache entry."""
        data = {"test": "value"}
        entry = CacheEntry(data, ttl_seconds=3600)
        
        assert entry.data == data
        assert entry.expires_at > datetime.now()
    
    def test_cache_entry_not_expired(self):
        """Test cache entry expiration check."""
        data = {"test": "value"}
        entry = CacheEntry(data, ttl_seconds=3600)
        
        assert not entry.is_expired()
    
    def test_cache_entry_expired(self):
        """Test expired cache entry."""
        data = {"test": "value"}
        entry = CacheEntry(data, ttl_seconds=-1)  # Already expired
        
        assert entry.is_expired()


class TestNASAApiService:
    """Test NASA API service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return NASAApiService(api_key="test_key")
    
    def test_init(self, service):
        """Test service initialization."""
        assert service.api_key == "test_key"
        assert service.cache_dir.exists()
    
    def test_generate_cache_key(self, service):
        """Test cache key generation."""
        params = {"key": "value", "count": 10}
        key1 = service._generate_cache_key("/test", params)
        key2 = service._generate_cache_key("/test", params)
        
        # Same params should generate same key
        assert key1 == key2
        
        # Different params should generate different key
        key3 = service._generate_cache_key("/test", {"key": "different"})
        assert key1 != key3
    
    def test_cache_operations(self, service):
        """Test cache save and retrieve."""
        key = "test_cache_key"
        data = {"test": "data"}
        
        # Save to cache
        service._save_to_cache(key, data, ttl=3600)
        
        # Retrieve from cache
        retrieved = service._get_from_cache(key)
        assert retrieved == data
    
    def test_cache_miss(self, service):
        """Test cache miss returns None."""
        result = service._get_from_cache("nonexistent_key")
        assert result is None
    
    def test_clear_cache(self, service):
        """Test clearing cache."""
        service._save_to_cache("key1", {"data": 1}, 3600)
        service._save_to_cache("key2", {"data": 2}, 3600)
        
        service.clear_cache()
        
        assert service._get_from_cache("key1") is None
        assert service._get_from_cache("key2") is None
    
    @pytest.mark.asyncio
    async def test_fetch_tess_exoplanets_mock(self, service):
        """Test TESS exoplanet fetching with mock."""
        mock_response = [
            {
                "pl_name": "TESS-1 b",
                "hostname": "TESS-1",
                "discoverymethod": "Transit",
                "pl_orbper": 3.5,
                "pl_radj": 1.2,
                "pl_massj": 0.8,
                "pl_eqt": 1200,
                "sy_dist": 100.5
            }
        ]
        
        with patch.object(service, '_request_with_retry', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await service.fetch_tess_exoplanets(count=1)
            
            assert len(result) == 1
            assert result[0]['pl_name'] == "TESS-1 b"
            assert result[0]['data_source'] == 'TESS'
            assert 'fetched_at' in result[0]
    
    @pytest.mark.asyncio
    async def test_fetch_kepler_light_curves_mock(self, service):
        """Test Kepler light curve fetching with mock."""
        mock_response = [
            {
                "pl_name": "Kepler-452 b",
                "hostname": "Kepler-452",
                "pl_orbper": 384.8,
                "pl_radj": 1.6,
                "pl_massj": 5.0,
                "koi_snr": 15.2
            }
        ]
        
        with patch.object(service, '_request_with_retry', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await service.fetch_kepler_light_curves(count=1)
            
            assert len(result) == 1
            assert result[0]['pl_name'] == "Kepler-452 b"
            assert result[0]['data_source'] == 'Kepler'
    
    @pytest.mark.asyncio
    async def test_fetch_hubble_images_mock(self, service):
        """Test Hubble image fetching with mock."""
        mock_response = {
            "collection": {
                "items": [
                    {
                        "data": [{
                            "nasa_id": "hst_001",
                            "title": "Deep Space Image",
                            "description": "A beautiful deep space image",
                            "date_created": "2024-01-01",
                            "center": "STScI",
                            "media_type": "image"
                        }],
                        "links": [
                            {"rel": "canonical", "href": "https://example.com/image.jpg"},
                            {"rel": "preview", "href": "https://example.com/thumb.jpg"}
                        ]
                    }
                ]
            }
        }
        
        with patch.object(service, '_request_with_retry', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await service.fetch_hubble_images(query="deep space", count=1)
            
            assert len(result) == 1
            assert result[0]['nasa_id'] == "hst_001"
            assert result[0]['image_url'] == "https://example.com/image.jpg"
            assert result[0]['thumbnail_url'] == "https://example.com/thumb.jpg"
    
    @pytest.mark.asyncio
    async def test_fetch_apod_mock(self, service):
        """Test APOD fetching with mock."""
        mock_response = {
            "title": "Cosmic Cliffs",
            "date": "2024-01-15",
            "url": "https://example.com/apod.jpg",
            "explanation": "Beautiful cosmic cliffs"
        }
        
        with patch.object(service, '_request_with_retry', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await service.fetch_apod()
            
            assert result['title'] == "Cosmic Cliffs"
            assert result['date'] == "2024-01-15"
    
    @pytest.mark.asyncio
    async def test_fetch_all_exoplanets(self, service):
        """Test fetching all exoplanet data."""
        tess_data = [{"pl_name": "TESS-1 b"}]
        kepler_data = [{"pl_name": "Kepler-452 b"}]
        
        with patch.object(service, 'fetch_tess_exoplanets', new_callable=AsyncMock) as mock_tess, \
             patch.object(service, 'fetch_kepler_light_curves', new_callable=AsyncMock) as mock_kepler:
            
            mock_tess.return_value = tess_data
            mock_kepler.return_value = kepler_data
            
            result = await service.fetch_all_exoplanets()
            
            assert 'tess' in result
            assert 'kepler' in result
            assert len(result['tess']) == 1
            assert len(result['kepler']) == 1
    
    def test_save_to_json(self, service, tmp_path):
        """Test saving data to JSON file."""
        data = {"test": "data", "number": 42}
        filepath = tmp_path / "test.json"
        
        result = service.save_to_json(data, str(filepath))
        
        assert result is True
        assert filepath.exists()
        
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        
        assert loaded == data
    
    @pytest.mark.asyncio
    async def test_request_failure_raises_error(self, service):
        """Test that request failures raise NASAAPIError."""
        with patch.object(service, '_request_with_retry', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = NASAAPIError("All retries failed")
            
            with pytest.raises(NASAAPIError):
                await service.fetch_tess_exoplanets()


class TestDataPipeline:
    """Test data pipeline functionality."""
    
    @pytest.fixture
    def pipeline(self):
        """Create pipeline instance."""
        return DataPipeline()
    
    def test_clean_string(self, pipeline):
        """Test string cleaning."""
        assert pipeline._clean_string("  test  ") == "test"
        assert pipeline._clean_string(None) == ""
        assert len(pipeline._clean_string("a" * 300, max_length=100)) == 100
    
    def test_clean_numeric(self, pipeline):
        """Test numeric cleaning."""
        assert pipeline._clean_numeric(42.5) == 42.5
        assert pipeline._clean_numeric("42.5") == 42.5
        assert pipeline._clean_numeric(None) == 0.0
        assert pipeline._clean_numeric("invalid") == 0.0
    
    def test_clean_boolean(self, pipeline):
        """Test boolean cleaning."""
        assert pipeline._clean_boolean(True) is True
        assert pipeline._clean_boolean("true") is True
        assert pipeline._clean_boolean("1") is True
        assert pipeline._clean_boolean(False) is False
        assert pipeline._clean_boolean(None) is False
    
    def test_validate_exoplanet_valid(self, pipeline):
        """Test validating valid exoplanet data."""
        planet = {
            "pl_name": "Kepler-452 b",
            "hostname": "Kepler-452",
            "pl_orbper": 384.8,
            "pl_radj": 1.6,
            "pl_massj": 5.0,
            "sy_dist": 1400
        }
        
        is_valid, quality = pipeline._validate_exoplanet_data(planet)
        
        assert is_valid is True
        assert quality == DataQuality.EXCELLENT
    
    def test_validate_exoplanet_missing_name(self, pipeline):
        """Test validating exoplanet with missing name."""
        planet = {
            "hostname": "Kepler-452",
            "pl_radj": 1.6
        }
        
        is_valid, quality = pipeline._validate_exoplanet_data(planet)
        
        assert is_valid is False
        assert quality == DataQuality.INVALID
    
    def test_validate_exoplanet_partial_data(self, pipeline):
        """Test validating exoplanet with partial data."""
        planet = {
            "pl_name": "TESS-1 b",
            "hostname": "TESS-1",
            "pl_radj": 1.2
            # Missing mass and period
        }
        
        is_valid, quality = pipeline._validate_exoplanet_data(planet)
        
        assert is_valid is True
        assert quality in [DataQuality.FAIR, DataQuality.POOR]
    
    def test_validate_star_valid(self, pipeline):
        """Test validating valid star data."""
        star = {
            "hostname": "Kepler-452",
            "sy_dist": 1400,
            "sy_vmag": 13.4
        }
        
        is_valid, quality = pipeline._validate_star_data(star)
        
        assert is_valid is True
        assert quality == DataQuality.EXCELLENT
    
    def test_validate_star_missing_name(self, pipeline):
        """Test validating star with missing name."""
        star = {
            "sy_dist": 1400
        }
        
        is_valid, quality = pipeline._validate_star_data(star)
        
        assert is_valid is False
        assert quality == DataQuality.INVALID
    
    def test_validate_image_valid(self, pipeline):
        """Test validating valid image data."""
        image = {
            "nasa_id": "hst_001",
            "title": "Deep Space",
            "image_url": "https://example.com/image.jpg"
        }
        
        is_valid, quality = pipeline._validate_image_data(image)
        
        assert is_valid is True
        assert quality == DataQuality.EXCELLENT
    
    def test_validate_image_missing_id(self, pipeline):
        """Test validating image with missing NASA ID."""
        image = {
            "title": "Deep Space"
        }
        
        is_valid, quality = pipeline._validate_image_data(image)
        
        assert is_valid is False
        assert quality == DataQuality.INVALID
    
    def test_extract_year(self, pipeline):
        """Test year extraction from discovery date."""
        assert pipeline._extract_year("2015") == 2015
        assert pipeline._extract_year("2015-07-23") == 2015
        assert pipeline._extract_year(None) is None
        assert pipeline._extract_year("invalid") is None
    
    def test_parse_date_iso(self, pipeline):
        """Test parsing ISO format date."""
        result = pipeline._parse_date("2024-01-15T10:30:00Z")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
    
    def test_parse_date_simple(self, pipeline):
        """Test parsing simple date format."""
        result = pipeline._parse_date("2024-01-15")
        assert result is not None
        assert result.year == 2024
    
    def test_parse_date_invalid(self, pipeline):
        """Test parsing invalid date."""
        result = pipeline._parse_date("invalid")
        assert result is None
    
    def test_parse_date_none(self, pipeline):
        """Test parsing None date."""
        result = pipeline._parse_date(None)
        assert result is None


class TestRunPipeline:
    """Test complete pipeline execution."""
    
    @pytest.mark.asyncio
    async def test_run_pipeline_empty(self):
        """Test running pipeline with no data."""
        results = await run_pipeline()
        assert results == {}
    
    @pytest.mark.asyncio
    async def test_run_pipeline_with_exoplanets(self):
        """Test running pipeline with exoplanet data."""
        exoplanets = [
            {
                "pl_name": "Test Planet",
                "hostname": "Test Star",
                "pl_orbper": 10.5,
                "pl_radj": 1.2,
                "pl_massj": 0.8
            }
        ]
        
        # Mock database operations
        with patch('app.services.data_pipeline.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.scalar_one_or_none = AsyncMock(return_value=None)
            
            results = await run_pipeline(exoplanets=exoplanets)
            
            assert 'exoplanets' in results
            assert results['exoplanets'].records_processed == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
