"""Audio feature extraction using librosa."""

import logging
import numpy as np

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logging.warning("librosa not available. Feature extraction will be limited.")


class FeatureExtractor:
    """Extract audio features from audio files."""
    
    def __init__(self, sr=22050):
        """Initialize feature extractor.
        
        Args:
            sr: Sample rate for audio loading (default: 22050).
        """
        self.sr = sr
        
        if not LIBROSA_AVAILABLE:
            raise ImportError("librosa is required for feature extraction. Install it with: pip install librosa")
    
    def extract_features(self, file_path):
        """Extract audio features from a file.
        
        Args:
            file_path: Path to audio file.
            
        Returns:
            Dict with extracted features, or None if extraction fails.
        """
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=self.sr, mono=True)
            
            # Duration
            duration = librosa.get_duration(y=y, sr=sr)
            
            # RMS energy
            rms = librosa.feature.rms(y=y)[0]
            rms_mean = float(np.mean(rms))
            rms_std = float(np.std(rms))
            
            # Spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_centroid_mean = float(np.mean(spectral_centroids))
            spectral_centroid_std = float(np.std(spectral_centroids))
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            zcr_mean = float(np.mean(zcr))
            zcr_std = float(np.std(zcr))
            
            # MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_means = [float(np.mean(mfcc)) for mfcc in mfccs]
            mfcc_stds = [float(np.std(mfcc)) for mfcc in mfccs]
            
            features = {
                'duration': duration,
                'rms_mean': rms_mean,
                'rms_std': rms_std,
                'spectral_centroid_mean': spectral_centroid_mean,
                'spectral_centroid_std': spectral_centroid_std,
                'zcr_mean': zcr_mean,
                'zcr_std': zcr_std,
                'mfcc_means': mfcc_means,
                'mfcc_stds': mfcc_stds
            }
            
            return features
            
        except Exception as e:
            logging.error(f"Failed to extract features from {file_path}: {e}")
            return None
    
    def is_valid_one_shot(self, features, max_duration=30.0, min_duration=0.01):
        """Check if audio file appears to be a valid one-shot.
        
        Args:
            features: Feature dict from extract_features.
            max_duration: Maximum duration for one-shot (seconds).
            min_duration: Minimum duration for one-shot (seconds).
            
        Returns:
            Boolean indicating if this appears to be a one-shot.
        """
        if not features:
            return False
        
        duration = features.get('duration', 0)
        
        if duration < min_duration or duration > max_duration:
            return False
        
        return True
    
    def features_to_vector(self, features):
        """Convert features dict to flat numpy array for ML.
        
        Args:
            features: Feature dict from extract_features.
            
        Returns:
            Numpy array of features.
        """
        if not features:
            return None
        
        vector = [
            features['duration'],
            features['rms_mean'],
            features['rms_std'],
            features['spectral_centroid_mean'],
            features['spectral_centroid_std'],
            features['zcr_mean'],
            features['zcr_std'],
        ]
        
        # Add MFCCs
        vector.extend(features['mfcc_means'])
        vector.extend(features['mfcc_stds'])
        
        return np.array(vector)
