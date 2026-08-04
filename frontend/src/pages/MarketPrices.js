import React, { useState, useEffect } from 'react';
import { getMarket } from '../services/api';

export default function MarketPrices({ district }) {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  const load = () => {
    setLoading(true);
    getMarket(district).then(r => setPrices(r.data.prices || [])).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [district]);

  const filtered = prices.filter(p => p.crop.toLowerCase().includes(filter.toLowerCase()));

  const trendClass = (t) => {
    if (t?.includes('↑')) return 'trend-up';
    if (t?.includes('↓')) return 'trend-down';
    return 'trend-flat';
  };

  return (
    <div>
      <p className="section-title">Market Prices</p>
      <p className="section-sub">Live mandi prices and MSP for {district} district. Updated daily.</p>

      <div style={{ display: 'flex', gap: 12, marginBottom: 20, alignItems: 'center' }}>
        <input
          className="form-input"
          style={{ maxWidth: 280 }}
          placeholder="🔍 Search crop..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />
        <button className="btn btn-secondary" onClick={load}>🔄 Refresh</button>
        <span style={{ marginLeft: 'auto', fontSize: 13, color: 'var(--gray-600)' }}>
          📅 {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
        </span>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 32 }}>📊</div>
          <p style={{ marginTop: 12 }}>Loading market prices<span className="loading-dots" /></p>
        </div>
      ) : (
        <div className="card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Crop</th>
                <th>MSP (₹/qtl)</th>
                <th>Market Price</th>
                <th>Diff vs MSP</th>
                <th>Trend</th>
                <th>Market</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p, i) => {
                const diff = p.market_price - p.msp;
                const diffPct = ((diff / p.msp) * 100).toFixed(1);
                return (
                  <tr key={i}>
                    <td><strong>{p.crop}</strong></td>
                    <td>₹{p.msp?.toLocaleString('en-IN')}</td>
                    <td style={{ fontWeight: 700, fontSize: 15 }}>
                      ₹{p.market_price?.toLocaleString('en-IN')}
                    </td>
                    <td>
                      <span style={{ color: diff >= 0 ? 'var(--green-700)' : 'var(--red)', fontWeight: 600 }}>
                        {diff >= 0 ? '+' : ''}{diff} ({diffPct}%)
                      </span>
                    </td>
                    <td><span className={trendClass(p.trend)}>{p.trend}</span></td>
                    <td style={{ color: 'var(--gray-600)', fontSize: 12 }}>{p.market}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <p style={{ textAlign: 'center', padding: 20, color: 'var(--gray-600)' }}>No crops found.</p>
          )}
        </div>
      )}

      <div className="card" style={{ marginTop: 20, background: 'var(--yellow-lt)', borderColor: '#FFE082' }}>
        <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
          <span style={{ fontSize: 20 }}>⚠️</span>
          <div style={{ fontSize: 13, color: '#7B5800', lineHeight: 1.6 }}>
            <strong>Disclaimer:</strong> Market prices shown are simulated based on historical patterns for demonstration purposes.
            For official prices, visit <strong>agmarknet.gov.in</strong> or your nearest APMC market.
            MSP figures are as per Government of India notifications for 2024-25.
          </div>
        </div>
      </div>
    </div>
  );
}
