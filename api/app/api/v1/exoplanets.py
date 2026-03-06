"""
Exoplanet API Endpoints for AstroAI-Core

RESTful API for exoplanet data access and management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.models.exoplanet import Exoplanet

router = APIRouter()


@router.get("", response_model=List[dict], summary="Get exoplanet list")
async def get_exoplanets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search in planet name or hostname"),
    discovery_method: Optional[str] = Query(None, description="Filter by discovery method"),
    data_source: Optional[str] = Query(None, description="Filter by data source (TESS, Kepler, etc.)"),
    min_distance: Optional[float] = Query(None, ge=0, description="Minimum distance in light years"),
    max_distance: Optional[float] = Query(None, ge=0, description="Maximum distance in light years"),
    has_mass: Optional[bool] = Query(None, description="Filter planets with mass data"),
    has_radius: Optional[bool] = Query(None, description="Filter planets with radius data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a list of exoplanets with optional filtering.
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return (max 100)
    - **search**: Search term for planet name or hostname
    - **discovery_method**: Filter by discovery method (e.g., 'Transit')
    - **data_source**: Filter by data source (e.g., 'TESS', 'Kepler')
    - **min_distance**: Minimum distance from Earth in light years
    - **max_distance**: Maximum distance from Earth in light years
    - **has_mass**: Only return planets with mass measurements
    - **has_radius**: Only return planets with radius measurements
    
    Returns a list of exoplanet records with basic information.
    """
    try:
        # Build query
        query = select(Exoplanet)
        
        # Apply filters
        filters = []
        
        if search:
            search_filter = and_(
                Exoplanet.name.ilike(f"%{search}%"),
                Exoplanet.hostname.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if discovery_method:
            filters.append(Exoplanet.discovery_method.ilike(f"%{discovery_method}%"))
        
        if data_source:
            filters.append(Exoplanet.data_source == data_source)
        
        if min_distance is not None:
            filters.append(Exoplanet.distance_ly >= min_distance)
        
        if max_distance is not None:
            filters.append(Exoplanet.distance_ly <= max_distance)
        
        if has_mass:
            filters.append(Exoplanet.mass_jupiter.isnot(None))
        
        if has_radius:
            filters.append(Exoplanet.radius_jupiter.isnot(None))
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        exoplanets = result.scalars().all()
        
        # Get total count
        count_query = select(func.count(Exoplanet.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return {
            "items": [planet.to_dict() for planet in exoplanets],
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch exoplanets: {str(e)}"
        )


@router.get("/{exoplanet_id}", response_model=dict, summary="Get exoplanet by ID")
async def get_exoplanet(
    exoplanet_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific exoplanet.
    
    - **exoplanet_id**: Database ID of the exoplanet
    
    Returns complete exoplanet record including all measurements and metadata.
    """
    try:
        result = await db.execute(
            select(Exoplanet).where(Exoplanet.id == exoplanet_id)
        )
        exoplanet = result.scalar_one_or_none()
        
        if not exoplanet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exoplanet with ID {exoplanet_id} not found"
            )
        
        return exoplanet.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch exoplanet: {str(e)}"
        )


@router.get("/name/{planet_name}", response_model=dict, summary="Get exoplanet by name")
async def get_exoplanet_by_name(
    planet_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get exoplanet by its name.
    
    - **planet_name**: Name of the exoplanet (e.g., 'Kepler-452 b')
    
    Returns the exoplanet record if found.
    """
    try:
        result = await db.execute(
            select(Exoplanet).where(Exoplanet.name == planet_name)
        )
        exoplanet = result.scalar_one_or_none()
        
        if not exoplanet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exoplanet '{planet_name}' not found"
            )
        
        return exoplanet.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch exoplanet: {str(e)}"
        )


@router.get("/stats/summary", response_model=dict, summary="Get exoplanet statistics")
async def get_exoplanet_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary statistics about exoplanets in the database.
    
    Returns counts by discovery method, data source, and other metrics.
    """
    try:
        # Total count
        total_result = await db.execute(select(func.count(Exoplanet.id)))
        total = total_result.scalar()
        
        # Count by discovery method
        method_result = await db.execute(
            select(Exoplanet.discovery_method, func.count(Exoplanet.id))
            .group_by(Exoplanet.discovery_method)
        )
        by_method = {row[0] or 'Unknown': row[1] for row in method_result.all()}
        
        # Count by data source
        source_result = await db.execute(
            select(Exoplanet.data_source, func.count(Exoplanet.id))
            .group_by(Exoplanet.data_source)
        )
        by_source = {row[0] or 'Unknown': row[1] for row in source_result.all()}
        
        # Average distance
        avg_distance_result = await db.execute(
            select(func.avg(Exoplanet.distance_ly)).where(Exoplanet.distance_ly.isnot(None))
        )
        avg_distance = avg_distance_result.scalar()
        
        # Planets with mass data
        mass_result = await db.execute(
            select(func.count(Exoplanet.id)).where(Exoplanet.mass_jupiter.isnot(None))
        )
        with_mass = mass_result.scalar()
        
        # Planets with radius data
        radius_result = await db.execute(
            select(func.count(Exoplanet.id)).where(Exoplanet.radius_jupiter.isnot(None))
        )
        with_radius = radius_result.scalar()
        
        return {
            "total": total,
            "by_discovery_method": by_method,
            "by_data_source": by_source,
            "average_distance_ly": round(avg_distance, 2) if avg_distance else None,
            "planets_with_mass": with_mass,
            "planets_with_radius": with_radius,
            "completeness": {
                "mass": round(with_mass / total * 100, 1) if total > 0 else 0,
                "radius": round(with_radius / total * 100, 1) if total > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


@router.get("/habitable", response_model=List[dict], summary="Get potentially habitable exoplanets")
async def get_habitable_exoplanets(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get exoplanets that are potentially in the habitable zone.
    
    This is a simplified filter based on equilibrium temperature.
    True habitability assessment requires more complex analysis.
    
    - **limit**: Maximum number of records to return
    """
    try:
        # Simplified habitable zone: equilibrium temperature between 200K and 350K
        result = await db.execute(
            select(Exoplanet)
            .where(Exoplanet.equilibrium_temp >= 200)
            .where(Exoplanet.equilibrium_temp <= 350)
            .where(Exoplanet.radius_jupiter.isnot(None))
            .order_by(Exoplanet.distance_ly)
            .limit(limit)
        )
        exoplanets = result.scalars().all()
        
        return {
            "items": [planet.to_dict() for planet in exoplanets],
            "total": len(exoplanets),
            "note": "Habitability assessment is simplified. Actual habitability requires detailed atmospheric analysis."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch habitable exoplanets: {str(e)}"
        )
