import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ReportGenerator from './pages/ReportGenerator';
import Chatbot from './pages/Chatbot';
import MarketPrices from './pages/MarketPrices';
import Schemes from './pages/Schemes';
import { getDistricts } from './services/api';

const NAV = [
  { path: '/',         icon: '🏠', label: 'Dashboard' },
  { path: '/report',   icon: '📄', label: 'Farm Report' },
  { path: '/chat',     icon: '🤖', label: 'KrishiBot AI' },
  { path: '/market',   icon: '📊', label: 'Market Prices' },
  { path: '/schemes',  icon: '🏛️', label: 'Govt Schemes' },
];

function Sidebar({ district, setDistrict, districts }) {
  const navigate = useNavigate();
  const location = useLocation();
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-icon">🌾</span>
        <h2>KVK Krishak Seva</h2>
        <p>West Bengal Agricultural Advisory</p>
      </div>
      <nav className="sidebar-nav">
        {NAV.map(n => (
          <button
            key={n.path}
            className={`nav-item ${location.pathname === n.path ? 'active' : ''}`}
            onClick={() => navigate(n.path)}
          >
            <span className="nav-icon">{n.icon}</span>
            {n.label}
          </button>
        ))}
        <div style={{ marginTop: 'auto', paddingTop: 20 }}>
          <div className="form-group" style={{ padding: '0 2px' }}>
            <label className="form-label" style={{ color: 'rgba(255,255,255,0.6)', fontSize: 11 }}>
              YOUR DISTRICT
            </label>
            <select
              className="form-select"
              style={{ background: 'rgba(255,255,255,0.1)', color: 'white', borderColor: 'rgba(255,255,255,0.2)', fontSize: 13 }}
              value={district}
              onChange={e => setDistrict(e.target.value)}
            >
              {districts.map(d => <option key={d} value={d} style={{ color: '#263238' }}>{d}</option>)}
            </select>
          </div>
        </div>
      </nav>
      <div className="sidebar-footer">
        ICAR-KVK West Bengal<br />
        Powered by Groq AI
      </div>
    </aside>
  );
}

function Layout({ district, setDistrict, districts }) {
  const location = useLocation();
  const current = NAV.find(n => n.path === location.pathname) || NAV[0];
  return (
    <div className="app-layout">
      <Sidebar district={district} setDistrict={setDistrict} districts={districts} />
      <div className="main-content">
        <header className="topbar">
          <h1>{current.icon} {current.label}</h1>
          <div className="topbar-right">
            <span className="district-badge">📍 {district}</span>
          </div>
        </header>
        <main className="page-body">
          <Routes>
            <Route path="/"        element={<Dashboard district={district} />} />
            <Route path="/report"  element={<ReportGenerator district={district} />} />
            <Route path="/chat"    element={<Chatbot district={district} />} />
            <Route path="/market"  element={<MarketPrices district={district} />} />
            <Route path="/schemes" element={<Schemes />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  const [district, setDistrict] = useState('Bardhaman');
  const [districts, setDistricts] = useState([
    'Bankura','Bardhaman','Birbhum','Cooch Behar','Darjeeling',
    'Hooghly','Howrah','Jalpaiguri','Malda','Murshidabad',
    'Nadia','North 24 Parganas','Purulia','South 24 Parganas'
  ]);

  useEffect(() => {
    getDistricts().then(r => setDistricts(r.data.districts)).catch(() => {});
  }, []);

  return (
    <BrowserRouter>
      <Layout district={district} setDistrict={setDistrict} districts={districts} />
    </BrowserRouter>
  );
}
