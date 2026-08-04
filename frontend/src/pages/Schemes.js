import React, { useState, useEffect } from 'react';
import { getSchemes } from '../services/api';

const SCHEME_ICONS = {
  'PM-KISAN': '💰',
  'Bangla Shasyabima (PMFBY WB)': '🛡️',
  'Krishak Bandhu': '🤝',
  'Kisan Credit Card (KCC)': '💳',
  'PM Kusum Yojana': '☀️',
  'Soil Health Card Scheme': '🧪',
};

export default function Schemes() {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    getSchemes()
      .then(r => setSchemes(r.data.schemes || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div style={{ textAlign: 'center', paddingTop: 60, color: 'var(--green-700)' }}>
      <div style={{ fontSize: 40 }}>🏛️</div>
      <p style={{ marginTop: 12, fontWeight: 600 }}>Loading schemes<span className="loading-dots" /></p>
    </div>
  );

  return (
    <div>
      <p className="section-title">Government Schemes</p>
      <p className="section-sub">
        Central and West Bengal state schemes available for farmers. Click a scheme to see full details.
      </p>

      <div className="grid-2" style={{ gap: 20, alignItems: 'flex-start' }}>
        {/* Scheme cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {schemes.map((s, i) => (
            <div
              key={i}
              className="card"
              style={{
                cursor: 'pointer',
                borderColor: selected === i ? 'var(--green-600)' : 'var(--gray-200)',
                borderWidth: selected === i ? 2 : 1,
                background: selected === i ? 'var(--green-50)' : 'white',
                transition: 'all 0.15s ease',
              }}
              onClick={() => setSelected(selected === i ? null : i)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 12,
                  background: 'var(--green-100)', display: 'flex',
                  alignItems: 'center', justifyContent: 'center', fontSize: 24, flexShrink: 0
                }}>
                  {SCHEME_ICONS[s.name] || '📋'}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--green-900)' }}>{s.name}</div>
                  <div style={{ fontSize: 12, color: 'var(--gray-600)', marginTop: 2 }}>
                    {s.description.slice(0, 70)}...
                  </div>
                </div>
                <span className="badge badge-green" style={{ flexShrink: 0 }}>{s.benefit.split(' ').slice(0, 3).join(' ')}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Detail panel */}
        <div style={{ position: 'sticky', top: 80 }}>
          {selected === null ? (
            <div className="card" style={{ textAlign: 'center', padding: '50px 24px', color: 'var(--gray-600)' }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>🏛️</div>
              <p style={{ fontWeight: 600 }}>Select a scheme to view details</p>
              <p style={{ fontSize: 13, marginTop: 8 }}>
                Eligibility criteria, benefit amount, and application process will appear here.
              </p>
            </div>
          ) : (
            <div className="card">
              <div style={{ display: 'flex', gap: 14, alignItems: 'center', marginBottom: 20 }}>
                <div style={{
                  width: 56, height: 56, borderRadius: 14,
                  background: 'var(--green-800)', display: 'flex',
                  alignItems: 'center', justifyContent: 'center', fontSize: 28
                }}>
                  {SCHEME_ICONS[schemes[selected].name] || '📋'}
                </div>
                <div>
                  <h2 style={{ fontSize: 18, color: 'var(--green-900)' }}>{schemes[selected].name}</h2>
                  <span className="badge badge-green" style={{ marginTop: 4, display: 'inline-block' }}>
                    Benefit: {schemes[selected].benefit}
                  </span>
                </div>
              </div>

              {[
                { label: '📋 Description', value: schemes[selected].description },
                { label: '✅ Eligibility', value: schemes[selected].eligibility },
                { label: '💰 Benefit', value: schemes[selected].benefit },
                { label: '📍 How to Apply', value: schemes[selected].apply_at },
              ].map(({ label, value }) => (
                <div key={label} style={{
                  marginBottom: 16, padding: '14px',
                  background: 'var(--gray-100)', borderRadius: 8
                }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--green-700)', marginBottom: 6 }}>
                    {label}
                  </div>
                  <div style={{ fontSize: 14, color: 'var(--gray-900)', lineHeight: 1.6 }}>{value}</div>
                </div>
              ))}

              <a
                href={schemes[selected].apply_at?.startsWith('http') ? schemes[selected].apply_at : '#'}
                target="_blank"
                rel="noreferrer"
                className="btn btn-primary"
                style={{ textDecoration: 'none', marginTop: 4 }}
              >
                🔗 Apply / Learn More
              </a>
            </div>
          )}

          {/* Help box */}
          <div className="card" style={{ marginTop: 16, background: 'var(--green-50)', borderColor: 'var(--green-100)' }}>
            <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--green-800)', marginBottom: 8 }}>
              📞 Need Help Applying?
            </div>
            <div style={{ fontSize: 13, color: 'var(--gray-700)', lineHeight: 1.7 }}>
              • Visit your nearest <strong>Block Agriculture Office</strong><br />
              • Contact your local <strong>KVK (Krishi Vigyan Kendra)</strong><br />
              • Call the Kisan Call Centre: <strong>1800-180-1551</strong> (Toll free)<br />
              • PM-KISAN helpline: <strong>155261 / 011-24300606</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
