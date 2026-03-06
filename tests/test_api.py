"""
Unit tests for API Endpoints

Tests exoplanet and image API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typing import AsyncGenerator
import sys
from pathlib import Path

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'api'))

from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.models.exoplanet import Exoplanet
from app.models.image import Image


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        # Import models to create tables
        from app.models import exoplanet, image  # noqa
        
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session_maker(test_engine):
    """Create test session maker."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    return async_session_maker


@pytest.fixture
async def db_session(test_session_maker) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with test_session_maker() as session:
        yield session


@pytest.fixture
def client(db_session):
    """Create test client with overridden database dependency."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestExoplanetEndpoints:
    """Test exoplanet API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_exoplanets_empty(self, client, db_session):
        """Test getting exoplanets when database is empty."""
        response = client.get("/api/v1/exoplanets")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"] == []
        assert data["total"] == 0
    
    @pytest.mark.asyncio
    async def test_get_exoplanets_with_data(self, client, db_session):
        """Test getting exoplanets with data in database."""
        # Add test data
        planet = Exoplanet(
            name="Test Planet b",
            hostname="Test Star",
            discovery_method="Transit",
            orbital_period=10.5,
            radius_jupiter=1.2,
            mass_jupiter=0.8,
            distance_ly=100.0,
            data_source="TESS"
        )
        db_session.add(planet)
        await db_session.commit()
        
        response = client.get("/api/v1/exoplanets")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Test Planet b"
    
    @pytest.mark.asyncio
    async def test_get_exoplanets_pagination(self, client, db_session):
        """Test exoplanet pagination."""
        # Add multiple planets
        for i in range(5):
            planet = Exoplanet(
                name=f"Planet {i} b",
                hostname=f"Star {i}",
                orbital_period=10.0 + i
            )
            db_session.add(planet)
        await db_session.commit()
        
        # Test skip and limit
        response = client.get("/api/v1/exoplanets?skip=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["skip"] == 2
        assert data["limit"] == 2
    
    @pytest.mark.asyncio
    async def test_get_exoplanet_by_id(self, client, db_session):
        """Test getting exoplanet by ID."""
        planet = Exoplanet(
            name="Kepler-452 b",
            hostname="Kepler-452",
            orbital_period=384.8
        )
        db_session.add(planet)
        await db_session.commit()
        
        response = client.get(f"/api/v1/exoplanets/{planet.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Kepler-452 b"
        assert data["orbital_period"] == 384.8
    
    @pytest.mark.asyncio
    async def test_get_exoplanet_not_found(self, client):
        """Test getting non-existent exoplanet."""
        response = client.get("/api/v1/exoplanets/99999")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_exoplanet_by_name(self, client, db_session):
        """Test getting exoplanet by name."""
        planet = Exoplanet(
            name="Kepler-452 b",
            hostname="Kepler-452"
        )
        db_session.add(planet)
        await db_session.commit()
        
        response = client.get("/api/v1/exoplanets/name/Kepler-452 b")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Kepler-452 b"
    
    @pytest.mark.asyncio
    async def test_get_exoplanet_by_name_not_found(self, client):
        """Test getting non-existent exoplanet by name."""
        response = client.get("/api/v1/exoplanets/name/NonExistent Planet")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_exoplanets_filter_by_discovery_method(self, client, db_session):
        """Test filtering exoplanets by discovery method."""
        planet1 = Exoplanet(name="Planet 1", discovery_method="Transit")
        planet2 = Exoplanet(name="Planet 2", discovery_method="Radial Velocity")
        db_session.add_all([planet1, planet2])
        await db_session.commit()
        
        response = client.get("/api/v1/exoplanets?discovery_method=Transit")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["discovery_method"] == "Transit"
    
    @pytest.mark.asyncio
    async def test_get_exoplanets_filter_by_data_source(self, client, db_session):
        """Test filtering exoplanets by data source."""
        planet1 = Exoplanet(name="TESS Planet", data_source="TESS")
        planet2 = Exoplanet(name="Kepler Planet", data_source="Kepler")
        db_session.add_all([planet1, planet2])
        await db_session.commit()
        
        response = client.get("/api/v1/exoplanets?data_source=TESS")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["data_source"] == "TESS"
    
    @pytest.mark.asyncio
    async def test_get_exoplanets_filter_by_distance(self, client, db_session):
        """Test filtering exoplanets by distance."""
        planet1 = Exoplanet(name="Near Planet", distance_ly=50.0)
        planet2 = Exoplanet(name="Far Planet", distance_ly=500.0)
        db_session.add_all([planet1, planet2])
        await db_session.commit()
        
        response = client.get("/api/v1/exoplanets?max_distance=100")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Near Planet"
    
    @pytest.mark.asyncio
    async def test_get_exoplanet_stats(self, client, db_session):
        """Test getting exoplanet statistics."""
        planet1 = Exoplanet(name="Planet 1", discovery_method="Transit", data_source="TESS", distance_ly=100.0, mass_jupiter=1.0, radius_jupiter=1.0)
        planet2 = Exoplanet(name="Planet 2", discovery_method="Transit", data_source="Kepler", distance_ly=200.0)
        db_session.add_all([planet1, planet2])
        await db_session.commit()
        
        response = client.get("/api/v1/exoplanets/stats/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert "by_discovery_method" in data
        assert "by_data_source" in data
    
    @pytest.mark.asyncio
    async def test_get_habitable_exoplanets(self, client, db_session):
        """Test getting potentially habitable exoplanets."""
        # Add planet in habitable zone (200K-350K equilibrium temp)
        habitable = Exoplanet(
            name="Habitable Planet",
            equilibrium_temp=280.0,
            radius_jupiter=1.0
        )
        # Add planet outside habitable zone
        hot = Exoplanet(
            name="Hot Planet",
            equilibrium_temp=1000.0,
            radius_jupiter=1.0
        )
        db_session.add_all([habitable, hot])
        await db_session.commit()
        
        response = client.get("/api/v1/exoplanets/habitable")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Habitable Planet"


class TestImageEndpoints:
    """Test image API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_images_empty(self, client, db_session):
        """Test getting images when database is empty."""
        response = client.get("/api/v1/images")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"] == []
    
    @pytest.mark.asyncio
    async def test_get_images_with_data(self, client, db_session):
        """Test getting images with data in database."""
        image = Image(
            nasa_id="hst_001",
            title="Deep Space Image",
            description="A beautiful image",
            mission="Hubble",
            center="STScI"
        )
        db_session.add(image)
        await db_session.commit()
        
        response = client.get("/api/v1/images")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["nasa_id"] == "hst_001"
    
    @pytest.mark.asyncio
    async def test_get_image_by_id(self, client, db_session):
        """Test getting image by ID."""
        image = Image(
            nasa_id="hst_001",
            title="Test Image"
        )
        db_session.add(image)
        await db_session.commit()
        
        response = client.get(f"/api/v1/images/{image.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["nasa_id"] == "hst_001"
    
    @pytest.mark.asyncio
    async def test_get_image_not_found(self, client):
        """Test getting non-existent image."""
        response = client.get("/api/v1/images/99999")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_image_by_nasa_id(self, client, db_session):
        """Test getting image by NASA ID."""
        image = Image(
            nasa_id="jwst_001",
            title="JWST Image"
        )
        db_session.add(image)
        await db_session.commit()
        
        response = client.get("/api/v1/images/nasa/jwst_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["nasa_id"] == "jwst_001"
    
    @pytest.mark.asyncio
    async def test_get_images_filter_by_mission(self, client, db_session):
        """Test filtering images by mission."""
        image1 = Image(nasa_id="hst_001", title="Hubble Image", mission="Hubble")
        image2 = Image(nasa_id="jwst_001", title="JWST Image", mission="JWST")
        db_session.add_all([image1, image2])
        await db_session.commit()
        
        response = client.get("/api/v1/images?mission=Hubble")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["mission"] == "Hubble"
    
    @pytest.mark.asyncio
    async def test_get_images_filter_by_target_type(self, client, db_session):
        """Test filtering images by target type."""
        image1 = Image(nasa_id="img1", title="Galaxy", target_type="Galaxy")
        image2 = Image(nasa_id="img2", title="Nebula", target_type="Nebula")
        db_session.add_all([image1, image2])
        await db_session.commit()
        
        response = client.get("/api/v1/images?target_type=Galaxy")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    @pytest.mark.asyncio
    async def test_get_images_pagination(self, client, db_session):
        """Test image pagination."""
        for i in range(5):
            image = Image(nasa_id=f"img_{i}", title=f"Image {i}")
            db_session.add(image)
        await db_session.commit()
        
        response = client.get("/api/v1/images?skip=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["skip"] == 2
    
    @pytest.mark.asyncio
    async def test_analyze_image_upload(self, client):
        """Test image analysis upload endpoint."""
        # Create a mock file
        import io
        file_content = io.BytesIO(b"fake image data")
        
        response = client.post(
            "/api/v1/analyze/image",
            files={"file": ("test.jpg", file_content, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysis" in data
    
    @pytest.mark.asyncio
    async def test_analyze_image_invalid_type(self, client):
        """Test image analysis with invalid file type."""
        import io
        file_content = io.BytesIO(b"fake text data")
        
        response = client.post(
            "/api/v1/analyze/image",
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_image_stats(self, client, db_session):
        """Test getting image statistics."""
        image1 = Image(nasa_id="img1", title="Image 1", mission="Hubble", target_type="Galaxy", center="STScI")
        image2 = Image(nasa_id="img2", title="Image 2", mission="JWST", target_type="Nebula", center="GSFC")
        db_session.add_all([image1, image2])
        await db_session.commit()
        
        response = client.get("/api/v1/images/stats/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert "by_mission" in data
        assert "by_target_type" in data
    
    @pytest.mark.asyncio
    async def test_get_images_by_mission(self, client, db_session):
        """Test getting images by mission."""
        image1 = Image(nasa_id="hst_1", title="Hubble 1", mission="Hubble")
        image2 = Image(nasa_id="hst_2", title="Hubble 2", mission="Hubble")
        image3 = Image(nasa_id="jwst_1", title="JWST 1", mission="JWST")
        db_session.add_all([image1, image2, image3])
        await db_session.commit()
        
        response = client.get("/api/v1/images/mission/Hubble")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["mission"] == "Hubble"


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AstroAI-Core API"
        assert data["status"] == "running"
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
