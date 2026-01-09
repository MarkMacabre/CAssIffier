"""Context extraction from folder names and filenames."""

import re
from pathlib import Path
from cassiffier.categories import CATEGORY_KEYWORDS, GENRE_KEYWORDS


def tokenize(text):
    """Tokenize text by splitting on various delimiters.
    
    Args:
        text: Text to tokenize.
        
    Returns:
        List of lowercase tokens.
    """
    # Replace common delimiters with spaces
    text = re.sub(r'[_\-\.\s]+', ' ', text)
    
    # Handle camelCase by inserting spaces
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Split and convert to lowercase
    tokens = text.lower().split()
    
    return tokens


class ContextExtractor:
    """Extract semantic hints from folder and file names."""
    
    def __init__(self):
        """Initialize context extractor."""
        pass
    
    def extract_context(self, file_path, depth=5):
        """Extract context from file path.
        
        Args:
            file_path: Path to audio file.
            depth: How many parent directories to examine (default: 5).
            
        Returns:
            Dict with extracted context including tokens and hints.
        """
        path = Path(file_path)
        
        # Get filename without extension
        filename = path.stem
        filename_tokens = tokenize(filename)
        
        # Get parent folder tokens
        folder_tokens = []
        parts = path.parts
        # Get up to 'depth' parent folders
        for i in range(max(0, len(parts) - depth - 1), len(parts) - 1):
            folder_tokens.extend(tokenize(parts[i]))
        
        # Combine all tokens
        all_tokens = filename_tokens + folder_tokens
        
        context = {
            'filename_tokens': filename_tokens,
            'folder_tokens': folder_tokens,
            'all_tokens': all_tokens,
            'original_filename': filename,
            'parent_folder': path.parent.name
        }
        
        return context
    
    def find_category_hints(self, context):
        """Find category hints from context tokens.
        
        Args:
            context: Context dict from extract_context.
            
        Returns:
            Dict mapping categories to confidence scores.
        """
        hints = {}
        all_tokens = context['all_tokens']
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            if isinstance(keywords, dict):
                # Category has subcategories
                for subcategory, subkeywords in keywords.items():
                    for token in all_tokens:
                        for keyword in subkeywords:
                            if keyword in token:
                                key = f"{category}/{subcategory}"
                                hints[key] = hints.get(key, 0) + 1
            else:
                # Category without subcategories
                for token in all_tokens:
                    for keyword in keywords:
                        if keyword in token:
                            hints[category] = hints.get(category, 0) + 1
        
        return hints
    
    def find_genre_hints(self, context):
        """Find genre hints from context tokens.
        
        Args:
            context: Context dict from extract_context.
            
        Returns:
            Dict mapping genres to confidence scores.
        """
        hints = {}
        all_tokens = context['all_tokens']
        
        for genre, keywords in GENRE_KEYWORDS.items():
            for token in all_tokens:
                for keyword in keywords:
                    if keyword in token:
                        hints[genre] = hints.get(genre, 0) + 1
        
        return hints
    
    def extract_bpm(self, context):
        """Extract BPM from context if present.
        
        Args:
            context: Context dict from extract_context.
            
        Returns:
            BPM as integer, or None if not found.
        """
        all_tokens = context['all_tokens']
        
        for token in all_tokens:
            # Look for patterns like "140bpm" or "bpm140"
            match = re.search(r'(\d{2,3})bpm', token)
            if match:
                return int(match.group(1))
            
            match = re.search(r'bpm(\d{2,3})', token)
            if match:
                return int(match.group(1))
        
        return None
