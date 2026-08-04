import React, { useState, useEffect, useRef, useCallback } from 'react';
import { sendChat, getQuickTips } from '../services/api';

const WELCOME = `🙏 Namaskar! I am KrishiBot — your AI agricultural advisor for West Bengal.

I can help you with:
• Crop cultivation & best practices
• Pest & disease management  
• Government schemes (PM-KISAN, Krishak Bandhu, KCC...)
• Soil health & fertilizer recommendations
• Market prices & post-harvest advice

আপনি বাংলায়ও জিজ্ঞেস করতে পারেন! (You can ask in Bengali too!)

How can I help you today?`;

const SUGGESTIONS = [
  "How to control BPH in paddy?",
  "Best variety of rice for Kharif?",
  "What is PM-KISAN scheme?",
  "Potato Late Blight treatment",
  "Soil testing kaise karein?",
  "Krishak Bandhu scheme details",
];

// ── Pulse animation for recording indicator ───────────────────────────
const pulseStyle = `
  @keyframes bounce { 0%,80%,100%{transform:scale(0.8);opacity:0.5} 40%{transform:scale(1.2);opacity:1} }
  @keyframes pulse  { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(1.18);opacity:0.75} }
  @keyframes ripple { 0%{transform:scale(1);opacity:0.6} 100%{transform:scale(2.2);opacity:0} }
  @keyframes fadeIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
  .msg-anim { animation: fadeIn 0.22s ease; }
`;

function TypingDots() {
  return (
    <div style={{ display: 'flex', gap: 4, padding: '8px 4px', alignItems: 'center' }}>
      {[0,1,2].map(i => (
        <div key={i} style={{
          width: 8, height: 8, borderRadius: '50%',
          background: 'var(--green-600)',
          animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
        }} />
      ))}
    </div>
  );
}

// ── Mic button with ripple effect ─────────────────────────────────────
function MicButton({ isRecording, isSupported, onClick, disabled }) {
  if (!isSupported) return (
    <div title="Voice not supported in this browser" style={{
      width: 42, height: 42, borderRadius: '50%',
      background: 'var(--gray-200)', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      fontSize: 18, opacity: 0.4, cursor: 'not-allowed', flexShrink: 0
    }}>🎙️</div>
  );

  return (
    <div style={{ position: 'relative', flexShrink: 0 }}>
      {isRecording && (
        <>
          <div style={{
            position: 'absolute', inset: -6, borderRadius: '50%',
            border: '2px solid #ef4444',
            animation: 'ripple 1s ease-out infinite',
          }} />
          <div style={{
            position: 'absolute', inset: -12, borderRadius: '50%',
            border: '2px solid #ef4444',
            animation: 'ripple 1s ease-out 0.4s infinite',
          }} />
        </>
      )}
      <button
        onClick={onClick}
        disabled={disabled}
        title={isRecording ? 'Stop recording' : 'Speak your question'}
        style={{
          width: 42, height: 42, borderRadius: '50%', border: 'none',
          cursor: disabled ? 'not-allowed' : 'pointer',
          background: isRecording
            ? 'linear-gradient(135deg, #ef4444, #dc2626)'
            : 'linear-gradient(135deg, var(--green-700), var(--green-800))',
          color: 'white', fontSize: 18,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: isRecording ? '0 0 0 3px rgba(239,68,68,0.25)' : '0 2px 8px rgba(0,0,0,0.18)',
          transition: 'all 0.2s ease',
          animation: isRecording ? 'pulse 1s ease-in-out infinite' : 'none',
          position: 'relative', zIndex: 1,
        }}
      >
        {isRecording ? '⏹' : '🎙️'}
      </button>
    </div>
  );
}

// ── Speaker / TTS button ──────────────────────────────────────────────
function SpeakButton({ text, isSpeaking, onToggle }) {
  return (
    <button
      onClick={() => onToggle(text)}
      title={isSpeaking ? 'Stop speaking' : 'Read aloud'}
      style={{
        background: 'none', border: 'none', cursor: 'pointer',
        fontSize: 14, padding: '2px 4px', borderRadius: 4,
        color: isSpeaking ? '#ef4444' : 'var(--green-600)',
        transition: 'color 0.15s',
      }}
    >
      {isSpeaking ? '🔇' : '🔊'}
    </button>
  );
}

export default function Chatbot({ district }) {
  const [messages, setMessages]       = useState([{ role: 'assistant', content: WELCOME, ts: new Date() }]);
  const [input, setInput]             = useState('');
  const [loading, setLoading]         = useState(false);
  const [tips, setTips]               = useState([]);

  // Voice input (STT) state
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript]   = useState('');
  const [sttSupported, setSttSupported] = useState(false);
  const [sttLang, setSttLang]         = useState('en-IN');
  const [sttStatus, setSttStatus]     = useState('');   // status text shown to user

  // Voice output (TTS) state
  const [speakingIdx, setSpeakingIdx] = useState(null); // index of message being spoken
  const [ttsEnabled, setTtsEnabled]   = useState(true);
  const [ttsVoice, setTtsVoice]       = useState(null);
  const [availableVoices, setAvailableVoices] = useState([]);

  const recognitionRef = useRef(null);
  const bottomRef      = useRef(null);
  const utteranceRef   = useRef(null);

  // ── Detect browser support & load voices ────────────────────────────
  useEffect(() => {
    getQuickTips().then(r => setTips(r.data.tips)).catch(() => {});

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setSttSupported(!!SpeechRecognition);

    // Load TTS voices
    const loadVoices = () => {
      const voices = window.speechSynthesis?.getVoices() || [];
      setAvailableVoices(voices);
      // Prefer Indian English or Hindi voice
      const preferred = voices.find(v => v.lang === 'en-IN')
        || voices.find(v => v.lang.startsWith('en'))
        || voices[0];
      if (preferred) setTtsVoice(preferred);
    };
    loadVoices();
    window.speechSynthesis?.addEventListener('voiceschanged', loadVoices);
    return () => window.speechSynthesis?.removeEventListener('voiceschanged', loadVoices);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // ── Stop TTS when component unmounts ────────────────────────────────
  useEffect(() => {
    return () => {
      window.speechSynthesis?.cancel();
      recognitionRef.current?.stop();
    };
  }, []);

  // ── Speech-to-Text ───────────────────────────────────────────────────
  const startRecording = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    // Stop any playing TTS first
    window.speechSynthesis?.cancel();
    setSpeakingIdx(null);

    const recognition = new SpeechRecognition();
    recognition.continuous      = false;
    recognition.interimResults  = true;
    recognition.lang            = sttLang;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsRecording(true);
      setTranscript('');
      setSttStatus('🎙️ Listening… speak now');
    };

    recognition.onresult = (event) => {
      let interim = '';
      let final   = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) final += t;
        else interim += t;
      }
      const current = final || interim;
      setTranscript(current);
      setInput(current);
      setSttStatus(final ? '✅ Got it! Sending…' : `🎙️ ${current}`);
      if (final) {
        setIsRecording(false);
        recognitionRef.current = null;
        // Auto-send after short delay
        setTimeout(() => {
          setSttStatus('');
          setTranscript('');
          sendMessage(final.trim());
        }, 500);
      }
    };

    recognition.onerror = (event) => {
      setIsRecording(false);
      recognitionRef.current = null;
      if (event.error === 'no-speech') setSttStatus('⚠️ No speech detected. Try again.');
      else if (event.error === 'not-allowed') setSttStatus('❌ Microphone permission denied.');
      else setSttStatus(`❌ Error: ${event.error}`);
      setTimeout(() => setSttStatus(''), 3000);
    };

    recognition.onend = () => {
      setIsRecording(false);
      recognitionRef.current = null;
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, [sttLang]);

  const stopRecording = useCallback(() => {
    recognitionRef.current?.stop();
    setIsRecording(false);
    setSttStatus('');
  }, []);

  const toggleRecording = () => {
    if (isRecording) stopRecording();
    else startRecording();
  };

  // ── Text-to-Speech ───────────────────────────────────────────────────
  const speak = useCallback((text, idx) => {
    if (!window.speechSynthesis) return;

    // If already speaking this message, stop
    if (speakingIdx === idx) {
      window.speechSynthesis.cancel();
      setSpeakingIdx(null);
      return;
    }

    window.speechSynthesis.cancel();
    const clean = text.replace(/[•*#]/g, '').replace(/\n+/g, '. ');
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.voice  = ttsVoice;
    utterance.lang   = sttLang === 'bn-IN' ? 'bn-IN' : 'en-IN';
    utterance.rate   = 0.92;
    utterance.pitch  = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => setSpeakingIdx(idx);
    utterance.onend   = () => setSpeakingIdx(null);
    utterance.onerror = () => setSpeakingIdx(null);

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [speakingIdx, ttsVoice, sttLang]);

  const stopSpeaking = () => {
    window.speechSynthesis?.cancel();
    setSpeakingIdx(null);
  };

  // ── Send message ─────────────────────────────────────────────────────
  const sendMessage = async (textOverride) => {
    const msg = (textOverride || input).trim();
    if (!msg) return;
    setInput('');
    setTranscript('');
    stopSpeaking();

    const userMsg = { role: 'user', content: msg, ts: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      const res = await sendChat(`[District: ${district}] ${msg}`, history);
      const reply = res.data.response;
      const newMsg = { role: 'assistant', content: reply, ts: new Date(), source: res.data.source };
      setMessages(prev => {
        const updated = [...prev, newMsg];
        // Auto-speak if TTS enabled
        if (ttsEnabled) {
          setTimeout(() => speak(reply, updated.length - 1), 300);
        }
        return updated;
      });
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Could not reach the server. Please ensure the backend is running on port 5000.',
        ts: new Date()
      }]);
    }
    setLoading(false);
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const formatTime = (d) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const LANG_OPTIONS = [
    { code: 'en-IN', label: '🇮🇳 English (India)' },
    { code: 'bn-IN', label: '🇧🇩 বাংলা (Bengali)' },
    { code: 'hi-IN', label: '🇮🇳 हिन्दी (Hindi)' },
    { code: 'en-US', label: '🇺🇸 English (US)' },
  ];

  return (
    <div>
      <style>{pulseStyle}</style>

      <p className="section-title">KrishiBot AI Assistant</p>
      <p className="section-sub">Powered by Groq · LLaMA 3.3 70B · Voice Input 🎙️ · Voice Output 🔊 · English & Bengali</p>

      <div className="grid-2" style={{ gap: 24, alignItems: 'flex-start' }}>

        {/* ── Chat window ───────────────────────────────────────────── */}
        <div>
          <div style={{ background: 'white', borderRadius: 'var(--radius)', boxShadow: 'var(--shadow)', border: '1px solid var(--gray-200)', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 210px)', maxHeight: 680 }}>

            {/* Header */}
            <div style={{
              padding: '12px 18px',
              background: 'linear-gradient(90deg, var(--green-800), var(--green-700))',
              color: 'white', borderRadius: 'var(--radius) var(--radius) 0 0',
              display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0,
            }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#69F0AE', boxShadow: '0 0 6px #69F0AE' }} />
              <span style={{ fontWeight: 700, fontSize: 15 }}>🌾 KrishiBot</span>

              {/* TTS toggle */}
              <button
                onClick={() => { setTtsEnabled(p => !p); if (ttsEnabled) stopSpeaking(); }}
                title={ttsEnabled ? 'Disable auto-speak' : 'Enable auto-speak'}
                style={{
                  marginLeft: 'auto', background: ttsEnabled ? 'rgba(255,255,255,0.18)' : 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(255,255,255,0.3)', borderRadius: 6,
                  color: 'white', fontSize: 12, padding: '3px 10px', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 5,
                }}
              >
                {ttsEnabled ? '🔊 Auto-Speak ON' : '🔇 Auto-Speak OFF'}
              </button>

              <span style={{ fontSize: 11, opacity: 0.7 }}>Groq · LLaMA 3.3</span>
            </div>

            {/* Voice language selector */}
            <div style={{
              padding: '8px 14px', background: 'var(--green-50)',
              borderBottom: '1px solid var(--green-100)',
              display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0,
            }}>
              <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--green-700)' }}>🌐 Voice Language:</span>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {LANG_OPTIONS.map(l => (
                  <button
                    key={l.code}
                    onClick={() => setSttLang(l.code)}
                    style={{
                      padding: '3px 10px', borderRadius: 20, fontSize: 11, cursor: 'pointer',
                      border: `1.5px solid ${sttLang === l.code ? 'var(--green-700)' : 'var(--gray-200)'}`,
                      background: sttLang === l.code ? 'var(--green-700)' : 'white',
                      color: sttLang === l.code ? 'white' : 'var(--gray-600)',
                      fontWeight: sttLang === l.code ? 700 : 400,
                      transition: 'all 0.15s',
                    }}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
            </div>

            {/* STT status banner */}
            {sttStatus && (
              <div style={{
                padding: '7px 16px', background: isRecording ? '#FFF0F0' : 'var(--green-50)',
                borderBottom: `1px solid ${isRecording ? '#FFCDD2' : 'var(--green-100)'}`,
                fontSize: 13, color: isRecording ? '#c62828' : 'var(--green-800)',
                fontWeight: 600, flexShrink: 0,
                display: 'flex', alignItems: 'center', gap: 8,
              }}>
                {isRecording && <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#ef4444', display: 'inline-block', animation: 'pulse 1s infinite' }} />}
                {sttStatus}
              </div>
            )}

            {/* Messages */}
            <div style={{
              flex: 1, overflowY: 'auto', padding: '16px',
              display: 'flex', flexDirection: 'column', gap: 14,
              background: 'var(--gray-100)',
            }}>
              {messages.map((m, i) => (
                <div key={i} className="msg-anim" style={{ display: 'flex', flexDirection: 'column', alignItems: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
                  {m.role === 'assistant' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                      <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--green-700)' }}>🤖 KrishiBot</span>
                      {m.source && <span style={{ fontSize: 10, color: 'var(--gray-600)' }}>({m.source})</span>}
                      {/* Per-message speak button */}
                      <SpeakButton
                        text={m.content}
                        isSpeaking={speakingIdx === i}
                        onToggle={(text) => speak(text, i)}
                      />
                    </div>
                  )}
                  <div className={`chat-bubble ${m.role === 'user' ? 'user' : 'bot'}`}
                    style={{ border: speakingIdx === i ? '2px solid var(--green-400)' : undefined }}>
                    {m.content}
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--gray-600)', margin: '2px 4px' }}>
                    {formatTime(m.ts || new Date())}
                    {m.role === 'user' && m.isVoice && <span style={{ marginLeft: 4 }}>🎙️</span>}
                  </div>
                </div>
              ))}

              {loading && (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--green-700)', marginBottom: 4 }}>🤖 KrishiBot</div>
                  <div className="chat-bubble bot"><TypingDots /></div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input area */}
            <div style={{
              display: 'flex', gap: 8, padding: '12px 14px',
              background: 'white', borderTop: '1px solid var(--gray-200)',
              borderRadius: '0 0 var(--radius) var(--radius)',
              alignItems: 'flex-end', flexShrink: 0,
            }}>
              {/* Mic button */}
              <MicButton
                isRecording={isRecording}
                isSupported={sttSupported}
                onClick={toggleRecording}
                disabled={loading}
              />

              <textarea
                className="chat-input"
                rows={2}
                placeholder={isRecording ? '🎙️ Listening… speak now' : 'Type or use 🎙️ to speak (English, বাংলা, हिन्दी)'}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                style={{ flex: 1, resize: 'none', transition: 'border-color 0.15s',
                  borderColor: isRecording ? '#ef4444' : undefined }}
              />

              {/* Stop speaking button (shown while TTS active) */}
              {speakingIdx !== null && (
                <button
                  onClick={stopSpeaking}
                  title="Stop speaking"
                  style={{
                    width: 42, height: 42, borderRadius: '50%', border: 'none',
                    background: '#ef4444', color: 'white', fontSize: 16,
                    cursor: 'pointer', flexShrink: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}
                >
                  ⏹
                </button>
              )}

              <button
                className="btn btn-primary"
                style={{ alignSelf: 'flex-end', height: 42, flexShrink: 0 }}
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
              >
                {loading ? <span className="spinner" /> : '➤ Send'}
              </button>
            </div>
          </div>

          {/* Voice help note */}
          <div style={{
            marginTop: 10, padding: '10px 14px',
            background: 'var(--green-50)', borderRadius: 8,
            border: '1px solid var(--green-100)',
            fontSize: 12, color: 'var(--green-800)', lineHeight: 1.7,
          }}>
            <strong>🎙️ Voice Tips:</strong> Click the mic → speak your question → it auto-sends.
            &nbsp;|&nbsp; <strong>🔊 Read Aloud:</strong> Click 🔊 on any reply to hear it spoken.
            &nbsp;|&nbsp; Works best in <strong>Chrome / Edge</strong>.
            &nbsp;|&nbsp; Allow microphone when browser asks.
          </div>
        </div>

        {/* ── Sidebar ───────────────────────────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Voice assistant card */}
          <div className="card" style={{ background: 'linear-gradient(135deg, var(--green-900), var(--green-800))', border: 'none' }}>
            <div style={{ color: 'white' }}>
              <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
                🎙️ Voice Assistant Guide
              </div>
              {[
                ['🔴 Red mic', 'Recording in progress'],
                ['⏹ Square', 'Stop recording / speaking'],
                ['🔊 Speaker', 'Read this message aloud'],
                ['🔇 Muted', 'Stop current speech'],
                ['Auto-Speak ON', 'Replies read automatically'],
              ].map(([icon, desc]) => (
                <div key={icon} style={{ display: 'flex', gap: 10, marginBottom: 7, fontSize: 12, alignItems: 'center' }}>
                  <span style={{ background: 'rgba(255,255,255,0.12)', borderRadius: 5, padding: '2px 7px', fontWeight: 700, color: 'var(--yellow)', minWidth: 90, textAlign: 'center', flexShrink: 0 }}>{icon}</span>
                  <span style={{ color: 'var(--mint, #B7E4C7)' }}>{desc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* TTS voice selector */}
          {availableVoices.length > 0 && (
            <div className="card">
              <div className="card-header">
                <div className="card-icon">🔊</div>
                <h3>Voice Selection</h3>
              </div>
              <div className="form-group">
                <label className="form-label">Speak replies using</label>
                <select
                  className="form-select"
                  value={ttsVoice?.name || ''}
                  onChange={e => setTtsVoice(availableVoices.find(v => v.name === e.target.value))}
                >
                  {availableVoices.map(v => (
                    <option key={v.name} value={v.name}>{v.name} ({v.lang})</option>
                  ))}
                </select>
              </div>
              <button
                className="btn btn-secondary"
                style={{ marginTop: 10, fontSize: 13 }}
                onClick={() => speak('Namaskar! I am KrishiBot, your farming advisor.', -1)}
              >
                🔊 Test Voice
              </button>
            </div>
          )}

          {/* Quick questions */}
          <div className="card">
            <div className="card-header">
              <div className="card-icon">💡</div>
              <h3>Quick Questions</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  className="btn btn-secondary"
                  style={{ justifyContent: 'flex-start', fontSize: 13, padding: '8px 14px' }}
                  onClick={() => sendMessage(s)}
                  disabled={loading}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Seasonal tips */}
          {tips.length > 0 && (
            <div className="card">
              <div className="card-header">
                <div className="card-icon">📅</div>
                <h3>Seasonal Tips</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {tips.map((t, i) => (
                  <div key={i} style={{ display: 'flex', gap: 10, fontSize: 13, lineHeight: 1.5, alignItems: 'flex-start' }}>
                    <span style={{ color: 'var(--green-600)', fontWeight: 700, flexShrink: 0 }}>✓</span>
                    <span>{t}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Info card */}
          <div className="card" style={{ background: 'var(--green-50)', borderColor: 'var(--green-100)' }}>
            <div style={{ fontSize: 13, color: 'var(--green-800)', lineHeight: 1.7 }}>
              <strong>📌 District:</strong> {district}<br />
              <strong>🔗 Model:</strong> LLaMA 3.3 70B (Groq)<br />
              <strong>🌐 Voice Input:</strong> English · বাংলা · हिन्दी<br />
              <strong>🔊 Voice Output:</strong> Browser TTS<br /><br />
              <em style={{ fontSize: 11, color: 'var(--gray-600)' }}>
                Voice features use browser Web Speech API — no extra setup needed. Set GROQ_API_KEY for full AI.
              </em>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
