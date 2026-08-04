# 🌾 KVK Krishak Seva — Smart Farming App for West Bengal

A full-stack web application providing AI-powered agricultural advisory, automated PDF farm reports, and a chatbot (KrishiBot) for farmers in West Bengal, India.

---

## 🗂️ Project Structure

```
kvk-farmer-app/
├── backend/                  # Flask Python backend
│   ├── app.py                # Main Flask app
│   ├── requirements.txt
│   ├── .env.example          # Copy to .env and add your key
│   ├── Dockerfile
│   ├── routes/
│   │   ├── report.py         # Report generation + ML endpoints
│   │   ├── chatbot.py        # KrishiBot (Groq LLaMA) endpoints
│   │   └── data.py           # Weather, market, advisory endpoints
│   ├── services/
│   │   ├── data_service.py   # WB agricultural data & mock APIs
│   │   ├── ml_service.py     # ML models (crop recommendation + yield)
│   │   └── report_service.py # PDF report builder (ReportLab)
│   └── models/               # Auto-created when app first runs
│
├── frontend/                 # React JS frontend
│   ├── package.json
│   ├── public/index.html
│   ├── Dockerfile
│   ├── nginx.conf
│   └── src/
│       ├── App.js            # Router + Layout + Sidebar
│       ├── index.js
│       ├── index.css         # Global styles
│       ├── services/api.js   # Axios API calls
│       └── pages/
│           ├── Dashboard.js        # Weather + Advisory + Market chart
│           ├── ReportGenerator.js  # Farm report form + PDF download
│           ├── Chatbot.js          # KrishiBot AI chat interface
│           ├── MarketPrices.js     # Mandi prices table
│           └── Schemes.js          # Government schemes browser
│
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.9+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| npm | 9+ | Comes with Node.js |
| Git | Any | https://git-scm.com |

---

## 🚀 Quick Start (Manual — Recommended for Development)

### Step 1 — Get a Free Groq API Key

1. Go to **https://console.groq.com**
2. Sign up for a free account
3. Go to **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_...`)

---

### Step 2 — Set Up the Backend

```bash
# Navigate to backend directory
cd kvk-farmer-app/backend

# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
```

Now open `.env` and paste your Groq API key:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

```bash
# Run the backend
python app.py
```

✅ Backend will start at **http://localhost:5000**

On first run, it will automatically train the ML models (takes ~30–60 seconds).

---

### Step 3 — Set Up the Frontend

Open a **new terminal window**:

```bash
# Navigate to frontend directory
cd kvk-farmer-app/frontend

# Install Node packages
npm install

# Start the React dev server
npm start
```

✅ Frontend will open at **http://localhost:3000**

The React app proxies all `/api/` calls to the Flask backend automatically.

---

## 🐳 Docker Deployment (Production)

```bash
# In the root kvk-farmer-app/ directory
# Create a .env file with your key:
echo "GROQ_API_KEY=gsk_your_key_here" > .env

# Build and start both services
docker-compose up --build

# Access:
# Frontend → http://localhost:3000
# Backend  → http://localhost:5000
```

---

## 🌐 API Endpoints

### Data Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/data/weather?district=Bardhaman` | Current weather |
| GET | `/api/data/market?district=Bardhaman` | Market prices |
| GET | `/api/data/advisory?district=Bardhaman` | Farm advisory |
| GET | `/api/data/schemes` | Govt schemes |
| GET | `/api/data/districts` | WB districts list |
| GET | `/api/data/crops` | Crop list |
| GET | `/api/data/dashboard?district=Bardhaman` | All dashboard data |

### Report Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/report/preview` | JSON preview of report data |
| POST | `/api/report/generate` | Download PDF report |
| POST | `/api/report/train` | Re-train ML models |

### Chatbot Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/chat/message` | Send message to KrishiBot |
| GET | `/api/chat/quick-tips` | Seasonal farming tips |

### Example Report Request Body
```json
{
  "farmer_name": "Ramesh Mondal",
  "village": "Khandaghosh",
  "district": "Bardhaman",
  "land_ha": 2.5,
  "primary_crop": "Rice (Aman)",
  "irrigation": "Canal/Tubewell",
  "season": "kharif",
  "soil_N": 75,
  "soil_P": 38,
  "soil_K": 42,
  "soil_pH": 6.2
}
```

---

## 🤖 ML Models

Two models are automatically trained on startup:

### 1. Crop Recommender (Random Forest Classifier)
- **Input:** Soil NPK, pH, temperature, rainfall, humidity, season
- **Output:** Top 3 recommended crops with confidence %
- **Training data:** 3,000 synthetic agronomic samples for WB crops
- **Accuracy:** ~85–90%

### 2. Yield Predictor (Gradient Boosting Regressor)
- **Input:** Crop type, soil NPK, pH, temperature, rainfall, humidity, irrigation
- **Output:** Predicted yield in quintal/ha
- **Training data:** 2,000 synthetic samples across 8 crops
- **R² Score:** ~0.75–0.80

### 3. Pest Risk Assessor (Rule-based)
- **Input:** Crop, temperature, humidity, rainfall
- **Output:** Risk level (High/Medium/Low) + treatment recommendation for each pest

---

## 🌿 Features

| Feature | Details |
|---------|---------|
| 📊 Dashboard | Live weather, 7-day forecast, market chart, advisory, schemes |
| 📄 PDF Reports | AI crop reco, yield prediction, pest risk, market prices, schemes — all in one PDF |
| 🤖 KrishiBot | Groq LLaMA 3.3 70B chatbot — English + Bengali support |
| 📈 Market Prices | MSP vs market price comparison with trends |
| 🏛️ Schemes | PM-KISAN, Krishak Bandhu, KCC, PMFBY, PM-KUSUM, Soil Health Card |
| 🗺️ District-wise | All 20 West Bengal districts supported |

---

## 🔧 Troubleshooting

**Backend won't start:**
```bash
# Make sure you're in the virtual environment
# Check Python version
python --version  # must be 3.9+

# Try reinstalling
pip install -r requirements.txt --force-reinstall
```

**ML models fail to train:**
```bash
# Run training manually
python -c "from services.ml_service import train_models; train_models()"
```

**Chatbot returns fallback responses:**
- Ensure `GROQ_API_KEY` is set in `backend/.env`
- Verify the key at https://console.groq.com
- The app still works without a key using rule-based responses

**Frontend can't reach backend:**
- Ensure backend is running on port 5000
- Check the `"proxy": "http://localhost:5000"` line in `frontend/package.json`
- For production, ensure nginx.conf proxy is correct

**PDF not downloading:**
- Check browser allows downloads from localhost
- Try a different browser
- Check backend logs for ReportLab errors

---

## 📞 Support

For agricultural queries, contact:
- **KVK Helpline:** 1800-180-1551 (Toll free)
- **Kisan Call Centre:** 1551
- **PM-KISAN:** 155261 / 011-24300606

---

## 📄 License

This project is built for educational and agricultural development purposes under ICAR-KVK guidelines.
