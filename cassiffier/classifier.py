"""Hybrid rule-based and ML classification."""

import logging
from pathlib import Path

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    logging.warning("joblib not available. ML classification will be disabled.")

from cassiffier.categories import (
    CATEGORIES, get_all_categories, get_subcategories, is_genre_aware
)
from cassiffier.context import ContextExtractor


class Classifier:
    """Hybrid classifier using rules and ML."""
    
    def __init__(self, config):
        """Initialize classifier.
        
        Args:
            config: Config instance with classifier settings.
        """
        self.config = config
        self.context_extractor = ContextExtractor()
        self.ml_model = None
        self.use_ml = config.get('use_ml_classifier', True)
        
        # Try to load ML model if enabled
        if self.use_ml:
            self._load_ml_model()
    
    def _load_ml_model(self):
        """Load ML model from disk."""
        model_path = self.config.get('ml_model_path')
        if not model_path:
            logging.info("No ML model path configured")
            return
        
        model_file = Path(model_path)
        if not model_file.exists():
            logging.info(f"ML model not found at {model_path}. Will use rule-based only.")
            return
        
        if not JOBLIB_AVAILABLE:
            logging.warning("joblib not available. Cannot load ML model.")
            return
        
        try:
            self.ml_model = joblib.load(model_file)
            logging.info(f"Loaded ML model from {model_path}")
        except Exception as e:
            logging.error(f"Failed to load ML model: {e}")
    
    def classify(self, file_path, features=None):
        """Classify an audio file.
        
        Args:
            file_path: Path to audio file.
            features: Optional pre-extracted features.
            
        Returns:
            Classification result dict with:
            - category: Main category
            - subcategory: Subcategory (if applicable)
            - genre: Genre (if applicable)
            - confidence: Confidence score (0-1)
            - method: Classification method used ('rule' or 'ml')
        """
        # Extract context from file path
        context = self.context_extractor.extract_context(file_path)
        
        # Try rule-based classification first
        rule_result = self._classify_by_rules(context)
        
        if rule_result and rule_result['confidence'] >= 0.8:
            # High confidence rule match
            return rule_result
        
        # Try ML classification if available
        if self.ml_model and features:
            ml_result = self._classify_by_ml(features, context)
            
            # If ML has higher confidence, use it
            if ml_result and ml_result['confidence'] > rule_result.get('confidence', 0):
                return ml_result
        
        # Return rule result or default to Unknown
        if rule_result:
            return rule_result
        
        return {
            'category': 'Unknown',
            'subcategory': None,
            'genre': None,
            'confidence': 0.0,
            'method': 'default'
        }
    
    def _classify_by_rules(self, context):
        """Classify using rule-based approach.
        
        Args:
            context: Context dict from ContextExtractor.
            
        Returns:
            Classification result dict or None.
        """
        # Get category hints from context
        category_hints = self.context_extractor.find_category_hints(context)
        
        if not category_hints:
            return None
        
        # Find the category/subcategory with highest score
        best_match = max(category_hints.items(), key=lambda x: x[1])
        match_key, match_score = best_match
        
        # Parse category and subcategory
        if '/' in match_key:
            category, subcategory = match_key.split('/')
        else:
            category = match_key
            subcategory = None
        
        # Calculate confidence based on match score
        # Score is number of keyword matches
        # Confidence scales with score, capped at 0.95
        confidence = min(0.95, 0.5 + (match_score * 0.15))
        
        # Try to detect genre if category is genre-aware
        genre = None
        genre_confidence = 0.0
        
        if is_genre_aware(category):
            genre_hints = self.context_extractor.find_genre_hints(context)
            if genre_hints:
                best_genre = max(genre_hints.items(), key=lambda x: x[1])
                genre, genre_score = best_genre
                genre_confidence = min(0.95, 0.5 + (genre_score * 0.15))
                
                # Only use genre if confidence is above threshold
                if genre_confidence < self.config.get('genre_confidence_threshold', 0.6):
                    genre = None
        
        return {
            'category': category,
            'subcategory': subcategory,
            'genre': genre,
            'confidence': confidence,
            'method': 'rule'
        }
    
    def _classify_by_ml(self, features, context):
        """Classify using ML model.
        
        Args:
            features: Audio features dict.
            context: Context dict from ContextExtractor.
            
        Returns:
            Classification result dict or None.
        """
        if not self.ml_model:
            return None
        
        try:
            from cassiffier.features import FeatureExtractor
            
            # Convert features to vector
            extractor = FeatureExtractor()
            feature_vector = extractor.features_to_vector(features)
            
            if feature_vector is None:
                return None
            
            # Reshape for prediction
            feature_vector = feature_vector.reshape(1, -1)
            
            # Get prediction and probabilities
            prediction = self.ml_model.predict(feature_vector)[0]
            
            # Try to get probability if model supports it
            confidence = 0.5
            if hasattr(self.ml_model, 'predict_proba'):
                probabilities = self.ml_model.predict_proba(feature_vector)[0]
                confidence = float(max(probabilities))
            
            # Parse prediction (format: "Category/Subcategory" or "Category")
            if '/' in prediction:
                category, subcategory = prediction.split('/', 1)
            else:
                category = prediction
                subcategory = None
            
            # Try to detect genre if category is genre-aware
            genre = None
            if is_genre_aware(category):
                genre_hints = self.context_extractor.find_genre_hints(context)
                if genre_hints:
                    best_genre = max(genre_hints.items(), key=lambda x: x[1])
                    genre, _ = best_genre
            
            return {
                'category': category,
                'subcategory': subcategory,
                'genre': genre,
                'confidence': confidence,
                'method': 'ml'
            }
            
        except Exception as e:
            logging.error(f"ML classification failed: {e}")
            return None
