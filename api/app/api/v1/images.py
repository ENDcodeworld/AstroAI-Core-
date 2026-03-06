"""
Image API Endpoints for AstroAI-Core

RESTful API for astronomical image access and analysis.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.models.image import Image

router = APIRouter()


@router.get("", response_model=dict, summary="Get astronomical images")
async def get_images(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search in title or description"),
    target_type: Optional[str] = Query(None, description="Filter by target type (Galaxy, Nebula, Star, etc.)"),
    mission: Optional[str] = Query(None, description="Filter by mission (Hubble, JWST, etc.)"),
    center: Optional[str] = Query(None, description="Filter by NASA center"),
    constellation: Optional[str] = Query(None, description="Filter by constellation"),
    is_processed: Optional[bool] = Query(None, description="Filter by AI processing status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a list of astronomical images with optional filtering.
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return (max 100)
    - **search**: Search term for title or description
    - **target_type**: Filter by astronomical target type
    - **mission**: Filter by space mission (Hubble, JWST, etc.)
    - **center**: Filter by NASA center
    - **constellation**: Filter by constellation
    - **is_processed**: Filter by AI analysis status
    
    Returns a list of image metadata with URLs.
    """
    try:
        # Build query
        query = select(Image)
        
        # Apply filters
        filters = []
        
        if search:
            filters.append(
                and_(
                    Image.title.ilike(f"%{search}%"),
                    Image.description.ilike(f"%{search}%")
                )
            )
        
        if target_type:
            filters.append(Image.target_type == target_type)
        
        if mission:
            filters.append(Image.mission.ilike(f"%{mission}%"))
        
        if center:
            filters.append(Image.center.ilike(f"%{center}%"))
        
        if constellation:
            filters.append(Image.constellation.ilike(f"%{constellation}%"))
        
        if is_processed is not None:
            filters.append(Image.is_processed == is_processed)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        images = result.scalars().all()
        
        # Get total count
        count_query = select(func.count(Image.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return {
            "items": [img.to_dict() for img in images],
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch images: {str(e)}"
        )


@router.get("/{image_id}", response_model=dict, summary="Get image by ID")
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific astronomical image.
    
    - **image_id**: Database ID of the image
    
    Returns complete image metadata including URLs and analysis results.
    """
    try:
        result = await db.execute(
            select(Image).where(Image.id == image_id)
        )
        image = result.scalar_one_or_none()
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with ID {image_id} not found"
            )
        
        return image.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch image: {str(e)}"
        )


@router.get("/nasa/{nasa_id}", response_model=dict, summary="Get image by NASA ID")
async def get_image_by_nasa_id(
    nasa_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get image by its NASA identifier.
    
    - **nasa_id**: NASA unique identifier for the image
    
    Returns the image record if found.
    """
    try:
        result = await db.execute(
            select(Image).where(Image.nasa_id == nasa_id)
        )
        image = result.scalar_one_or_none()
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with NASA ID '{nasa_id}' not found"
            )
        
        return image.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch image: {str(e)}"
        )


@router.post("/analyze", response_model=dict, summary="Analyze uploaded image")
async def analyze_image(
    file: UploadFile = File(..., description="Image file to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and analyze an astronomical image.
    
    - **file**: Image file (PNG, JPEG, FITS supported)
    
    Performs AI analysis on the uploaded image and returns results.
    Currently returns mock analysis - to be implemented with actual ML model.
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/fits"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size (max 50MB)
        if file_size > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size: 50MB"
            )
        
        # TODO: Implement actual AI analysis
        # For now, return mock analysis results
        analysis_results = {
            "status": "completed",
            "file_name": file.filename,
            "file_size_bytes": file_size,
            "content_type": file.content_type,
            "analysis": {
                "objects_detected": [],
                "classification": "pending",
                "confidence": 0.0,
                "note": "AI analysis model to be implemented in Phase 2"
            }
        }
        
        return {
            "success": True,
            "message": "Image uploaded successfully",
            "analysis": analysis_results,
            "next_steps": "Full AI analysis will be available in Phase 2"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze image: {str(e)}"
        )


@router.get("/stats/summary", response_model=dict, summary="Get image statistics")
async def get_image_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary statistics about images in the database.
    
    Returns counts by mission, target type, and processing status.
    """
    try:
        # Total count
        total_result = await db.execute(select(func.count(Image.id)))
        total = total_result.scalar()
        
        # Count by mission
        mission_result = await db.execute(
            select(Image.mission, func.count(Image.id))
            .group_by(Image.mission)
        )
        by_mission = {row[0] or 'Unknown': row[1] for row in mission_result.all()}
        
        # Count by target type
        target_result = await db.execute(
            select(Image.target_type, func.count(Image.id))
            .group_by(Image.target_type)
        )
        by_target = {row[0] or 'Unknown': row[1] for row in target_result.all()}
        
        # Count by NASA center
        center_result = await db.execute(
            select(Image.center, func.count(Image.id))
            .group_by(Image.center)
        )
        by_center = {row[0] or 'Unknown': row[1] for row in center_result.all()}
        
        # Processed vs unprocessed
        processed_result = await db.execute(
            select(func.count(Image.id)).where(Image.is_processed == True)
        )
        processed = processed_result.scalar()
        
        return {
            "total": total,
            "by_mission": by_mission,
            "by_target_type": by_target,
            "by_center": by_center,
            "processed": processed,
            "unprocessed": total - processed,
            "processing_rate": round(processed / total * 100, 1) if total > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


@router.get("/mission/{mission_name}", response_model=dict, summary="Get images by mission")
async def get_images_by_mission(
    mission_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get images from a specific space mission.
    
    - **mission_name**: Mission name (e.g., 'Hubble', 'JWST', 'James Webb')
    - **skip**: Pagination offset
    - **limit**: Maximum records to return
    """
    try:
        result = await db.execute(
            select(Image)
            .where(Image.mission.ilike(f"%{mission_name}%"))
            .offset(skip)
            .limit(limit)
        )
        images = result.scalars().all()
        
        # Get total count
        count_result = await db.execute(
            select(func.count(Image.id))
            .where(Image.mission.ilike(f"%{mission_name}%"))
        )
        total = count_result.scalar()
        
        return {
            "items": [img.to_dict() for img in images],
            "total": total,
            "mission": mission_name
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mission images: {str(e)}"
        )
