import React, { useState, useEffect } from 'react';
import { getDashboard } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const weatherIcon = (cond) => {
  if (!cond) return '🌡️';
  const c = cond.toLowerCase();
  if (c.includes('thunder')) return '⛈️';
  if (c.includes('heavy rain') || c.includes('monsoon')) return '🌧️';
  if (c.includes('light rain') || c.includes('moderate rain')) return '🌦️';
  if (c.includes('overcast') || c.includes('cloudy')) return '☁️';
  if (c.includes('partly')) return '⛅';
  if (c.includes('winter') || c.includes('clear')) return '☀️';
  if (c.includes('hot') || c.includes('pre-monsoon')) return '🌤️';
  if (c.includes('post-monsoon')) return '🌤️';
  return '🌡️';
};

export default function Dashboard({ district }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getDashboard(district)
      .then(r => setData(r.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [district]);

  if (loading) return (
    <div style={{ textAlign: 'center', paddingTop: 80, color: 'var(--green-700)' }}>
      <div style={{ fontSize: 48 }}>🌱</div>
      <p style={{ marginTop: 16, fontWeight: 600 }}>Loading farm data<span className="loading-dots" /></p>
    </div>
  );

  if (!data) return <div className="card"><p>⚠️ Could not load data. Make sure backend is running.</p></div>;

  const { weather, market_prices, advisory, schemes } = data;
  const forecast = weather?.forecast_7day || [];
  const topPrices = (market_prices || []).slice(0, 6).map(p => ({
    crop: p.crop.replace(' (', '\n('),
    price: p.market_price,
    msp: p.msp
  }));

  return (
    <div>
      <p className="section-title">Good day, Farmer! 🙏</p>
      <p className="section-sub">Here's your daily agricultural overview for {district} district.</p>

      {/* Stat tiles */}
      <div className="grid-4" style={{ marginBottom: 24 }}>
        <div className="stat-tile">
          <div className="stat-label">Temperature</div>
          <div className="stat-value">{weather?.temp_max}°C</div>
          <div className="stat-sub">Min: {weather?.temp_min}°C</div>
        </div>
        <div className="stat-tile">
          <div className="stat-label">Rainfall</div>
          <div className="stat-value">{weather?.rainfall_mm}<span style={{ fontSize: 14 }}>mm</span></div>
          <div className="stat-sub">Humidity: {weather?.humidity_pct}%</div>
        </div>
        <div className="stat-tile">
          <div className="stat-label">Season</div>
          <div className="stat-value" style={{ fontSize: 18, marginTop: 10 }}>{advisory?.season}</div>
          <div className="stat-sub">{advisory?.date}</div>
        </div>
        <div className="stat-tile">
          <div className="stat-label">Wind Speed</div>
          <div className="stat-value">{weather?.wind_kmh}<span style={{ fontSize: 14 }}>km/h</span></div>
          <div className="stat-sub">{weather?.condition}</div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Weather card */}
        <div className="card">
          <div className="card-header">
            <div className="card-icon">🌤️</div>
            <h3>7-Day Forecast</h3>
          </div>
          <div className="forecast-strip">
            {forecast.map((d, i) => (
              <div key={i} className="forecast-day">
                <div className="f-day">{d.day.slice(0, 3).toUpperCase()}</div>
                <div className="f-day" style={{ color: 'var(--gray-600)', fontWeight: 400 }}>{d.date}</div>
                <div className="f-icon">{weatherIcon(d.condition)}</div>
                <div className="f-temp">{d.temp_max}° / {d.temp_min}°</div>
                <div className="f-temp" style={{ marginTop: 3 }}>{d.condition.split('/')[0]}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Advisory */}
        <div className="card">
          <div className="card-header">
            <div className="card-icon">📋</div>
            <h3>Today's Advisory</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {(advisory?.advisories || []).map((a, i) => (
              <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', fontSize: 13, lineHeight: 1.5 }}>
                <span style={{ color: 'var(--green-600)', fontWeight: 700, flexShrink: 0 }}>•</span>
                <span>{a}</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 14, padding: '10px 14px', background: 'var(--green-50)', borderRadius: 8, fontSize: 12, color: 'var(--green-800)' }}>
            📞 KVK: {advisory?.kvk_contact}
          </div>
        </div>
      </div>

      {/* Market chart */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div className="card-icon">📊</div>
          <h3>Market Price Overview (₹/quintal)</h3>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={topPrices} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ECEFF1" />
            <XAxis dataKey="crop" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(val, name) => [`₹${val}`, name === 'price' ? 'Market Price' : 'MSP']}
              contentStyle={{ borderRadius: 8, fontSize: 12 }}
            />
            <Bar dataKey="msp"   name="MSP"          fill="#A5D6A7" radius={[4,4,0,0]} />
            <Bar dataKey="price" name="Market Price" fill="#2E7D32" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Schemes teaser */}
      <div className="card">
        <div className="card-header">
          <div className="card-icon">🏛️</div>
          <h3>Active Government Schemes</h3>
        </div>
        <div className="grid-2">
          {(schemes || []).slice(0, 4).map((s, i) => (
            <div key={i} style={{
              padding: '14px', background: 'var(--green-50)',
              borderRadius: 8, border: '1px solid var(--green-100)'
            }}>
              <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--green-800)', marginBottom: 4 }}>{s.name}</div>
              <div style={{ fontSize: 12, color: 'var(--gray-600)', marginBottom: 6 }}>{s.description.slice(0, 80)}...</div>
              <span className="badge badge-green">{s.benefit}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
