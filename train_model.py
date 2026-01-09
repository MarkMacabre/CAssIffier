#!/usr/bin/env python3
"""Training script for CAssIffier ML classifier."""

import sys
import logging
import argparse
from pathlib import Path

from cassiffier.training import ModelTrainer


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


def main():
    """Main entry point for training."""
    parser = argparse.ArgumentParser(
        description='Train ML classifier for CAssIffier'
    )
    parser.add_argument(
        'training_dir',
        help='Directory with organized training samples'
    )
    parser.add_argument(
        '-o', '--output',
        dest='output_path',
        default='models/classifier.joblib',
        help='Output path for trained model (default: models/classifier.joblib)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    print("="*60)
    print("CAssIffier - Model Training")
    print("="*60)
    print(f"Training directory: {args.training_dir}")
    print(f"Output model:       {args.output_path}")
    print("="*60)
    
    # Check training directory
    training_path = Path(args.training_dir)
    if not training_path.exists():
        print(f"Error: Training directory does not exist: {args.training_dir}")
        return 1
    
    try:
        # Train model
        trainer = ModelTrainer()
        model = trainer.train_and_save(args.training_dir, args.output_path)
        
        print("\n✓ Training complete!")
        print(f"Model saved to: {args.output_path}")
        
        return 0
        
    except ImportError as e:
        print(f"Error: {e}")
        print("\nPlease install required dependencies:")
        print("  pip install scikit-learn numpy librosa")
        return 1
    except Exception as e:
        print(f"Error during training: {e}")
        logging.exception("Training failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
