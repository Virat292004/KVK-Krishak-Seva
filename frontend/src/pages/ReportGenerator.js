import React, { useState, useEffect } from 'react';
import { previewReport, generateReport, getCrops } from '../services/api';

const INPUT_STYLE = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' };

export default function ReportGenerator({ district }) {
  const [crops, setCrops]         = useState([]);
  const [preview, setPreview]     = useState(null);
  const [loading, setLoading]     = useState(false);
  const [generating, setGenerating] = useState(false);
  const [form, setForm] = useState({
    farmer_name: '', village: '', land_ha: '1.0',
    primary_crop: 'Rice (Aman)', irrigation: 'Canal/Tubewell',
    season: 'kharif', soil_N: '70', soil_P: '35',
    soil_K: '40', soil_pH: '6.0',
  });

  useEffect(() => {
    getCrops().then(r => setCrops(r.data.crops)).catch(() => {});
  }, []);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handlePreview = async () => {
    setLoading(true);
    try {
      const res = await previewReport({ ...form, district });
      setPreview(res.data);
    } catch (e) {
      alert('Preview failed. Ensure backend is running.');
    }
    setLoading(false);
  };

  const handleDownload = async () => {
    setGenerating(true);
    try {
      const res = await generateReport({ ...form, district });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `KVK_Report_${form.farmer_name || 'Farmer'}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert('PDF generation failed.');
    }
    setGenerating(false);
  };

  return (
    <div>
      <p className="section-title">Farm Report Generator</p>
      <p className="section-sub">Enter farm details to get AI-powered crop recommendations and a downloadable PDF report.</p>

      <div className="grid-2" style={{ gap: 24, alignItems: 'flex-start' }}>
        {/* Form */}
        <div className="card">
          <div className="card-header">
            <div className="card-icon">👤</div>
            <h3>Farmer Details</h3>
          </div>
          <div style={INPUT_STYLE}>
            <div className="form-group">
              <label className="form-label">Farmer Name</label>
              <input className="form-input" placeholder="e.g. Ramesh Mondal"
                value={form.farmer_name} onChange={e => set('farmer_name', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Village / Block</label>
              <input className="form-input" placeholder="e.g. Khandaghosh"
                value={form.village} onChange={e => set('village', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Land Holding (ha)</label>
              <input className="form-input" type="number" step="0.5" min="0.1"
                value={form.land_ha} onChange={e => set('land_ha', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Irrigation Source</label>
              <select className="form-select" value={form.irrigation} onChange={e => set('irrigation', e.target.value)}>
                <option>Canal/Tubewell</option>
                <option>Rain-fed</option>
                <option>Pond/Tank</option>
                <option>Drip/Sprinkler</option>
                <option>None</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Primary Crop</label>
              <select className="form-select" value={form.primary_crop} onChange={e => set('primary_crop', e.target.value)}>
                {crops.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Season</label>
              <select className="form-select" value={form.season} onChange={e => set('season', e.target.value)}>
                <option value="kharif">Kharif (Jun–Nov)</option>
                <option value="rabi">Rabi (Nov–Mar)</option>
                <option value="zaid">Zaid (Mar–Jun)</option>
              </select>
            </div>
          </div>

          <div style={{ margin: '20px 0 6px', borderTop: '1px solid var(--gray-200)', paddingTop: 18 }}>
            <div className="card-header" style={{ marginBottom: 14 }}>
              <div className="card-icon">🧪</div>
              <h3>Soil Test Values</h3>
            </div>
            <div style={INPUT_STYLE}>
              {[['soil_N','Nitrogen (N) kg/ha','60–120'],['soil_P','Phosphorus (P) kg/ha','20–60'],
                ['soil_K','Potassium (K) kg/ha','20–80'],['soil_pH','Soil pH','4.5–8.0']].map(([k,label,hint]) => (
                <div className="form-group" key={k}>
                  <label className="form-label">{label}</label>
                  <input className="form-input" type="number" step="0.1"
                    placeholder={hint} value={form[k]} onChange={e => set(k, e.target.value)} />
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
            <button className="btn btn-secondary" onClick={handlePreview} disabled={loading}>
              {loading ? <><span className="spinner" style={{ borderColor: 'rgba(0,0,0,0.2)', borderTopColor: 'var(--green-800)' }} /> Analyzing...</> : '🔍 Preview Analysis'}
            </button>
            <button className="btn btn-primary" onClick={handleDownload} disabled={generating}>
              {generating ? <><span className="spinner" /> Generating...</> : '📄 Download PDF Report'}
            </button>
          </div>
        </div>

        {/* Preview panel */}
        <div>
          {!preview ? (
            <div className="card" style={{ textAlign: 'center', padding: '50px 24px', color: 'var(--gray-600)' }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>📊</div>
              <p style={{ fontWeight: 600 }}>Fill in the form and click "Preview Analysis"</p>
              <p style={{ fontSize: 13, marginTop: 8 }}>AI-powered crop recommendations and yield predictions will appear here</p>
            </div>
          ) : (
            <>
              {/* ML Recommendations */}
              <div className="card" style={{ marginBottom: 16 }}>
                <div className="card-header">
                  <div className="card-icon">🤖</div>
                  <h3>AI Crop Recommendations</h3>
                </div>
                {(preview.ml?.recommendations || []).map((r, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '10px 14px', marginBottom: 8, borderRadius: 8,
                    background: i === 0 ? 'var(--green-50)' : 'var(--gray-100)',
                    border: `1px solid ${i === 0 ? 'var(--green-400)' : 'var(--gray-200)'}`
                  }}>
                    <div>
                      <span style={{ fontWeight: 700, fontSize: 14 }}>{['🥇','🥈','🥉'][i]} {r.crop}</span>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 700, color: 'var(--green-800)' }}>{r.confidence}%</div>
                      <div style={{ fontSize: 11, color: 'var(--gray-600)' }}>confidence</div>
                    </div>
                  </div>
                ))}
                {preview.ml?.yield_prediction && (
                  <div style={{ marginTop: 12, padding: '12px 14px', background: '#E8F5E9', borderRadius: 8, border: '1px solid var(--green-400)' }}>
                    <div style={{ fontSize: 12, color: 'var(--green-700)', fontWeight: 600 }}>PREDICTED YIELD</div>
                    <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--green-800)' }}>
                      {preview.ml.yield_prediction.predicted_yield_qtl_per_ha} <span style={{ fontSize: 13 }}>qtl/ha</span>
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--gray-600)' }}>
                      = {preview.ml.yield_prediction.predicted_yield_kg_per_ha} kg/ha for {preview.ml.yield_prediction.crop}
                    </div>
                  </div>
                )}
              </div>

              {/* Pest risk */}
              {preview.ml?.pest_risk && (
                <div className="card" style={{ marginBottom: 16 }}>
                  <div className="card-header">
                    <div className="card-icon">🐛</div>
                    <h3>Pest Risk — {preview.ml.pest_risk.crop}</h3>
                  </div>
                  <table className="data-table">
                    <thead><tr><th>Pest</th><th>Risk</th></tr></thead>
                    <tbody>
                      {(preview.ml.pest_risk.pest_risks || []).map((p, i) => (
                        <tr key={i}>
                          <td>{p.pest}</td>
                          <td><span className={`risk-${p.risk_level.toLowerCase()}`}>{p.risk_level}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Weather summary */}
              <div className="card">
                <div className="card-header">
                  <div className="card-icon">🌤️</div>
                  <h3>Current Weather — {district}</h3>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                  {[
                    ['Condition', preview.weather?.condition],
                    ['Max Temp', `${preview.weather?.temp_max}°C`],
                    ['Rainfall', `${preview.weather?.rainfall_mm} mm`],
                    ['Humidity', `${preview.weather?.humidity_pct}%`],
                  ].map(([k, v]) => (
                    <div key={k} style={{ background: 'var(--gray-100)', padding: '10px 14px', borderRadius: 8 }}>
                      <div style={{ fontSize: 11, color: 'var(--gray-600)', fontWeight: 600 }}>{k}</div>
                      <div style={{ fontWeight: 700, fontSize: 15, marginTop: 2 }}>{v}</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
