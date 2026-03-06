"""
Exoplanet database model for AstroAI-Core

Stores exoplanet data from NASA Exoplanet Archive (TESS, Kepler, etc.)
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Exoplanet(Base):
    """
    Exoplanet model representing discovered planets outside our solar system.
    
    Data sources:
    - TESS (Transiting Exoplanet Survey Satellite)
    - Kepler Space Telescope
    - Other discovery missions
    """
    
    __tablename__ = 'exoplanets'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identification
    name = Column(String(100), nullable=False, index=True, comment="Planet name (e.g., 'Kepler-452 b')")
    hostname = Column(String(100), nullable=True, index=True, comment="Host star name")
    
    # Discovery information
    discovery_method = Column(String(50), nullable=True, comment="Discovery method (Transit, Radial Velocity, etc.)")
    discovery_year = Column(Integer, nullable=True, comment="Year of discovery")
    
    # Physical characteristics
    orbital_period = Column(Float, nullable=True, comment="Orbital period in days")
    radius_jupiter = Column(Float, nullable=True, comment="Planet radius in Jupiter radii")
    mass_jupiter = Column(Float, nullable=True, comment="Planet mass in Jupiter masses")
    equilibrium_temp = Column(Float, nullable=True, comment="Equilibrium temperature in Kelvin")
    
    # Host star information
    distance_ly = Column(Float, nullable=True, comment="Distance to system in light years")
    visual_magnitude = Column(Float, nullable=True, comment="Apparent visual magnitude of host star")
    
    # Data quality
    quality_score = Column(String(20), nullable=True, default='good', comment="Data quality assessment")
    
    # Metadata
    data_source = Column(String(50), nullable=True, comment="Source of data (TESS, Kepler, etc.)")
    raw_data = Column(JSON, nullable=True, comment="Original JSON data from API")
    fetched_at = Column(DateTime(timezone=True), default=func.now(), comment="When data was fetched")
    created_at = Column(DateTime(timezone=True), default=func.now(), comment="Record creation time")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), comment="Last update time")
    
    # Derived fields (for quick queries)
    is_habitable_zone = Column(Boolean, nullable=True, comment="Whether planet is in habitable zone")
    is_earth_like = Column(Boolean, nullable=True, comment="Whether planet is Earth-like")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_exoplanets_discovery_method', 'discovery_method'),
        Index('idx_exoplanets_distance', 'distance_ly'),
        Index('idx_exoplanets_orbital_period', 'orbital_period'),
        Index('idx_exoplanets_quality', 'quality_score'),
        Index('idx_exoplanets_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Exoplanet(name='{self.name}', hostname='{self.hostname}')>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'hostname': self.hostname,
            'discovery_method': self.discovery_method,
            'discovery_year': self.discovery_year,
            'orbital_period': self.orbital_period,
            'radius_jupiter': self.radius_jupiter,
            'mass_jupiter': self.mass_jupiter,
            'equilibrium_temp': self.equilibrium_temp,
            'distance_ly': self.distance_ly,
            'visual_magnitude': self.visual_magnitude,
            'quality_score': self.quality_score,
            'data_source': self.data_source,
            'is_habitable_zone': self.is_habitable_zone,
            'is_earth_like': self.is_earth_like,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_nasa_data(cls, data: dict) -> 'Exoplanet':
        """
        Create Exoplanet instance from NASA API data.
        
        Args:
            data: Dictionary from NASA Exoplanet Archive
            
        Returns:
            Exoplanet instance
        """
        return cls(
            name=data.get('pl_name', ''),
            hostname=data.get('hostname', ''),
            discovery_method=data.get('discoverymethod', ''),
            orbital_period=cls._safe_float(data.get('pl_orbper')),
            radius_jupiter=cls._safe_float(data.get('pl_radj')),
            mass_jupiter=cls._safe_float(data.get('pl_massj')),
            equilibrium_temp=cls._safe_float(data.get('pl_eqt')),
            distance_ly=cls._safe_float(data.get('sy_dist')),
            visual_magnitude=cls._safe_float(data.get('sy_vmag')),
            discovery_year=cls._extract_year(data.get('pl_disc')),
            data_source=data.get('data_source', 'NASA'),
            raw_data=data
        )
    
    @staticmethod
    def _safe_float(value) -> float:
        """Safely convert value to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _extract_year(disc_string) -> int:
        """Extract year from discovery date string."""
        if not disc_string:
            return None
        try:
            return int(str(disc_string)[:4])
        except (ValueError, TypeError):
            return None
