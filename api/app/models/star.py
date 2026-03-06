"""
Star database model for AstroAI-Core

Stores stellar data from various astronomical surveys
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Star(Base):
    """
    Star model representing stellar objects.
    
    Data sources:
    - NASA Exoplanet Archive
    - ESA Gaia Mission
    - SIMBAD Astronomical Database
    """
    
    __tablename__ = 'stars'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identification
    name = Column(String(100), nullable=False, index=True, unique=True, comment="Star name (e.g., 'Kepler-452')")
    alternative_names = Column(Text, nullable=True, comment="Alternative designations (comma-separated)")
    
    # Classification
    spectral_type = Column(String(20), nullable=True, comment="Spectral classification (e.g., 'G2V')")
    constellation = Column(String(50), nullable=True, comment="Constellation name")
    
    # Physical characteristics
    mass_solar = Column(Float, nullable=True, comment="Mass in solar masses")
    radius_solar = Column(Float, nullable=True, comment="Radius in solar radii")
    temperature = Column(Float, nullable=True, comment="Effective temperature in Kelvin")
    luminosity_solar = Column(Float, nullable=True, comment="Luminosity in solar luminosities")
    metallicity = Column(Float, nullable=True, comment="Metallicity [Fe/H]")
    age_gyr = Column(Float, nullable=True, comment="Age in billions of years")
    
    # Position and distance
    distance_ly = Column(Float, nullable=True, comment="Distance in light years")
    right_ascension = Column(String(50), nullable=True, comment="Right ascension (J2000)")
    declination = Column(String(50), nullable=True, comment="Declination (J2000)")
    proper_motion_ra = Column(Float, nullable=True, comment="Proper motion in RA (mas/yr)")
    proper_motion_dec = Column(Float, nullable=True, comment="Proper motion in Dec (mas/yr)")
    
    # Photometry
    visual_magnitude = Column(Float, nullable=True, comment="Apparent visual magnitude (V)")
    absolute_magnitude = Column(Float, nullable=True, comment="Absolute magnitude (Mv)")
    b_v_color = Column(Float, nullable=True, comment="B-V color index")
    
    # Planetary system
    has_planets = Column(Integer, default=0, comment="Number of known planets")
    planet_names = Column(Text, nullable=True, comment="Names of known planets (comma-separated)")
    
    # Data quality
    quality_score = Column(String(20), nullable=True, default='good', comment="Data quality assessment")
    
    # Metadata
    data_source = Column(String(50), nullable=True, comment="Source of data")
    raw_data = Column(JSON, nullable=True, comment="Original JSON data from API")
    created_at = Column(DateTime(timezone=True), default=func.now(), comment="Record creation time")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), comment="Last update time")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_stars_spectral_type', 'spectral_type'),
        Index('idx_stars_constellation', 'constellation'),
        Index('idx_stars_distance', 'distance_ly'),
        Index('idx_stars_magnitude', 'visual_magnitude'),
        Index('idx_stars_has_planets', 'has_planets'),
        Index('idx_stars_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Star(name='{self.name}', spectral_type='{self.spectral_type}')>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'alternative_names': self.alternative_names,
            'spectral_type': self.spectral_type,
            'constellation': self.constellation,
            'mass_solar': self.mass_solar,
            'radius_solar': self.radius_solar,
            'temperature': self.temperature,
            'luminosity_solar': self.luminosity_solar,
            'metallicity': self.metallicity,
            'age_gyr': self.age_gyr,
            'distance_ly': self.distance_ly,
            'right_ascension': self.right_ascension,
            'declination': self.declination,
            'visual_magnitude': self.visual_magnitude,
            'absolute_magnitude': self.absolute_magnitude,
            'b_v_color': self.b_v_color,
            'has_planets': self.has_planets,
            'planet_names': self.planet_names,
            'quality_score': self.quality_score,
            'data_source': self.data_source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_nasa_data(cls, data: dict) -> 'Star':
        """
        Create Star instance from NASA API data.
        
        Args:
            data: Dictionary from NASA Exoplanet Archive
            
        Returns:
            Star instance
        """
        return cls(
            name=data.get('hostname', ''),
            spectral_type=data.get('spectral_type', ''),
            distance_ly=cls._safe_float(data.get('sy_dist')),
            visual_magnitude=cls._safe_float(data.get('sy_vmag')),
            mass_solar=cls._safe_float(data.get('st_mass')),
            radius_solar=cls._safe_float(data.get('st_rad')),
            temperature=cls._safe_float(data.get('st_teff')),
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
