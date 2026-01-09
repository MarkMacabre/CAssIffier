"""Main CLI entry point for CAssIffier."""

import sys
import logging
from pathlib import Path
import argparse

from cassiffier.config import Config
from cassiffier.database import Database
from cassiffier.scanner import Scanner
from cassiffier.hasher import DuplicateDetector
from cassiffier.features import FeatureExtractor
from cassiffier.classifier import Classifier
from cassiffier.organizer import Organizer


def setup_logging(verbose=False):
    """Setup logging configuration.
    
    Args:
        verbose: Enable verbose logging.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def handle_duplicate(file_path, existing_record, config):
    """Handle duplicate file detection.
    
    Args:
        file_path: Path to duplicate file.
        existing_record: Database record of existing file.
        config: Config instance.
        
    Returns:
        Action to take: 'skip', 'keep_both', or 'delete'
    """
    duplicate_action = config.get('duplicate_action', 'ask')
    
    if duplicate_action == 'skip':
        return 'skip'
    elif duplicate_action == 'keep_both':
        return 'keep_both'
    elif duplicate_action == 'delete':
        return 'delete'
    else:
        # Ask user
        print(f"\n⚠️  Duplicate file detected!")
        print(f"  Original: {existing_record['original_path']}")
        print(f"  New:      {file_path}")
        print(f"\nWhat would you like to do?")
        print("  [s] Skip this file")
        print("  [k] Keep both files")
        print("  [d] Delete duplicate")
        print("  [a] Skip all future duplicates")
        
        while True:
            choice = input("\nYour choice: ").lower().strip()
            if choice == 's':
                return 'skip'
            elif choice == 'k':
                return 'keep_both'
            elif choice == 'd':
                return 'delete'
            elif choice == 'a':
                config.set('duplicate_action', 'skip')
                return 'skip'
            else:
                print("Invalid choice. Please enter s, k, d, or a.")


def process_files(files, database, detector, feature_extractor, classifier, 
                  organizer, config):
    """Process a list of audio files.
    
    Args:
        files: List of file paths to process.
        database: Database instance.
        detector: DuplicateDetector instance.
        feature_extractor: FeatureExtractor instance.
        classifier: Classifier instance.
        organizer: Organizer instance.
        config: Config instance.
    """
    total = len(files)
    processed = 0
    skipped = 0
    organized = 0
    needs_review = 0
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{total}] Processing: {file_path.name}")
        
        try:
            # Check for duplicates
            file_hash = detector.get_hash(file_path)
            is_dup, existing = detector.check_duplicate(file_path)
            
            if is_dup:
                action = handle_duplicate(file_path, existing, config)
                
                if action == 'skip':
                    print("  → Skipped (duplicate)")
                    skipped += 1
                    continue
                elif action == 'delete':
                    file_path.unlink()
                    print("  → Deleted (duplicate)")
                    skipped += 1
                    continue
                # If 'keep_both', continue processing
            
            # Extract features
            print("  → Extracting features...")
            features = feature_extractor.extract_features(file_path)
            
            if not features:
                print("  → Failed to extract features")
                skipped += 1
                continue
            
            # Check if valid one-shot
            if not feature_extractor.is_valid_one_shot(
                features, 
                config.get('max_duration', 30.0),
                config.get('min_duration', 0.01)
            ):
                duration = features.get('duration', 0)
                print(f"  → Rejected: invalid duration ({duration:.2f}s)")
                skipped += 1
                continue
            
            # Classify
            print("  → Classifying...")
            classification = classifier.classify(file_path, features)
            
            print(f"  → Category: {classification['category']}")
            if classification['subcategory']:
                print(f"  → Subcategory: {classification['subcategory']}")
            if classification['genre']:
                print(f"  → Genre: {classification['genre']}")
            print(f"  → Confidence: {classification['confidence']:.2f} ({classification['method']})")
            
            # Organize file
            print("  → Organizing...")
            organized_path, review = organizer.organize_file(
                file_path, classification, copy=False
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
                
                if review:
                    print("  ⚠️  Low confidence - copied to review folder")
                    needs_review += 1
            else:
                print("  → Failed to organize")
                skipped += 1
            
            processed += 1
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
            print(f"  ✗ Error: {e}")
            skipped += 1
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total files:      {total}")
    print(f"Organized:        {organized}")
    print(f"Needs review:     {needs_review}")
    print(f"Skipped:          {skipped}")
    print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='CAssIffier - Audio Sample Organization System'
    )
    parser.add_argument(
        'input_dir',
        nargs='?',
        help='Root directory to scan for audio files'
    )
    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        default='organized_library',
        help='Output directory for organized library (default: organized_library)'
    )
    parser.add_argument(
        '-c', '--config',
        dest='config_file',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Only process new files not in database'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--create-structure',
        action='store_true',
        help='Create empty folder structure and exit'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Load configuration
    config = Config(args.config_file)
    
    # Create organizer
    organizer = Organizer(args.output_dir, config)
    
    # If just creating structure, do that and exit
    if args.create_structure:
        print(f"Creating library structure in {args.output_dir}...")
        organizer.create_structure()
        print("Done!")
        return 0
    
    # Check input directory
    if not args.input_dir:
        print("Error: input_dir is required")
        print("Usage: python -m cassiffier.main <input_dir> [options]")
        return 1
    
    input_path = Path(args.input_dir)
    if not input_path.exists():
        print(f"Error: Directory does not exist: {args.input_dir}")
        return 1
    
    print("="*60)
    print("CAssIffier - Audio Sample Organization System")
    print("="*60)
    print(f"Input directory:  {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Database:         {config.get('database_path')}")
    print("="*60)
    
    # Initialize components
    database = Database(config.get('database_path'))
    scanner = Scanner(config.get('scan_extensions'))
    detector = DuplicateDetector(database)
    
    try:
        feature_extractor = FeatureExtractor()
    except ImportError as e:
        print(f"Error: {e}")
        return 1
    
    classifier = Classifier(config)
    
    # Scan for files
    print("\nScanning for audio files...")
    files = scanner.scan(args.input_dir, recursive=True)
    print(f"Found {len(files)} audio files")
    
    if args.incremental:
        print("\nFiltering for new files only...")
        files = scanner.filter_new_files(files, database)
        print(f"Found {len(files)} new files")
    
    if not files:
        print("\nNo files to process.")
        return 0
    
    # Process files
    process_files(files, database, detector, feature_extractor, 
                  classifier, organizer, config)
    
    # Print database statistics
    print("\nDatabase statistics:")
    stats = database.get_statistics()
    print(f"  Total files: {stats['total_files']}")
    if stats.get('by_category'):
        print("  By category:")
        for cat, count in sorted(stats['by_category'].items()):
            print(f"    {cat}: {count}")
    
    database.close()
    
    print("\n✓ Processing complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
