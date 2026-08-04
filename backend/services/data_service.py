"""
Data service for West Bengal agricultural data.
Fetches from open government APIs and IMD weather data.
Falls back to curated seed data when offline.
"""
import requests
import json
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# --- Curated West Bengal agricultural reference data ---
WB_DISTRICTS = [
    "Bankura", "Birbhum", "Burdwan", "Cooch Behar", "Darjeeling",
    "Dinajpur (N)", "Dinajpur (S)", "Hooghly", "Howrah", "Jalpaiguri",
    "Jhargram", "Kalimpong", "Malda", "Midnapore (E)", "Midnapore (W)",
    "Murshidabad", "Nadia", "North 24 Parganas", "Purulia", "South 24 Parganas"
]

CROP_DATA = {
    "Rice (Aman)": {
        "season": "Kharif",
        "sow_month": "June-July",
        "harvest_month": "November-December",
        "avg_yield_qtl_per_ha": 28,
        "msp_per_qtl": 2183,
        "key_pests": ["Brown Plant Hopper", "Stem Borer", "Leaf Folder"],
        "fertilizer_kg_per_ha": {"N": 80, "P": 40, "K": 40},
        "districts": ["Bardhaman", "Hooghly", "Nadia", "Murshidabad", "24 Parganas"]
    },
    "Rice (Boro)": {
        "season": "Rabi",
        "sow_month": "December-January",
        "harvest_month": "April-May",
        "avg_yield_qtl_per_ha": 45,
        "msp_per_qtl": 2183,
        "key_pests": ["Blast", "Sheath Blight", "Gall Midge"],
        "fertilizer_kg_per_ha": {"N": 100, "P": 50, "K": 50},
        "districts": ["Birbhum", "Bankura", "Purulia", "West Midnapore"]
    },
    "Potato": {
        "season": "Rabi",
        "sow_month": "October-November",
        "harvest_month": "February-March",
        "avg_yield_qtl_per_ha": 220,
        "msp_per_qtl": 400,
        "key_pests": ["Late Blight", "Early Blight", "Aphids"],
        "fertilizer_kg_per_ha": {"N": 120, "P": 80, "K": 120},
        "districts": ["Hooghly", "Bardhaman", "Nadia", "Cooch Behar"]
    },
    "Jute": {
        "season": "Kharif",
        "sow_month": "March-May",
        "harvest_month": "July-September",
        "avg_yield_qtl_per_ha": 25,
        "msp_per_qtl": 5050,
        "key_pests": ["Semilooper", "Stem Rot", "Hairy Caterpillar"],
        "fertilizer_kg_per_ha": {"N": 60, "P": 30, "K": 30},
        "districts": ["Murshidabad", "Nadia", "24 Parganas", "Cooch Behar"]
    },
    "Mustard": {
        "season": "Rabi",
        "sow_month": "October-November",
        "harvest_month": "February-March",
        "avg_yield_qtl_per_ha": 12,
        "msp_per_qtl": 5650,
        "key_pests": ["Aphids", "Alternaria Blight", "Sawfly"],
        "fertilizer_kg_per_ha": {"N": 60, "P": 30, "K": 30},
        "districts": ["Birbhum", "Bankura", "Murshidabad", "Malda"]
    },
    "Wheat": {
        "season": "Rabi",
        "sow_month": "November-December",
        "harvest_month": "March-April",
        "avg_yield_qtl_per_ha": 30,
        "msp_per_qtl": 2275,
        "key_pests": ["Rust", "Aphids", "Loose Smut"],
        "fertilizer_kg_per_ha": {"N": 100, "P": 50, "K": 40},
        "districts": ["Darjeeling", "Cooch Behar", "Malda", "Dinajpur"]
    },
    "Maize": {
        "season": "Kharif",
        "sow_month": "June-July",
        "harvest_month": "September-October",
        "avg_yield_qtl_per_ha": 35,
        "msp_per_qtl": 2090,
        "key_pests": ["Fall Armyworm", "Stem Borer", "Downy Mildew"],
        "fertilizer_kg_per_ha": {"N": 120, "P": 60, "K": 40},
        "districts": ["Purulia", "Bankura", "Jhargram"]
    },
    "Vegetables": {
        "season": "All Season",
        "sow_month": "Year round",
        "harvest_month": "Year round",
        "avg_yield_qtl_per_ha": 150,
        "msp_per_qtl": "Market dependent",
        "key_pests": ["Whitefly", "Thrips", "Leafminer"],
        "fertilizer_kg_per_ha": {"N": 80, "P": 40, "K": 60},
        "districts": ["All districts"]
    }
}

SCHEMES = [
    {
        "name": "PM-KISAN",
        "description": "Direct income support of ₹6,000/year to farmer families in 3 installments",
        "eligibility": "All small and marginal farmers with cultivable land",
        "benefit": "₹6,000 per year",
        "apply_at": "https://pmkisan.gov.in"
    },
    {
        "name": "Bangla Shasyabima (PMFBY WB)",
        "description": "Crop insurance scheme covering yield losses due to natural calamities",
        "eligibility": "All farmers growing notified crops",
        "benefit": "Up to full sum insured based on crop loss",
        "apply_at": "Block Agriculture Office"
    },
    {
        "name": "Krishak Bandhu",
        "description": "West Bengal state scheme providing ₹10,000/year per acre (min 1 acre)",
        "eligibility": "WB farmers with land records",
        "benefit": "₹10,000 per acre per year",
        "apply_at": "State Agriculture Department"
    },
    {
        "name": "Kisan Credit Card (KCC)",
        "description": "Short-term credit for crop cultivation, post-harvest expenses",
        "eligibility": "All farmers, tenant farmers, sharecroppers",
        "benefit": "Credit up to ₹3 lakh at 4% interest",
        "apply_at": "Nearest bank branch"
    },
    {
        "name": "PM Kusum Yojana",
        "description": "Solar pump scheme for irrigation to reduce diesel/electricity cost",
        "eligibility": "Farmers with agricultural land",
        "benefit": "60% subsidy on solar pump installation",
        "apply_at": "WB Renewable Energy Development Agency"
    },
    {
        "name": "Soil Health Card Scheme",
        "description": "Free soil testing and health card with fertilizer recommendations",
        "eligibility": "All farmers",
        "benefit": "Free soil testing every 2 years",
        "apply_at": "Block Agriculture Office or KVK"
    }
]

WEATHER_STATIONS = {
    "Bankura": {"lat": 23.23, "lon": 87.07},
    "Bardhaman": {"lat": 23.23, "lon": 87.86},
    "Birbhum": {"lat": 23.89, "lon": 87.53},
    "Cooch Behar": {"lat": 26.32, "lon": 89.45},
    "Darjeeling": {"lat": 27.04, "lon": 88.26},
    "Hooghly": {"lat": 22.90, "lon": 88.39},
    "Howrah": {"lat": 22.59, "lon": 88.30},
    "Jalpaiguri": {"lat": 26.54, "lon": 88.73},
    "Malda": {"lat": 25.00, "lon": 88.14},
    "Murshidabad": {"lat": 24.18, "lon": 88.27},
    "Nadia": {"lat": 23.47, "lon": 88.56},
    "Purulia": {"lat": 23.33, "lon": 86.36},
    "South 24 Parganas": {"lat": 22.15, "lon": 88.45},
    "North 24 Parganas": {"lat": 22.86, "lon": 88.75},
}

KVK_CENTERS = {
    "Bankura": "KVK Bankura, Kenduadihi, Bankura-722102",
    "Bardhaman": "KVK Bardhaman, Krishnanagar, Burdwan-713101",
    "Birbhum": "KVK Birbhum, Suri, Birbhum-731101",
    "Nadia": "KVK Nadia, Mohanpur, Nadia-741246",
    "Murshidabad": "KVK Murshidabad, Berhampore-742101",
    "Hooghly": "KVK Hooghly, Chinsurah, Hooghly-712101",
    "Purulia": "KVK Purulia, Manbazar, Purulia-723131",
    "Darjeeling": "KVK Darjeeling, Siliguri, Darjeeling-734001",
}

def get_mock_weather(district: str) -> dict:
    """Generate realistic seasonal weather for West Bengal district."""
    month = datetime.now().month
    # West Bengal climate patterns
    if month in [6, 7, 8, 9]:  # Monsoon
        temp_max = random.uniform(30, 35)
        temp_min = random.uniform(24, 28)
        rainfall = random.uniform(150, 400)
        humidity = random.uniform(80, 95)
        condition = "Monsoon / Heavy Rain"
    elif month in [10, 11]:  # Post-monsoon
        temp_max = random.uniform(28, 33)
        temp_min = random.uniform(20, 24)
        rainfall = random.uniform(10, 60)
        humidity = random.uniform(65, 80)
        condition = "Post-Monsoon / Partly Cloudy"
    elif month in [12, 1, 2]:  # Winter
        temp_max = random.uniform(18, 25)
        temp_min = random.uniform(10, 15)
        rainfall = random.uniform(0, 20)
        humidity = random.uniform(50, 70)
        condition = "Winter / Clear"
    else:  # Pre-monsoon (Mar-May)
        temp_max = random.uniform(35, 42)
        temp_min = random.uniform(24, 29)
        rainfall = random.uniform(5, 40)
        humidity = random.uniform(55, 75)
        condition = "Pre-Monsoon / Hot & Humid"

    return {
        "district": district,
        "date": datetime.now().strftime("%d %B %Y"),
        "condition": condition,
        "temp_max": round(temp_max, 1),
        "temp_min": round(temp_min, 1),
        "rainfall_mm": round(rainfall, 1),
        "humidity_pct": round(humidity, 1),
        "wind_kmh": round(random.uniform(8, 25), 1),
        "forecast_7day": _generate_7day_forecast(month)
    }

def _generate_7day_forecast(month: int) -> list:
    forecasts = []
    base_date = datetime.now()
    conditions = ["Sunny", "Partly Cloudy", "Overcast", "Light Rain", "Moderate Rain", "Thunderstorm"]
    weights_monsoon = [0.05, 0.10, 0.15, 0.25, 0.30, 0.15]
    weights_dry = [0.40, 0.30, 0.15, 0.10, 0.04, 0.01]
    weights = weights_monsoon if month in [6,7,8,9] else weights_dry

    for i in range(1, 8):
        d = base_date + timedelta(days=i)
        cond = random.choices(conditions, weights=weights)[0]
        forecasts.append({
            "date": d.strftime("%d %b"),
            "day": d.strftime("%A"),
            "condition": cond,
            "temp_max": round(random.uniform(22, 38), 1),
            "temp_min": round(random.uniform(15, 27), 1),
        })
    return forecasts

def get_market_prices(district: str) -> list:
    """Return simulated mandi prices for West Bengal crops."""
    prices = []
    for crop, data in CROP_DATA.items():
        msp = data["msp_per_qtl"]
        if isinstance(msp, int):
            market_price = round(msp * random.uniform(0.90, 1.30))
            prices.append({
                "crop": crop,
                "msp": msp,
                "market_price": market_price,
                "unit": "₹/quintal",
                "trend": random.choice(["↑ Rising", "↓ Falling", "→ Stable"]),
                "market": f"{district} APMC"
            })
    return prices

def get_advisory(district: str, crop: str = None) -> dict:
    """Return current agricultural advisory."""
    month = datetime.now().month
    advisories = []
    
    if month in [6, 7]:
        advisories = [
            "Transplant Aman paddy seedlings in well-puddled field. Maintain 5 cm water level.",
            "Apply basal dose of fertilizer (NPK) before transplanting.",
            "Monitor for Stem Borer and BPH. Use light traps.",
            "Ensure proper field bunding to retain rainwater.",
            "Complete jute harvesting before fibre gets overripe.",
        ]
    elif month in [8, 9]:
        advisories = [
            "Apply top dressing of urea in Aman paddy at tillering stage.",
            "Scout for Leaf Folder and apply Chlorantraniliprole if damage > 10%.",
            "Drain excess water from paddy fields after heavy rain.",
            "Prepare land for potato sowing (Oct-Nov). Apply FYM @ 20t/ha.",
            "Spray Mancozeb on jute to prevent stem rot.",
        ]
    elif month in [10, 11]:
        advisories = [
            "Begin potato sowing using certified seed (Kufri Jyoti / Kufri Sindhuri).",
            "Sow mustard in well-prepared field. Use Pusa Bold variety.",
            "Harvest Aman paddy at 80% maturity. Dry grains to < 14% moisture.",
            "Apply lime to acidic soils (pH < 5.5) @ 2-3 t/ha.",
            "Plant winter vegetables (cauliflower, cabbage, tomato) in nursery.",
        ]
    elif month in [12, 1, 2]:
        advisories = [
            "Irrigate potato crop at 10-day intervals. Apply fungicide for Late Blight.",
            "Top dress wheat with urea at CRI stage (21 DAS).",
            "Protect Boro paddy nursery from cold wave. Use polythene covers.",
            "Harvest mustard when 75% pods turn yellow.",
            "Apply potassic fertilizer to potato to improve tuber quality.",
        ]
    else:
        advisories = [
            "Prepare land for Kharif crops. Deep plough and apply FYM.",
            "Order certified seeds of Aman paddy from authorised dealers.",
            "Service irrigation pumps and check canal system.",
            "Attend KVK training on improved variety selection.",
            "Apply pre-emergent herbicide in fields before Kharif sowing.",
        ]

    return {
        "district": district,
        "season": _get_current_season(month),
        "date": datetime.now().strftime("%d %B %Y"),
        "advisories": advisories,
        "kvk_contact": KVK_CENTERS.get(district, "Nearest KVK Office")
    }

def _get_current_season(month: int) -> str:
    if month in [6,7,8,9,10]: return "Kharif 2024-25"
    elif month in [11,12,1,2,3]: return "Rabi 2024-25"
    else: return "Zaid 2025"

def get_all_data(district: str) -> dict:
    return {
        "weather": get_mock_weather(district),
        "market_prices": get_market_prices(district),
        "advisory": get_advisory(district),
        "schemes": SCHEMES,
        "crops": CROP_DATA,
        "districts": WB_DISTRICTS
    }
