"""ML model training utilities."""

import logging
from pathlib import Path

try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("scikit-learn or numpy not available. ML training disabled.")

from cassiffier.features import FeatureExtractor


class ModelTrainer:
    """Train ML models for classification."""
    
    def __init__(self):
        """Initialize model trainer."""
        if not ML_AVAILABLE:
            raise ImportError(
                "scikit-learn and numpy are required for training. "
                "Install with: pip install scikit-learn numpy"
            )
        
        self.feature_extractor = FeatureExtractor()
    
    def prepare_training_data(self, training_dir):
        """Prepare training data from organized samples.
        
        Args:
            training_dir: Directory with organized training samples.
                         Should have structure: Category/Subcategory/files.ext
            
        Returns:
            Tuple of (X, y) where X is feature matrix and y is labels.
        """
        training_path = Path(training_dir)
        
        if not training_path.exists():
            raise ValueError(f"Training directory does not exist: {training_dir}")
        
        X = []
        y = []
        
        # Iterate through category folders
        for category_dir in training_path.iterdir():
            if not category_dir.is_dir():
                continue
            
            category = category_dir.name
            
            # Check for subcategories
            has_subcategories = False
            for item in category_dir.iterdir():
                if item.is_dir():
                    has_subcategories = True
                    break
            
            if has_subcategories:
                # Process subcategories
                for subcat_dir in category_dir.iterdir():
                    if not subcat_dir.is_dir():
                        continue
                    
                    subcategory = subcat_dir.name
                    label = f"{category}/{subcategory}"
                    
                    # Process files in subcategory
                    for audio_file in subcat_dir.glob('*'):
                        if audio_file.suffix.lower() in ['.wav', '.mp3']:
                            features = self._extract_features_safe(audio_file)
                            if features:
                                X.append(features)
                                y.append(label)
            else:
                # Process files directly in category
                for audio_file in category_dir.glob('*'):
                    if audio_file.suffix.lower() in ['.wav', '.mp3']:
                        features = self._extract_features_safe(audio_file)
                        if features:
                            X.append(features)
                            y.append(category)
        
        if not X:
            raise ValueError("No training data found")
        
        X = np.array(X)
        y = np.array(y)
        
        logging.info(f"Prepared {len(X)} training samples with {len(set(y))} classes")
        return X, y
    
    def _extract_features_safe(self, audio_file):
        """Extract features with error handling.
        
        Args:
            audio_file: Path to audio file.
            
        Returns:
            Feature vector or None on error.
        """
        try:
            features = self.feature_extractor.extract_features(audio_file)
            if features:
                return self.feature_extractor.features_to_vector(features)
        except Exception as e:
            logging.warning(f"Failed to extract features from {audio_file}: {e}")
        return None
    
    def train_model(self, X, y, test_size=0.2, random_state=42):
        """Train a Random Forest classifier.
        
        Args:
            X: Feature matrix.
            y: Labels.
            test_size: Proportion of data to use for testing.
            random_state: Random seed for reproducibility.
            
        Returns:
            Trained model.
        """
        # Check for classes with too few samples for stratification
        unique, counts = np.unique(y, return_counts=True)
        min_samples = counts.min()
        
        # Only use stratification if all classes have at least 2 samples
        stratify_arg = y if min_samples >= 2 else None
        if stratify_arg is None:
            logging.warning("Some classes have only 1 sample. Disabling stratification.")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=stratify_arg
        )
        
        logging.info(f"Training set: {len(X_train)} samples")
        logging.info(f"Test set: {len(X_test)} samples")
        
        # Train Random Forest
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )
        
        logging.info("Training model...")
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logging.info(f"Model accuracy: {accuracy:.3f}")
        logging.info("\nClassification Report:")
        logging.info(classification_report(y_test, y_pred))
        
        return model
    
    def save_model(self, model, output_path):
        """Save trained model to disk.
        
        Args:
            model: Trained model.
            output_path: Path to save model.
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(model, output_file)
        logging.info(f"Model saved to {output_path}")
    
    def train_and_save(self, training_dir, output_path):
        """Complete training pipeline.
        
        Args:
            training_dir: Directory with training data.
            output_path: Path to save trained model.
            
        Returns:
            Trained model.
        """
        logging.info("Preparing training data...")
        X, y = self.prepare_training_data(training_dir)
        
        logging.info("Training model...")
        model = self.train_model(X, y)
        
        logging.info("Saving model...")
        self.save_model(model, output_path)
        
        return model
