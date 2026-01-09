"""Filesystem scanner for audio files."""

import logging
from pathlib import Path


class Scanner:
    """Scan directories for audio files."""
    
    def __init__(self, extensions=None):
        """Initialize scanner.
        
        Args:
            extensions: List of file extensions to scan (e.g., ['.wav', '.mp3']).
                       If None, defaults to ['.wav', '.mp3'].
        """
        self.extensions = extensions or ['.wav', '.mp3']
        # Ensure extensions start with dot
        self.extensions = [ext if ext.startswith('.') else f'.{ext}' 
                          for ext in self.extensions]
    
    def scan(self, root_dir, recursive=True):
        """Scan directory for audio files.
        
        Args:
            root_dir: Root directory to scan.
            recursive: Whether to scan recursively (default: True).
            
        Returns:
            List of Path objects for audio files found.
        """
        root_path = Path(root_dir)
        
        if not root_path.exists():
            logging.error(f"Directory does not exist: {root_dir}")
            return []
        
        if not root_path.is_dir():
            logging.error(f"Not a directory: {root_dir}")
            return []
        
        audio_files = []
        
        if recursive:
            # Recursive scan using rglob
            for ext in self.extensions:
                pattern = f"**/*{ext}"
                audio_files.extend(root_path.rglob(pattern))
        else:
            # Non-recursive scan using glob
            for ext in self.extensions:
                pattern = f"*{ext}"
                audio_files.extend(root_path.glob(pattern))
        
        # Sort by path for consistent ordering
        audio_files.sort()
        
        logging.info(f"Found {len(audio_files)} audio files in {root_dir}")
        return audio_files
    
    def filter_new_files(self, files, database):
        """Filter files to only include new ones not in database.
        
        Args:
            files: List of file paths.
            database: Database instance to check against.
            
        Returns:
            List of new file paths.
        """
        new_files = []
        
        for file_path in files:
            # Check if file already in database by path
            existing = database.get_file_by_path(str(file_path))
            if not existing:
                new_files.append(file_path)
        
        logging.info(f"Filtered to {len(new_files)} new files")
        return new_files
