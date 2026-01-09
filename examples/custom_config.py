#!/usr/bin/env python3
"""
Custom configuration example for CAssIffier.

This script demonstrates how to use custom configuration
with different settings for confidence thresholds and other options.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cassiffier.config import Config


def main():
    """Demonstrate custom configuration."""
    
    # Create a custom configuration
    config = Config()
    
    # Adjust settings
    config.set('confidence_threshold', 0.8)  # Higher threshold
    config.set('max_duration', 20.0)  # Shorter max duration
    config.set('duplicate_action', 'skip')  # Auto-skip duplicates
    config.set('genre_confidence_threshold', 0.7)  # Higher genre threshold
    
    # Save configuration
    config.save('my_config.json')
    print("Custom configuration saved to my_config.json")
    
    # Display current configuration
    print("\nCurrent Configuration:")
    print(f"  Confidence Threshold: {config.get('confidence_threshold')}")
    print(f"  Max Duration: {config.get('max_duration')} seconds")
    print(f"  Duplicate Action: {config.get('duplicate_action')}")
    print(f"  Genre Confidence: {config.get('genre_confidence_threshold')}")
    print(f"  Scan Extensions: {config.get('scan_extensions')}")
    
    print("\nTo use this configuration:")
    print("  cassiffier /path/to/samples -o output -c my_config.json")


if __name__ == '__main__':
    main()
