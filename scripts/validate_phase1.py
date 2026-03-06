#!/usr/bin/env python3
"""
Phase 1 Validation Script

Validates all Phase 1 components are properly implemented.
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'api'))

def check_file_exists(filepath, description):
    """Check if file exists."""
    path = project_root / filepath
    exists = path.exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {filepath}")
    if not exists:
        print(f"     ERROR: File not found!")
    return exists

def check_import(module_path, description):
    """Check if module can be imported."""
    try:
        # Convert path to module name
        module_name = module_path.replace('/', '.').replace('.py', '')
        __import__(module_name)
        print(f"  ✓ {description}: {module_path}")
        return True
    except Exception as e:
        print(f"  ✗ {description}: {module_path}")
        print(f"     ERROR: {e}")
        return False

def main():
    print("=" * 70)
    print("AstroAI-Core Phase 1 Validation")
    print("=" * 70)
    print()
    
    all_passed = True
    
    # Check files exist
    print("1. Checking file structure...")
    files_to_check = [
        ("api/app/services/nasa_data_service.py", "NASA Data Service"),
        ("api/app/services/data_pipeline.py", "Data Pipeline"),
        ("api/app/models/exoplanet.py", "Exoplanet Model"),
        ("api/app/models/star.py", "Star Model"),
        ("api/app/models/image.py", "Image Model"),
        ("api/app/api/v1/exoplanets.py", "Exoplanet API"),
        ("api/app/api/v1/images.py", "Image API"),
        ("tests/test_data_service.py", "Data Service Tests"),
        ("tests/test_api.py", "API Tests"),
        ("docs/PHASE1_DEVELOPMENT.md", "Phase 1 Documentation"),
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_passed = False
    
    print()
    
    # Check syntax
    print("2. Checking Python syntax...")
    import py_compile
    py_files = [
        "api/app/services/nasa_data_service.py",
        "api/app/services/data_pipeline.py",
        "api/app/models/exoplanet.py",
        "api/app/models/star.py",
        "api/app/models/image.py",
        "api/app/api/v1/exoplanets.py",
        "api/app/api/v1/images.py",
    ]
    
    for filepath in py_files:
        path = project_root / filepath
        try:
            py_compile.compile(str(path), doraise=True)
            print(f"  ✓ Syntax OK: {filepath}")
        except py_compile.PyCompileError as e:
            print(f"  ✗ Syntax Error: {filepath}")
            print(f"     {e}")
            all_passed = False
    
    print()
    
    # Check classes and functions exist
    print("3. Checking NASA API Service classes...")
    try:
        from app.services.nasa_data_service import NASAApiService, NASAAPIError, CacheEntry
        
        # Check NASAApiService methods
        required_methods = [
            'fetch_tess_exoplanets',
            'fetch_kepler_light_curves',
            'fetch_hubble_images',
            'fetch_apod',
            'fetch_all_exoplanets',
            '_request_with_retry',
            '_generate_cache_key',
            '_save_to_cache',
            '_get_from_cache',
            'clear_cache',
            'save_to_json'
        ]
        
        for method in required_methods:
            if hasattr(NASAApiService, method):
                print(f"  ✓ Method: {method}")
            else:
                print(f"  ✗ Missing method: {method}")
                all_passed = False
        
        print(f"  ✓ CacheEntry class exists")
        print(f"  ✓ NASAAPIError exception exists")
        
    except Exception as e:
        print(f"  ✗ Error importing NASA service: {e}")
        all_passed = False
    
    print()
    
    # Check Data Pipeline
    print("4. Checking Data Pipeline classes...")
    try:
        from app.services.data_pipeline import DataPipeline, DataQuality, ProcessingResult, run_pipeline
        
        # Check DataQuality enum values
        quality_levels = ['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'INVALID']
        for level in quality_levels:
            if hasattr(DataQuality, level):
                print(f"  ✓ Quality level: {level}")
            else:
                print(f"  ✗ Missing quality level: {level}")
                all_passed = False
        
        # Check DataPipeline methods
        required_methods = [
            'process_exoplanets',
            'process_stars',
            'process_images',
            '_validate_exoplanet_data',
            '_validate_star_data',
            '_validate_image_data',
            'get_incremental_update_stats'
        ]
        
        for method in required_methods:
            if hasattr(DataPipeline, method):
                print(f"  ✓ Method: {method}")
            else:
                print(f"  ✗ Missing method: {method}")
                all_passed = False
        
        print(f"  ✓ run_pipeline function exists")
        
    except Exception as e:
        print(f"  ✗ Error importing data pipeline: {e}")
        all_passed = False
    
    print()
    
    # Check Models
    print("5. Checking Database Models...")
    try:
        from app.models.exoplanet import Exoplanet
        from app.models.star import Star
        from app.models.image import Image
        
        # Check Exoplanet
        print(f"  ✓ Exoplanet model: __tablename__ = '{Exoplanet.__tablename__}'")
        
        # Check Star
        print(f"  ✓ Star model: __tablename__ = '{Star.__tablename__}'")
        
        # Check Image
        print(f"  ✓ Image model: __tablename__ = '{Image.__tablename__}'")
        
    except Exception as e:
        print(f"  ✗ Error importing models: {e}")
        all_passed = False
    
    print()
    
    # Check API endpoints
    print("6. Checking API Endpoints...")
    try:
        from app.api.v1.exoplanets import router as exoplanet_router
        from app.api.v1.images import router as image_router
        
        # Check exoplanet routes
        exoplanet_routes = [route.path for route in exoplanet_router.routes]
        print(f"  ✓ Exoplanet routes: {len(exoplanet_routes)} endpoints")
        for route in exoplanet_routes:
            print(f"     - {route}")
        
        # Check image routes
        image_routes = [route.path for route in image_router.routes]
        print(f"  ✓ Image routes: {len(image_routes)} endpoints")
        for route in image_routes:
            print(f"     - {route}")
        
    except Exception as e:
        print(f"  ✗ Error importing API endpoints: {e}")
        all_passed = False
    
    print()
    
    # Summary
    print("=" * 70)
    if all_passed:
        print("✓ Phase 1 Validation: PASSED")
        print()
        print("All components are properly implemented:")
        print("  • NASA Data Acquisition Module")
        print("  • Data Processing Pipeline")
        print("  • Database Models (Exoplanet, Star, Image)")
        print("  • RESTful API Endpoints")
        print("  • Unit Tests")
        print("  • Documentation")
    else:
        print("✗ Phase 1 Validation: FAILED")
        print()
        print("Some components have issues. Please review the errors above.")
    print("=" * 70)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
