"""File organization and moving."""

import logging
import shutil
from pathlib import Path


class Organizer:
    """Organize and move audio files to categorized folders."""
    
    def __init__(self, output_dir, config):
        """Initialize organizer.
        
        Args:
            output_dir: Root directory for organized library.
            config: Config instance.
        """
        self.output_dir = Path(output_dir)
        self.config = config
        self.review_folder = config.get('review_folder_name', '⚠_Review')
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
    
    def organize_file(self, file_path, classification, copy=False):
        """Organize a file based on its classification.
        
        Args:
            file_path: Path to file to organize.
            classification: Classification result dict.
            copy: If True, copy instead of move (default: False).
            
        Returns:
            Tuple of (organized_path, needs_review) where organized_path is the
            new file path and needs_review is True if file also placed in review.
        """
        source_path = Path(file_path)
        
        if not source_path.exists():
            logging.error(f"Source file does not exist: {file_path}")
            return None, False
        
        # Build destination path
        dest_path = self._build_path(source_path, classification)
        
        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle filename conflicts
        dest_path = self._resolve_conflict(dest_path)
        
        # Copy or move file
        try:
            if copy:
                shutil.copy2(source_path, dest_path)
                logging.info(f"Copied {source_path} -> {dest_path}")
            else:
                shutil.move(source_path, dest_path)
                logging.info(f"Moved {source_path} -> {dest_path}")
        except Exception as e:
            logging.error(f"Failed to organize {source_path}: {e}")
            return None, False
        
        # Check if needs review
        needs_review = classification['confidence'] < self.confidence_threshold
        
        if needs_review:
            self._copy_to_review(dest_path, classification)
        
        return str(dest_path), needs_review
    
    def _build_path(self, source_path, classification):
        """Build destination path based on classification.
        
        Args:
            source_path: Original file path.
            classification: Classification result dict.
            
        Returns:
            Path object for destination.
        """
        category = classification['category']
        subcategory = classification.get('subcategory')
        genre = classification.get('genre')
        
        # Start with output directory and category
        path_parts = [self.output_dir, category]
        
        # Add genre if present and category is genre-aware
        if genre:
            path_parts.append(genre)
        
        # Add subcategory if present
        if subcategory:
            path_parts.append(subcategory)
        
        # Add filename
        filename = source_path.name
        
        return Path(*path_parts, filename)
    
    def _resolve_conflict(self, dest_path):
        """Resolve filename conflict by adding number suffix.
        
        Args:
            dest_path: Destination path that may conflict.
            
        Returns:
            Path object with unique filename.
        """
        if not dest_path.exists():
            return dest_path
        
        # Add number suffix
        stem = dest_path.stem
        suffix = dest_path.suffix
        parent = dest_path.parent
        
        counter = 1
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _copy_to_review(self, file_path, classification):
        """Copy file to review folder for manual inspection.
        
        Args:
            file_path: Path to organized file.
            classification: Classification result dict.
        """
        review_dir = self.output_dir / self.review_folder
        review_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a subfolder with the predicted category
        category = classification['category']
        confidence = classification['confidence']
        
        # Build review path with category subfolder
        review_subdir = review_dir / f"{category}_conf{confidence:.2f}"
        review_subdir.mkdir(parents=True, exist_ok=True)
        
        # Copy file to review
        source_path = Path(file_path)
        dest_path = review_subdir / source_path.name
        
        # Resolve conflict if needed
        dest_path = self._resolve_conflict(dest_path)
        
        try:
            shutil.copy2(source_path, dest_path)
            logging.info(f"Copied to review: {dest_path}")
        except Exception as e:
            logging.error(f"Failed to copy to review: {e}")
    
    def create_structure(self):
        """Create the base folder structure for the organized library."""
        # This creates empty directories for all categories
        # Not strictly necessary since they're created on-demand,
        # but can be useful for visualization
        from cassiffier.categories import CATEGORIES
        
        for category, info in CATEGORIES.items():
            category_dir = self.output_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            subcategories = info.get('subcategories', [])
            for subcategory in subcategories:
                subcat_dir = category_dir / subcategory
                subcat_dir.mkdir(parents=True, exist_ok=True)
        
        # Create review folder
        review_dir = self.output_dir / self.review_folder
        review_dir.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"Created library structure in {self.output_dir}")
