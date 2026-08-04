from flask import Blueprint, request, jsonify
from services.data_service import (
    get_mock_weather, get_market_prices, get_advisory,
    get_all_data, WB_DISTRICTS, SCHEMES, CROP_DATA
)

data_bp = Blueprint('data', __name__)

@data_bp.route('/weather', methods=['GET'])
def weather():
    district = request.args.get('district', 'Bardhaman')
    return jsonify(get_mock_weather(district))

@data_bp.route('/market', methods=['GET'])
def market():
    district = request.args.get('district', 'Bardhaman')
    return jsonify({"prices": get_market_prices(district)})

@data_bp.route('/advisory', methods=['GET'])
def advisory():
    district = request.args.get('district', 'Bardhaman')
    crop = request.args.get('crop', None)
    return jsonify(get_advisory(district, crop))

@data_bp.route('/schemes', methods=['GET'])
def schemes():
    return jsonify({"schemes": SCHEMES})

@data_bp.route('/districts', methods=['GET'])
def districts():
    return jsonify({"districts": WB_DISTRICTS})

@data_bp.route('/crops', methods=['GET'])
def crops():
    return jsonify({"crops": list(CROP_DATA.keys()), "details": CROP_DATA})

@data_bp.route('/dashboard', methods=['GET'])
def dashboard():
    district = request.args.get('district', 'Bardhaman')
    return jsonify(get_all_data(district))
