from flask import Blueprint, request, jsonify, send_file
import io
from services.data_service import get_all_data, WB_DISTRICTS, CROP_DATA
from services.ml_service import recommend_crops, predict_yield, assess_pest_risk, train_models
from services.report_service import generate_farm_report

report_bp = Blueprint('report', __name__)

@report_bp.route('/generate', methods=['POST'])
def generate_report():
    """Generate a comprehensive PDF farm report."""
    data = request.json or {}

    farmer_data = {
        "name": data.get("farmer_name", "Unknown Farmer"),
        "village": data.get("village", "N/A"),
        "district": data.get("district", "Bardhaman"),
        "land_ha": data.get("land_ha", 1.0),
        "primary_crop": data.get("primary_crop", "Rice (Aman)"),
        "irrigation": data.get("irrigation", "Canal/Tubewell"),
    }

    district = farmer_data["district"]
    all_data = get_all_data(district)
    weather = all_data["weather"]
    market_prices = all_data["market_prices"]
    advisory = all_data["advisory"]
    schemes = all_data["schemes"]

    # Run ML models
    soil_N = float(data.get("soil_N", 70))
    soil_P = float(data.get("soil_P", 35))
    soil_K = float(data.get("soil_K", 40))
    soil_pH = float(data.get("soil_pH", 6.0))
    temperature = weather["temp_max"]
    rainfall = weather["rainfall_mm"]
    humidity = weather["humidity_pct"]
    season_map = {"kharif": 0, "rabi": 1, "zaid": 2}
    season = season_map.get(data.get("season", "kharif"), 0)
    primary_crop = farmer_data["primary_crop"]

    recommendations = recommend_crops(soil_N, soil_P, soil_K, soil_pH,
                                      temperature, rainfall, humidity, season)
    irrigation_flag = 1 if farmer_data["irrigation"].lower() != "none" else 0
    yield_pred = predict_yield(primary_crop, soil_N, soil_P, soil_K, soil_pH,
                                temperature, rainfall, humidity, irrigation_flag)
    pest_risk = assess_pest_risk(primary_crop, temperature, humidity, rainfall)

    ml_results = {
        "recommendations": recommendations,
        "yield_prediction": yield_pred,
        "pest_risk": pest_risk
    }

    try:
        pdf_bytes = generate_farm_report(
            farmer_data, weather, market_prices, advisory, ml_results, schemes
        )
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"KVK_Report_{farmer_data['name'].replace(' ','_')}.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/preview', methods=['POST'])
def preview_report():
    """Return JSON data that would go into report (for dashboard preview)."""
    data = request.json or {}
    district = data.get("district", "Bardhaman")
    all_data = get_all_data(district)
    weather = all_data["weather"]

    soil_N = float(data.get("soil_N", 70))
    soil_P = float(data.get("soil_P", 35))
    soil_K = float(data.get("soil_K", 40))
    soil_pH = float(data.get("soil_pH", 6.0))
    temperature = weather["temp_max"]
    rainfall = weather["rainfall_mm"]
    humidity = weather["humidity_pct"]
    season_map = {"kharif": 0, "rabi": 1, "zaid": 2}
    season = season_map.get(data.get("season", "kharif"), 0)
    primary_crop = data.get("primary_crop", "Rice (Aman)")
    irrigation_flag = 1 if data.get("irrigation", "Canal") != "None" else 0

    recommendations = recommend_crops(soil_N, soil_P, soil_K, soil_pH,
                                      temperature, rainfall, humidity, season)
    yield_pred = predict_yield(primary_crop, soil_N, soil_P, soil_K, soil_pH,
                                temperature, rainfall, humidity, irrigation_flag)
    pest_risk = assess_pest_risk(primary_crop, temperature, humidity, rainfall)

    return jsonify({
        "weather": weather,
        "market_prices": all_data["market_prices"][:6],
        "advisory": all_data["advisory"],
        "schemes": all_data["schemes"][:3],
        "ml": {
            "recommendations": recommendations,
            "yield_prediction": yield_pred,
            "pest_risk": pest_risk
        }
    })

@report_bp.route('/train', methods=['POST'])
def train():
    """Endpoint to retrain ML models."""
    result = train_models()
    return jsonify({"message": "Models trained successfully", "metrics": result})

@report_bp.route('/districts', methods=['GET'])
def get_districts():
    return jsonify({"districts": WB_DISTRICTS})

@report_bp.route('/crops', methods=['GET'])
def get_crops():
    return jsonify({"crops": list(CROP_DATA.keys())})
