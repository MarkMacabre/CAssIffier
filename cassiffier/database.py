"""Database layer for CAssIffier using SQLite."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


class Database:
    """SQLite database for tracking files and classifications."""
    
    def __init__(self, db_path="cassiffier.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Files table - stores file information and hashes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT UNIQUE NOT NULL,
                original_path TEXT NOT NULL,
                organized_path TEXT,
                category TEXT,
                subcategory TEXT,
                genre TEXT,
                confidence REAL,
                features TEXT,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        # Create index on file_hash for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_file_hash 
            ON files(file_hash)
        """)
        
        # Create index on organized_path
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_organized_path 
            ON files(organized_path)
        """)
        
        self.conn.commit()
    
    def add_file(self, file_hash, original_path, category=None, subcategory=None,
                 genre=None, confidence=None, features=None, organized_path=None,
                 status='pending'):
        """Add a file record to the database.
        
        Args:
            file_hash: SHA-256 hash of the file.
            original_path: Original file path.
            category: Classified category.
            subcategory: Classified subcategory.
            genre: Detected genre (if applicable).
            confidence: Classification confidence score.
            features: Audio features as dict.
            organized_path: Path after organization.
            status: File status (pending, organized, skipped, etc.)
            
        Returns:
            File ID if successful, None if duplicate.
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        # Convert features dict to JSON string
        features_json = json.dumps(features) if features else None
        
        try:
            cursor.execute("""
                INSERT INTO files (file_hash, original_path, organized_path,
                                 category, subcategory, genre, confidence,
                                 features, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (file_hash, original_path, organized_path, category,
                  subcategory, genre, confidence, features_json,
                  timestamp, status))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # File hash already exists
            return None
    
    def get_file_by_hash(self, file_hash):
        """Get file record by hash.
        
        Args:
            file_hash: SHA-256 hash of the file.
            
        Returns:
            File record as dict, or None if not found.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE file_hash = ?", (file_hash,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_file_by_path(self, path):
        """Get file record by original path.
        
        Args:
            path: Original file path.
            
        Returns:
            File record as dict, or None if not found.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE original_path = ?", (path,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_file(self, file_id, **kwargs):
        """Update file record.
        
        Args:
            file_id: File ID to update.
            **kwargs: Fields to update.
        """
        if not kwargs:
            return
        
        # Handle features separately if provided
        if 'features' in kwargs and isinstance(kwargs['features'], dict):
            kwargs['features'] = json.dumps(kwargs['features'])
        
        cursor = self.conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [file_id]
        
        cursor.execute(f"""
            UPDATE files SET {set_clause} WHERE id = ?
        """, values)
        self.conn.commit()
    
    def get_all_files(self, status=None):
        """Get all file records.
        
        Args:
            status: Filter by status (optional).
            
        Returns:
            List of file records as dicts.
        """
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * FROM files WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM files")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self):
        """Get database statistics.
        
        Returns:
            Dict with statistics.
        """
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total files
        cursor.execute("SELECT COUNT(*) as count FROM files")
        stats['total_files'] = cursor.fetchone()['count']
        
        # Files by status
        cursor.execute("SELECT status, COUNT(*) as count FROM files GROUP BY status")
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Files by category
        cursor.execute("SELECT category, COUNT(*) as count FROM files WHERE category IS NOT NULL GROUP BY category")
        stats['by_category'] = {row['category']: row['count'] for row in cursor.fetchall()}
        
        return stats
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
