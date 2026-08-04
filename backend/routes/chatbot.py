from flask import Blueprint, request, jsonify
import os
try:
    from groq import Groq
except ImportError:
    Groq = None

chatbot_bp = Blueprint('chatbot', __name__)

SYSTEM_PROMPT = """You are KrishiBot, an expert agricultural assistant for the Krishi Vigyan Kendra (KVK) serving farmers in West Bengal, India. 

Your role is to help farmers with:
1. Crop selection, cultivation practices, and agronomic advice
2. Pest and disease identification and management
3. Soil health, fertilizer recommendations, and organic farming
4. Weather interpretation and its impact on farming
5. Government schemes (PM-KISAN, PMFBY, Krishak Bandhu, KCC, PM-KUSUM, Soil Health Card)
6. Market price guidance and post-harvest management
7. Irrigation techniques and water management
8. KVK programs, training, and technology demonstrations

Context about West Bengal agriculture:
- Main crops: Rice (Aman/Boro/Aus), Potato, Jute, Mustard, Wheat, Vegetables
- Key districts: Bardhaman, Hooghly, Nadia, Murshidabad, Birbhum, Bankura, Purulia
- Three seasons: Kharif (June-Nov), Rabi (Nov-Mar), Zaid (Mar-June)
- Common challenges: Flooding, drought in western districts, soil acidity, BPH in rice

Guidelines:
- Respond in simple English. If the user writes in Bengali (বাংলা), respond in Bengali.
- Be practical and specific to West Bengal conditions
- Mention government schemes when relevant
- For serious plant diseases or pest outbreaks, advise consulting the local KVK
- Keep responses concise but complete
- Use local crop names and varieties when appropriate (e.g., MTU-7029, Swarna Sub1, Kufri Jyoti)
- Be encouraging and supportive to farmers"""

def _get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or Groq is None:
        return None
    return Groq(api_key=api_key)

@chatbot_bp.route('/message', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get("message", "").strip()
    conversation_history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conversation_history[-10:]:
        if msg.get("role") in ["user", "assistant"] and msg.get("content"):
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    client = _get_groq_client()
    if not client:
        return jsonify({"response": _fallback_response(user_message), "source": "fallback"})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        return jsonify({"response": reply, "source": "groq"})
    except Exception as e:
        return jsonify({"response": _fallback_response(user_message), "source": "fallback", "note": str(e)})


def _fallback_response(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["rice", "paddy", "dhan", "ধান"]):
        return ("For Aman paddy in West Bengal: Transplant seedlings 25-30 days old at 20x15 cm spacing. "
                "Apply basal NPK @ 40:30:30 kg/ha. Top dress urea at tillering (21 DAS) and panicle initiation. "
                "Monitor for BPH - install 5 light traps/ha. Recommended varieties: MTU-7029, Swarna Sub1, IR-64.")
    elif any(w in msg for w in ["potato", "aloo", "আলু"]):
        return ("For potato in West Bengal: Sow Oct 15-Nov 15. Use certified seed (Kufri Jyoti, Kufri Sindhuri). "
                "Apply FYM 20 t/ha + NPK 120:80:120 kg/ha. Spray Mancozeb 75 WP @ 2.5 kg/ha every 7 days for Late Blight.")
    elif any(w in msg for w in ["scheme", "subsidy", "pm-kisan", "krishak bandhu"]):
        return ("Key WB schemes:\n• PM-KISAN: Rs6,000/year - pmkisan.gov.in\n"
                "• Krishak Bandhu: Rs10,000/acre/year - Block office\n"
                "• KCC: Credit up to Rs3 lakh @ 4% interest\n• PMFBY: Crop insurance - Block Agriculture Office")
    elif any(w in msg for w in ["pest", "disease", "insect", "রোগ"]):
        return ("Pest tips:\n• BPH in rice: Imidacloprid 17.8 SL @ 125 ml/ha\n"
                "• Late Blight potato: Mancozeb 75 WP\n• Aphids mustard: Dimethoate 30 EC @ 1 L/ha\n"
                "• Fall Armyworm maize: Emamectin Benzoate 5 SG @ 220 g/ha")
    elif any(w in msg for w in ["soil", "fertilizer", "urea"]):
        return ("Soil tips:\n• Free soil testing at KVK (Soil Health Card scheme)\n"
                "• WB soils acidic (pH 5-6.5). Apply lime @ 2-3 t/ha if pH < 5.5\n"
                "• Rice NPK: 80:40:40 kg/ha. Use neem-coated urea.")
    else:
        return ("Namaskar! I am KrishiBot, your KVK advisor for West Bengal.\n\n"
                "I can help with: crop cultivation, pest management, government schemes, soil health, market prices.\n\n"
                "Ask in English or Bengali!\n\n"
                "Set GROQ_API_KEY in backend .env for full AI-powered responses.")


@chatbot_bp.route('/quick-tips', methods=['GET'])
def quick_tips():
    from datetime import datetime
    month = datetime.now().month
    if month in [6, 7, 8, 9]:
        tips = ["Complete Aman paddy transplanting before July 31",
                "Install 5 light traps/ha for BPH monitoring",
                "Ensure field bunding for water retention",
                "Check for stem borer egg masses on paddy leaves"]
    elif month in [10, 11]:
        tips = ["Begin potato sowing with certified seed varieties",
                "Apply lime to acidic soils before Rabi season",
                "Harvest Aman paddy at 80% grain maturity",
                "Set up winter vegetable nursery"]
    elif month in [12, 1, 2]:
        tips = ["Irrigate potato at 10-day intervals",
                "Spray Mancozeb on potato for Late Blight prevention",
                "Apply top dressing to Boro paddy nursery",
                "Harvest mustard when 75% pods turn yellow"]
    else:
        tips = ["Deep plough fields for Kharif preparation",
                "Order certified seeds from authorized dealers",
                "Service irrigation pumps before sowing season",
                "Apply FYM @ 5 t/ha to improve soil fertility"]
    return jsonify({"tips": tips})
