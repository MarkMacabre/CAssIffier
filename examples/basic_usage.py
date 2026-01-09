#!/usr/bin/env python3
"""
Basic usage example for CAssIffier.

This script demonstrates the most common use case:
organizing audio samples from a directory.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cassiffier.config import Config
from cassiffier.database import Database
from cassiffier.scanner import Scanner
from cassiffier.hasher import DuplicateDetector
from cassiffier.features import FeatureExtractor
from cassiffier.classifier import Classifier
from cassiffier.organizer import Organizer


def organize_samples(input_dir, output_dir):
    """Organize audio samples from input_dir to output_dir.
    
    Args:
        input_dir: Directory containing audio samples.
        output_dir: Directory for organized library.
    """
    print(f"Organizing samples from: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # Setup configuration
    config = Config()
    
    # Initialize components
    database = Database(config.get('database_path'))
    scanner = Scanner(config.get('scan_extensions'))
    detector = DuplicateDetector(database)
    feature_extractor = FeatureExtractor()
    classifier = Classifier(config)
    organizer = Organizer(output_dir, config)
    
    # Scan for files
    print("\nScanning for audio files...")
    files = scanner.scan(input_dir, recursive=True)
    print(f"Found {len(files)} audio files")
    
    if not files:
        print("No files to process.")
        return
    
    # Process each file
    organized = 0
    skipped = 0
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Processing: {file_path.name}")
        
        try:
            # Check for duplicates
            file_hash = detector.get_hash(file_path)
            is_dup, existing, _ = detector.check_duplicate(file_path, file_hash)
            
            if is_dup:
                print("  → Skipped (duplicate)")
                skipped += 1
                continue
            
            # Extract features
            features = feature_extractor.extract_features(file_path)
            if not features:
                print("  → Failed to extract features")
                skipped += 1
                continue
            
            # Validate one-shot
            if not feature_extractor.is_valid_one_shot(features):
                print("  → Rejected: invalid duration")
                skipped += 1
                continue
            
            # Classify
            classification = classifier.classify(file_path, features)
            print(f"  → Category: {classification['category']}")
            
            if classification['subcategory']:
                print(f"  → Subcategory: {classification['subcategory']}")
            
            if classification['genre']:
                print(f"  → Genre: {classification['genre']}")
            
            print(f"  → Confidence: {classification['confidence']:.2f}")
            
            # Organize
            organized_path, needs_review = organizer.organize_file(
                file_path, classification
            )
            
            if organized_path:
                # Add to database
                database.add_file(
                    file_hash=file_hash,
                    original_path=str(file_path),
                    organized_path=organized_path,
                    category=classification['category'],
                    subcategory=classification['subcategory'],
                    genre=classification['genre'],
                    confidence=classification['confidence'],
                    features=features,
                    status='organized'
                )
                
                print(f"  ✓ Organized to: {organized_path}")
                organized += 1
                
                if needs_review:
                    print("  ⚠️  Low confidence - copied to review folder")
            else:
                print("  → Failed to organize")
                skipped += 1
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            skipped += 1
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total files:      {len(files)}")
    print(f"Organized:        {organized}")
    print(f"Skipped:          {skipped}")
    print("="*60)
    
    database.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python basic_usage.py <input_dir> <output_dir>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    organize_samples(input_dir, output_dir)
