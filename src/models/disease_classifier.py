"""
Binary Disease Classifier for Potato Shield
Uses pre-trained ML model for Early Blight vs Late Blight classification based on weather data.

This serves as a secondary validation layer to ensure consistent, reliable disease predictions.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import os
from typing import Dict, Tuple, Optional

# Try to import sklearn, but handle gracefully if not installed
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("[CLASSIFIER] scikit-learn not installed. Disease classifier will not be available.")


class DiseaseClassifier:
    """
    Binary classifier for Early Blight vs Late Blight.
    
    Features:
    - Temperature (°C)
    - Humidity (%)
    - Wind Speed (km/h)
    - Wind Bearing (degrees)
    - Visibility (km)
    - Pressure (hPa)
    
    Output:
    - 0: Late Blight
    - 1: Early Blight
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize classifier.
        
        Args:
            model_path: Path to saved model file. If None, will train new model.
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for disease classifier")
        
        self.model = None
        self.scaler = None
        self.model_accuracy = None  # Store model accuracy
        self.model_metrics = None  # Store all metrics
        self.feature_names = [
            'Temperature', 'Humidity', 'Wind Speed', 
            'Wind Bearing', 'Visibility', 'Pressure'
        ]
        
        # Try to load pre-trained model
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            # Train model on CSV data
            csv_path = Path(__file__).parent.parent / "new" / "Disease with Weather.csv"
            if csv_path.exists():
                print("[CLASSIFIER] Training disease classifier from CSV data...")
                metrics = self.train_from_csv(str(csv_path))
                self.model_accuracy = metrics.get('accuracy', None)
                self.model_metrics = metrics
            else:
                print(f"[CLASSIFIER] Warning: Training data not found at {csv_path}")
    
    def train_from_csv(self, csv_path: str) -> Dict:
        """
        Train the classifier from CSV data.
        
        Args:
            csv_path: Path to training CSV file
            
        Returns:
            Dict with training metrics
        """
        # Load data
        df = pd.read_csv(csv_path)
        
        # Prepare features and labels
        X = df[self.feature_names].values
        y = df['Disease in number'].values  # 0 = Late Blight, 1 = Early Blight
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train ensemble model (Random Forest + Gradient Boosting for robustness)
        # Use Random Forest as primary (more stable, less prone to overfitting)
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'  # Handle any class imbalance
        )
        
        # Train
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted'),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        print(f"[CLASSIFIER] Model trained successfully!")
        print(f"[CLASSIFIER] Accuracy: {metrics['accuracy']:.3f}")
        print(f"[CLASSIFIER] F1 Score: {metrics['f1_score']:.3f}")
        print(f"[CLASSIFIER] Training samples: {metrics['training_samples']}")
        
        return metrics
    
    def predict(self, weather_data: Dict) -> Tuple[str, float, Dict]:
        """
        Predict disease type from weather data.
        
        Args:
            weather_data: Dict with keys: Temperature, Humidity, Wind Speed, 
                         Wind Bearing, Visibility, Pressure
        
        Returns:
            Tuple of (disease_name, confidence, probabilities_dict)
            - disease_name: "Early Blight" or "Late Blight"
            - confidence: float 0-1
            - probabilities_dict: {"late_blight": float, "early_blight": float}
        """
        if not self.model or not self.scaler:
            return "Unknown", 0.5, {"late_blight": 0.5, "early_blight": 0.5}
        
        try:
            # Extract features in correct order
            features = []
            for feat in self.feature_names:
                value = weather_data.get(feat, weather_data.get(feat.lower(), 0))
                features.append(float(value))
            
            # Prepare input
            X = np.array([features])
            X_scaled = self.scaler.transform(X)
            
            # Predict
            prediction = self.model.predict(X_scaled)[0]
            probabilities = self.model.predict_proba(X_scaled)[0]
            
            # Convert to labels
            disease_name = "Early Blight" if prediction == 1 else "Late Blight"
            confidence = float(probabilities[prediction])
            
            result = {
                "late_blight": float(probabilities[0]),
                "early_blight": float(probabilities[1])
            }
            
            return disease_name, confidence, result
            
        except Exception as e:
            print(f"[CLASSIFIER] Prediction error: {e}")
            return "Unknown", 0.5, {"late_blight": 0.5, "early_blight": 0.5}
    
    def validate_prediction(
        self, 
        weather_data: Dict, 
        current_prediction: Dict
    ) -> Dict:
        """
        Validate and potentially adjust current prediction using ML classifier.
        
        This serves as a secondary validation to ensure predictions are consistent
        with trained patterns from historical data.
        
        Args:
            weather_data: Current weather conditions
            current_prediction: Current blight prediction from rule-based system
            
        Returns:
            Dict with validation results and potentially adjusted prediction
        """
        # Get ML classifier prediction
        ml_disease, ml_confidence, ml_probabilities = self.predict(weather_data)
        
        # Extract current predictions
        current_late_blight = current_prediction.get("late_blight_risk", {}).get("risk_percentage", 0)
        current_early_blight = current_prediction.get("early_blight_risk", {}).get("risk_percentage", 0)
        
        # Check for agreement
        ml_late_prob = ml_probabilities["late_blight"] * 100  # Convert to percentage
        ml_early_prob = ml_probabilities["early_blight"] * 100
        
        # Calculate disagreement score
        late_blight_diff = abs(current_late_blight - ml_late_prob)
        early_blight_diff = abs(current_early_blight - ml_early_prob)
        avg_disagreement = (late_blight_diff + early_blight_diff) / 2
        
        # If significant disagreement (>20%), use weighted average
        if avg_disagreement > 20:
            # Weight: 60% current (domain-specific rules), 40% ML (data-driven)
            adjusted_late = (current_late_blight * 0.6) + (ml_late_prob * 0.4)
            adjusted_early = (current_early_blight * 0.6) + (ml_early_prob * 0.4)
            
            return {
                "validated": True,
                "adjustment_made": True,
                "disagreement_score": avg_disagreement,
                "ml_prediction": {
                    "disease": ml_disease,
                    "confidence": ml_confidence,
                    "late_blight": ml_late_prob,
                    "early_blight": ml_early_prob
                },
                "adjusted_prediction": {
                    "late_blight": adjusted_late,
                    "early_blight": adjusted_early
                },
                "model_accuracy": self.model_accuracy,
                "model_metrics": self.model_metrics,
                "recommendation": f"ML model suggests {ml_disease} with {ml_confidence:.1%} confidence. Adjusted predictions for consistency."
            }
        else:
            # Predictions agree - no adjustment needed
            return {
                "validated": True,
                "adjustment_made": False,
                "disagreement_score": avg_disagreement,
                "ml_prediction": {
                    "disease": ml_disease,
                    "confidence": ml_confidence,
                    "late_blight": ml_late_prob,
                    "early_blight": ml_early_prob
                },
                "model_accuracy": self.model_accuracy,
                "model_metrics": self.model_metrics,
                "recommendation": f"ML validation confirms current prediction. {ml_disease} detected with {ml_confidence:.1%} confidence."
            }
    
    def save_model(self, path: str):
        """Save trained model to disk."""
        if not self.model or not self.scaler:
            raise ValueError("No model to save. Train the model first.")
        
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'accuracy': self.model_accuracy,
                'metrics': self.model_metrics
            }, f)
        print(f"[CLASSIFIER] Model saved to {path}")
        if self.model_accuracy:
            print(f"[CLASSIFIER] Saved with accuracy: {self.model_accuracy:.3f}")
    
    def load_model(self, path: str):
        """Load trained model from disk."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data.get('feature_names', self.feature_names)
            self.model_accuracy = data.get('accuracy', None)
            self.model_metrics = data.get('metrics', None)
        print(f"[CLASSIFIER] Model loaded from {path}")
        if self.model_accuracy:
            print(f"[CLASSIFIER] Model Accuracy: {self.model_accuracy:.3f}")


# Global classifier instance
_classifier = None

def get_disease_classifier() -> Optional[DiseaseClassifier]:
    """
    Get or create global disease classifier instance.
    
    Returns:
        DiseaseClassifier instance or None if sklearn not available
    """
    global _classifier
    
    if not SKLEARN_AVAILABLE:
        return None
    
    if _classifier is None:
        try:
            # Try to load from models directory
            model_path = Path(__file__).parent / "disease_classifier.pkl"
            
            if model_path.exists():
                _classifier = DiseaseClassifier(model_path=str(model_path))
            else:
                # Train new model from CSV
                _classifier = DiseaseClassifier()
                # Save for future use
                if _classifier.model:
                    _classifier.save_model(str(model_path))
        except Exception as e:
            print(f"[CLASSIFIER] Error initializing classifier: {e}")
            _classifier = None
    
    return _classifier

