#!/usr/bin/env python3
"""
Database inspection example for CAssIffier.

This script shows how to query the database to inspect
processed files and their classifications.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cassiffier.database import Database


def inspect_database(db_path='cassiffier.db'):
    """Inspect the CAssIffier database.
    
    Args:
        db_path: Path to the database file.
    """
    print(f"Inspecting database: {db_path}")
    print("="*60)
    
    # Open database
    db = Database(db_path)
    
    # Get statistics
    stats = db.get_statistics()
    
    print(f"\nTotal Files: {stats['total_files']}")
    
    if stats.get('by_status'):
        print("\nBy Status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")
    
    if stats.get('by_category'):
        print("\nBy Category:")
        for category, count in sorted(stats['by_category'].items()):
            print(f"  {category}: {count}")
    
    # Get all organized files
    organized_files = db.get_all_files(status='organized')
    
    if organized_files:
        print(f"\nSample of Organized Files:")
        print("-"*60)
        
        # Show first 10
        for file_record in organized_files[:10]:
            print(f"\nOriginal: {file_record['original_path']}")
            print(f"Organized: {file_record['organized_path']}")
            print(f"Category: {file_record['category']}")
            if file_record['subcategory']:
                print(f"Subcategory: {file_record['subcategory']}")
            if file_record['genre']:
                print(f"Genre: {file_record['genre']}")
            print(f"Confidence: {file_record['confidence']:.2f}")
        
        if len(organized_files) > 10:
            print(f"\n... and {len(organized_files) - 10} more files")
    
    db.close()


if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'cassiffier.db'
    
    if not Path(db_path).exists():
        print(f"Error: Database not found at {db_path}")
        print("\nRun CAssIffier first to create a database:")
        print("  cassiffier /path/to/samples -o output")
        sys.exit(1)
    
    inspect_database(db_path)
