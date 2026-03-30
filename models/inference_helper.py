
"""
SahayakAI — Inference Helper (UPDATED WITH CALIBRATED MODEL)
==============================================================
Load trained models and predict dropout risk for Streamlit dashboard.

Usage:
    from inference_helper import predict_dropout_risk, load_model, load_feature_names
    
    # Load once at startup
    model = load_model(use_calibrated=True)  # Prefers calibrated model
    features = load_feature_names()
    
    # Predict for a student
    result = predict_dropout_risk(student_features, model, features)
    print(result["risk_probability"])
    print(result["tier"])
"""

import pickle
import numpy as np
import os

def load_model(path="models/dropout_model.pkl", use_calibrated=True):
    """Load trained model. Prefers calibrated model if available."""
    # Try calibrated first
    if use_calibrated:
        cal_path = "models/dropout_model_calibrated.pkl"
        if os.path.exists(cal_path):
            with open(cal_path, "rb") as f:
                model = pickle.load(f)
            print(f"✅ Using calibrated model: {cal_path}")
            return model
    
    # Fallback to uncalibrated
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Model not found at {path}. Run train_model.py first."
        )
    with open(path, "rb") as f:
        model = pickle.load(f)
    print(f"⚠️  Using uncalibrated model: {path}")
    return model

def load_stress_model(path="models/stress_model.pkl"):
    """Load stress classifier model."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def load_label_encoder(path="models/label_encoder.pkl"):
    """Load label encoder for stress types."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def load_feature_names(path="models/feature_names.pkl"):
    """Load feature names list."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Feature names not found at {path}. Run train_model.py first.")
    with open(path, "rb") as f:
        return pickle.load(f)

def load_tier2_templates(path="data/templates/tier2_messages.json"):
    """Load Tier 2 WhatsApp message templates."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            import json
            return json.load(f)
    return {}

def load_cv_results(path="models/cv_results.json"):
    """Load cross-validation results."""
    if os.path.exists(path):
        with open(path, "r") as f:
            import json
            return json.load(f)
    return None

def predict_dropout_risk(student_features, model=None, feature_names=None):
    """
    Predict dropout risk for a student.
    
    Args:
        student_features: Dict or array-like with feature values
        model: Pre-loaded model (optional, will load calibrated if available)
        feature_names: Pre-loaded feature names (optional, will load if None)
    
    Returns:
        Dictionary with risk_probability, tier, confidence, risk_level
    """
    if model is None:
        model = load_model(use_calibrated=True)
    if feature_names is None:
        feature_names = load_feature_names()
    
    # Convert input to array
    if isinstance(student_features, dict):
        feature_array = np.array([student_features.get(f, 0) for f in feature_names])
    else:
        feature_array = np.array(student_features).reshape(1, -1)
    
    # Predict probability
    risk_probability = model.predict_proba(feature_array)[0, 1]
    
    # Determine tier and confidence
    if risk_probability >= 0.75:
        tier = "Tier 1 — Immediate Visit"
        confidence = "High"
        risk_level = "Critical"
    elif risk_probability >= 0.50:
        tier = "Tier 2 — Digital Check-In"
        confidence = "High"
        risk_level = "Moderate"
    elif risk_probability >= 0.30:
        tier = "Tier 3 — Watch List"
        confidence = "Medium"
        risk_level = "Low"
    else:
        tier = "Tier 4 — Baseline Monitor"
        confidence = "Low"
        risk_level = "Very Low"
    
    return {
        "risk_probability": float(risk_probability),
        "tier": tier,
        "confidence": confidence,
        "risk_level": risk_level
    }

def predict_stress_type(student_features, model=None, label_encoder=None):
    """Predict stress type for at-risk students."""
    if model is None:
        model = load_stress_model()
    if model is None:
        return "Unknown"
    
    if label_encoder is None:
        label_encoder = load_label_encoder()
    
    if isinstance(student_features, dict):
        feature_names = load_feature_names()
        feature_array = np.array([student_features.get(f, 0) for f in feature_names])
    else:
        feature_array = np.array(student_features).reshape(1, -1)
    
    stress_proba = model.predict_proba(feature_array)[0]
    stress_idx = np.argmax(stress_proba)
    
    if label_encoder:
        return label_encoder.inverse_transform([stress_idx])[0]
    return f"Class_{stress_idx}"

def get_intervention_message(student_name, teacher_name, school_name, 
                              pattern="academic_struggle", signal="forum_passive_active_ratio"):
    """Get personalized Tier 2 WhatsApp message."""
    templates = load_tier2_templates()
    
    key = f"tier2_{pattern}_{signal}" if pattern == "academic_struggle" else f"tier2_{pattern}"
    
    if key in templates:
        message = templates[key]
    else:
        message = templates.get("tier2_generic", "Hello! Need any help with studies?")
    
    # Personalize
    message = message.replace("[Student]", student_name)
    message = message.replace("[Teacher]", teacher_name)
    message = message.replace("[School]", school_name)
    
    return message
