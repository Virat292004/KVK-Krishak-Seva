"""
ML Model Service for KVK Farmer App
- Crop recommendation using RandomForest
- Yield prediction using Gradient Boosting
- Pest risk assessment
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import random

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

CROP_ENCODER_PATH = os.path.join(MODEL_DIR, 'crop_encoder.pkl')
CROP_MODEL_PATH = os.path.join(MODEL_DIR, 'crop_recommender.pkl')
YIELD_MODEL_PATH = os.path.join(MODEL_DIR, 'yield_predictor.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')

CROPS = [
    "Rice (Aman)", "Rice (Boro)", "Potato", "Jute",
    "Mustard", "Wheat", "Maize", "Vegetables"
]

def _generate_training_data(n=3000):
    """Generate synthetic but agronomically realistic training data for WB."""
    random.seed(42)
    np.random.seed(42)
    rows = []

    crop_profiles = {
        "Rice (Aman)": {"N": (60,100), "P": (30,50), "K": (30,50), "pH": (5.5,6.5),
                        "temp": (25,35), "rain": (150,350), "humidity": (75,95), "season": 0},
        "Rice (Boro)": {"N": (80,120), "P": (40,60), "K": (40,60), "pH": (5.5,6.5),
                        "temp": (18,28), "rain": (20,80), "humidity": (60,80), "season": 1},
        "Potato":      {"N": (100,140), "P": (60,100), "K": (100,140), "pH": (5.0,6.0),
                        "temp": (15,25), "rain": (30,100), "humidity": (55,75), "season": 1},
        "Jute":        {"N": (50,80), "P": (20,40), "K": (20,40), "pH": (6.0,7.5),
                        "temp": (25,38), "rain": (100,300), "humidity": (70,90), "season": 0},
        "Mustard":     {"N": (40,80), "P": (20,40), "K": (20,40), "pH": (6.0,7.5),
                        "temp": (15,25), "rain": (10,60), "humidity": (50,70), "season": 1},
        "Wheat":       {"N": (80,120), "P": (40,60), "K": (30,50), "pH": (6.0,7.5),
                        "temp": (12,22), "rain": (20,70), "humidity": (45,65), "season": 1},
        "Maize":       {"N": (100,140), "P": (50,80), "K": (30,50), "pH": (5.5,7.0),
                        "temp": (22,32), "rain": (60,180), "humidity": (60,80), "season": 0},
        "Vegetables":  {"N": (60,100), "P": (30,60), "K": (40,80), "pH": (5.5,7.0),
                        "temp": (15,30), "rain": (20,150), "humidity": (55,80), "season": 2},
    }

    for crop, p in crop_profiles.items():
        for _ in range(n // len(crop_profiles)):
            rows.append({
                "N": np.random.uniform(*p["N"]) + np.random.normal(0, 8),
                "P": np.random.uniform(*p["P"]) + np.random.normal(0, 5),
                "K": np.random.uniform(*p["K"]) + np.random.normal(0, 5),
                "pH": np.clip(np.random.uniform(*p["pH"]) + np.random.normal(0, 0.2), 4.5, 8.0),
                "temperature": np.random.uniform(*p["temp"]) + np.random.normal(0, 1.5),
                "rainfall": np.random.uniform(*p["rain"]) + np.random.normal(0, 15),
                "humidity": np.clip(np.random.uniform(*p["humidity"]) + np.random.normal(0, 3), 30, 100),
                "season": p["season"],  # 0=kharif, 1=rabi, 2=all
                "crop": crop
            })

    return pd.DataFrame(rows)

def _generate_yield_data(n=2000):
    """Synthetic yield training data."""
    np.random.seed(42)
    rows = []
    for crop in CROPS:
        base_yields = {
            "Rice (Aman)": 28, "Rice (Boro)": 45, "Potato": 220,
            "Jute": 25, "Mustard": 12, "Wheat": 30,
            "Maize": 35, "Vegetables": 150
        }
        base = base_yields.get(crop, 30)
        for _ in range(n // len(CROPS)):
            N = np.random.uniform(40, 140)
            rain = np.random.uniform(20, 350)
            temp = np.random.uniform(12, 38)
            humidity = np.random.uniform(45, 95)
            pH = np.random.uniform(5.0, 7.5)
            irrigation = np.random.choice([0, 1], p=[0.3, 0.7])

            # Yield influenced by inputs
            yield_val = (
                base
                + 0.05 * N
                + 0.01 * rain
                - 0.2 * abs(temp - 25)
                - 0.1 * abs(pH - 6.2)
                + 5 * irrigation
                + np.random.normal(0, base * 0.1)
            )
            yield_val = max(yield_val, base * 0.4)

            rows.append({
                "crop": crop,
                "N": N,
                "P": np.random.uniform(20, 100),
                "K": np.random.uniform(20, 140),
                "pH": pH,
                "temperature": temp,
                "rainfall": rain,
                "humidity": humidity,
                "irrigation": irrigation,
                "yield_qtl_per_ha": round(yield_val, 2)
            })
    return pd.DataFrame(rows)

def train_models():
    """Train and save both ML models."""
    print("Training crop recommendation model...")
    df_crop = _generate_training_data()
    le = LabelEncoder()
    df_crop['crop_enc'] = le.fit_transform(df_crop['crop'])

    features = ["N", "P", "K", "pH", "temperature", "rainfall", "humidity", "season"]
    X = df_crop[features]
    y = df_crop['crop_enc']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    acc = clf.score(X_test, y_test)
    print(f"  Crop model accuracy: {acc:.2%}")

    print("Training yield prediction model...")
    df_yield = _generate_yield_data()
    le2 = LabelEncoder()
    df_yield['crop_enc'] = le2.fit_transform(df_yield['crop'])
    features2 = ["crop_enc", "N", "P", "K", "pH", "temperature", "rainfall", "humidity", "irrigation"]
    X2 = df_yield[features2]
    y2 = df_yield['yield_qtl_per_ha']

    X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y2, test_size=0.2, random_state=42)
    gb = GradientBoostingRegressor(n_estimators=200, max_depth=5, learning_rate=0.05, random_state=42)
    gb.fit(X2_train, y2_train)
    r2 = gb.score(X2_test, y2_test)
    print(f"  Yield model R²: {r2:.4f}")

    joblib.dump(le, CROP_ENCODER_PATH)
    joblib.dump(clf, CROP_MODEL_PATH)
    joblib.dump(gb, YIELD_MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(le2, os.path.join(MODEL_DIR, 'yield_crop_encoder.pkl'))
    print("Models saved successfully.")
    return {"crop_accuracy": round(acc, 4), "yield_r2": round(r2, 4)}

def _load_models():
    if not os.path.exists(CROP_MODEL_PATH):
        train_models()
    le = joblib.load(CROP_ENCODER_PATH)
    clf = joblib.load(CROP_MODEL_PATH)
    gb = joblib.load(YIELD_MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    le2 = joblib.load(os.path.join(MODEL_DIR, 'yield_crop_encoder.pkl'))
    return le, clf, gb, scaler, le2

def recommend_crops(soil_N, soil_P, soil_K, soil_pH, temperature, rainfall, humidity, season=0):
    """Return top 3 crop recommendations with probabilities."""
    le, clf, _, scaler, _ = _load_models()
    X = np.array([[soil_N, soil_P, soil_K, soil_pH, temperature, rainfall, humidity, season]])
    X_scaled = scaler.transform(X)
    probs = clf.predict_proba(X_scaled)[0]
    top3_idx = np.argsort(probs)[::-1][:3]
    results = []
    for idx in top3_idx:
        results.append({
            "crop": le.classes_[idx],
            "confidence": round(float(probs[idx]) * 100, 1)
        })
    return results

def predict_yield(crop, soil_N, soil_P, soil_K, soil_pH, temperature, rainfall, humidity, irrigation=1):
    """Predict yield in quintals per hectare."""
    _, _, gb, _, le2 = _load_models()
    if crop not in le2.classes_:
        return {"error": "Crop not found in model"}
    crop_enc = le2.transform([crop])[0]
    X = np.array([[crop_enc, soil_N, soil_P, soil_K, soil_pH, temperature, rainfall, humidity, irrigation]])
    predicted = gb.predict(X)[0]
    return {
        "crop": crop,
        "predicted_yield_qtl_per_ha": round(predicted, 2),
        "predicted_yield_kg_per_ha": round(predicted * 100, 0)
    }

def assess_pest_risk(crop, temperature, humidity, rainfall) -> dict:
    """Rule-based pest risk assessment."""
    risks = []
    
    pest_rules = {
        "Rice (Aman)": [
            {"pest": "Brown Plant Hopper", "condition": humidity > 85 and temperature > 28, "risk": "High"},
            {"pest": "Stem Borer", "condition": temperature > 25 and rainfall < 100, "risk": "Medium"},
            {"pest": "Leaf Folder", "condition": humidity > 80, "risk": "Medium"},
            {"pest": "Blast", "condition": humidity > 85 and temperature < 26, "risk": "High"},
        ],
        "Potato": [
            {"pest": "Late Blight", "condition": humidity > 80 and temperature < 20, "risk": "High"},
            {"pest": "Early Blight", "condition": temperature > 25 and humidity < 70, "risk": "Medium"},
            {"pest": "Aphids", "condition": temperature < 18 and humidity < 65, "risk": "Medium"},
        ],
        "Mustard": [
            {"pest": "Aphids", "condition": temperature < 20 and humidity < 65, "risk": "High"},
            {"pest": "Alternaria Blight", "condition": humidity > 70, "risk": "Medium"},
        ],
        "Wheat": [
            {"pest": "Yellow Rust", "condition": temperature < 15 and humidity > 75, "risk": "High"},
            {"pest": "Aphids", "condition": temperature < 18, "risk": "Medium"},
        ],
        "Maize": [
            {"pest": "Fall Armyworm", "condition": temperature > 25 and humidity > 70, "risk": "High"},
            {"pest": "Stem Borer", "condition": temperature > 28, "risk": "Medium"},
        ],
    }
    
    rules = pest_rules.get(crop, [])
    for rule in rules:
        level = rule["risk"] if rule["condition"] else "Low"
        risks.append({
            "pest": rule["pest"],
            "risk_level": level,
            "recommendation": _get_pest_recommendation(rule["pest"], level)
        })
    
    if not risks:
        risks = [{"pest": "General pests", "risk_level": "Low", 
                  "recommendation": "Regular field monitoring recommended"}]
    
    return {"crop": crop, "pest_risks": risks}

def _get_pest_recommendation(pest: str, level: str) -> str:
    recs = {
        "Brown Plant Hopper": "Apply Imidacloprid 17.8 SL @ 125 ml/ha. Drain water for 7 days.",
        "Stem Borer": "Install pheromone traps @ 5/ha. Apply Chlorantraniliprole 18.5 SC @ 150 ml/ha.",
        "Blast": "Apply Tricyclazole 75 WP @ 300 g/ha. Avoid excess nitrogen.",
        "Late Blight": "Spray Mancozeb 75 WP @ 2 kg/ha. Use resistant varieties (Kufri Jyoti).",
        "Aphids": "Apply Dimethoate 30 EC @ 1 L/ha or use yellow sticky traps.",
        "Fall Armyworm": "Apply Emamectin Benzoate 5 SG @ 220 g/ha. Use Bacillus thuringiensis sprays.",
        "Yellow Rust": "Apply Propiconazole 25 EC @ 500 ml/ha.",
        "Leaf Folder": "Apply Cartap Hydrochloride 50 SP @ 500 g/ha.",
        "Early Blight": "Spray Mancozeb @ 2.5 kg/ha at 10-day intervals.",
        "Alternaria Blight": "Apply Iprodione 50 WP @ 1 kg/ha.",
    }
    if level == "Low":
        return "Monitor weekly. No immediate action needed."
    return recs.get(pest, "Consult your nearest KVK for specific treatment recommendations.")
