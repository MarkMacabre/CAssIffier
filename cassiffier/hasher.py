"""File hashing and duplicate detection."""

import hashlib
from pathlib import Path


def compute_hash(file_path, algorithm='sha256', chunk_size=8192):
    """Compute hash of a file.
    
    Args:
        file_path: Path to file.
        algorithm: Hash algorithm to use (default: sha256).
        chunk_size: Size of chunks to read (default: 8192 bytes).
        
    Returns:
        Hex digest of the file hash.
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


class DuplicateDetector:
    """Handles duplicate detection using file hashes."""
    
    def __init__(self, database):
        """Initialize duplicate detector.
        
        Args:
            database: Database instance for looking up existing files.
        """
        self.database = database
    
    def check_duplicate(self, file_path):
        """Check if a file is a duplicate.
        
        Args:
            file_path: Path to file to check.
            
        Returns:
            Tuple of (is_duplicate, existing_record) where existing_record
            is the database record of the duplicate file, or None.
        """
        file_hash = compute_hash(file_path)
        existing = self.database.get_file_by_hash(file_hash)
        
        if existing:
            return True, existing
        return False, None
    
    def get_hash(self, file_path):
        """Get hash for a file.
        
        Args:
            file_path: Path to file.
            
        Returns:
            File hash as hex string.
        """
        return compute_hash(file_path)
