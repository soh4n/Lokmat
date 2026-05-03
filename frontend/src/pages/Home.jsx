import { useState, useRef, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { sendChatStream, getLiveElection } from '../services/api.js';
import './Home.css';

export default function Home() {
  const { t, lang } = useLanguage();
  const { isProfileComplete } = useAuth();

  // --- VoteSathi AI inline chat state ---
  const [messages, setMessages] = useState([
    {
      id: 'greeting',
      role: 'assistant',
      content: lang === 'hi'
        ? 'नमस्ते! मैं वोटसाथी AI हूं। मतदान, उम्मीदवारों, या प्रक्रिया के बारे में कुछ भी पूछें!'
        : "Namaste! I'm VoteSathi AI. Ask me anything about voting, candidates, or the electoral process.",
    },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const messagesContainerRef = useRef(null);
  const chatInputRef = useRef(null);

  // --- Online/Offline detection — per GEMINI.md real-world usability ---
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // --- Live Election Ticker (synced with India's election calendar) ---
  const [liveElection, setLiveElection] = useState(null);
  const [electionLoading, setElectionLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchLiveElection = async () => {
      try {
        const data = await getLiveElection();
        if (isMounted) {
          setLiveElection(data);
        }
      } catch {
        // Silently fail — banner just won't show
        if (isMounted) setLiveElection(null);
      } finally {
        if (isMounted) setElectionLoading(false);
      }
    };

    fetchLiveElection();

    // Refresh every 5 minutes to stay in sync
    const interval = setInterval(fetchLiveElection, 5 * 60 * 1000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  // Scroll within the chat container only — never scroll the page
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages, isLoading]);

  /** Format AI response: convert markdown-style to clean JSX */
  const formatResponse = useCallback((text) => {
    // Remove emojis
    const noEmoji = text.replace(/[\u{1F000}-\u{1FFFF}\u{2600}-\u{27BF}\u{FE00}-\u{FE0F}\u{1F900}-\u{1F9FF}\u{200D}\u{20E3}\u{E0020}-\u{E007F}]/gu, '').trim();
    // Split into lines and render
    const lines = noEmoji.split('\n');
    return lines.map((line, i) => {
      const trimmed = line.trim();
      if (!trimmed) return <br key={i} />;
      // Bold text: **text**
      const parts = trimmed.split(/(\*\*[^*]+\*\*)/g);
      const rendered = parts.map((part, j) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={j}>{part.slice(2, -2)}</strong>;
        }
        return part;
      });
      // Bullet points
      if (/^[-*•]\s/.test(trimmed) || /^\d+\.\s/.test(trimmed)) {
        const content = trimmed.replace(/^[-*•]\s*/, '').replace(/^\d+\.\s*/, '');
        const bulletParts = content.split(/(\*\*[^*]+\*\*)/g).map((part, j) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={j}>{part.slice(2, -2)}</strong>;
          }
          return part;
        });
        return <div key={i} className="vs-bullet">{bulletParts}</div>;
      }
      return <div key={i}>{rendered}</div>;
    });
  }, []);

  /** Send message via SSE streaming — first token <500ms per GEMINI.md */
  const sendMessage = async (text) => {
    if (!text.trim() || isLoading) return;
    if (!isOnline) return; // Don't send when offline

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setChatInput('');
    setIsLoading(true);

    // Add a streaming placeholder so the user sees tokens as they arrive
    const streamId = Date.now().toString() + '_streaming';
    setMessages((prev) => [...prev, {
      id: streamId,
      role: 'assistant',
      content: '',
      isStreaming: true,
    }]);

    const history = messages
      .filter((m) => m.id !== 'greeting')
      .map((m) => ({ role: m.role, content: m.content }));

    let fullText = '';

    try {
      await sendChatStream(
        text.trim(),
        history,
        '', // session_id
        // onChunk — append each token to the streaming message
        (chunk) => {
          fullText += chunk;
          setMessages((prev) => prev.map((m) =>
            m.id === streamId ? { ...m, content: fullText } : m
          ));
        },
        // onDone — replace streaming msg with final (adds suggestions)
        ({ suggestions }) => {
          setMessages((prev) => prev.map((m) =>
            m.id === streamId
              ? { ...m, isStreaming: false, suggestions: suggestions || [] }
              : m
          ));
          setIsLoading(false);
          chatInputRef.current?.focus();
        },
        // onError — replace streaming msg with error
        (errMsg) => {
          setMessages((prev) => prev.map((m) =>
            m.id === streamId
              ? {
                  ...m,
                  isStreaming: false,
                  content: lang === 'hi'
                    ? 'क्षमा करें, कुछ गलत हो गया। कृपया बाद में पुनः प्रयास करें।'
                    : `Sorry, something went wrong: ${errMsg}`,
                }
              : m
          ));
          setIsLoading(false);
          chatInputRef.current?.focus();
        },
      );
    } catch {
      // Network-level error (fetch itself failed)
      setMessages((prev) => prev.map((m) =>
        m.id === streamId
          ? {
              ...m,
              isStreaming: false,
              content: lang === 'hi'
                ? 'क्षमा करें, कुछ गलत हो गया। कृपया बाद में पुनः प्रयास करें।'
                : 'Sorry, something went wrong. Please try again later.',
            }
          : m
      ));
      setIsLoading(false);
      chatInputRef.current?.focus();
    }
  };

  /** Copy assistant message to clipboard — per GEMINI.md UX patterns */
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).catch(() => {});
  };

  /** Clear conversation — per GEMINI.md UX patterns */
  const clearConversation = () => {
    setMessages([{
      id: 'greeting',
      role: 'assistant',
      content: lang === 'hi'
        ? 'नमस्ते! मैं वोटसाथी AI हूं। मतदान, उम्मीदवारों, या प्रक्रिया के बारे में कुछ भी पूछें!'
        : "Namaste! I'm VoteSathi AI. Ask me anything about voting, candidates, or the electoral process.",
    }]);
  };

  const handleChatSubmit = (e) => { e.preventDefault(); sendMessage(chatInput); };
  const handleChip = (text) => { sendMessage(text); };

  return (
    <main className="page" role="main">
      {/* Offline banner — per GEMINI.md real-world usability */}
      {!isOnline && (
        <div className="offline-banner" role="alert" aria-live="assertive">
          <span className="material-symbols-outlined">wifi_off</span>
          <span>
            {lang === 'hi'
              ? 'आप ऑफ़लाइन हैं। इंटरनेट से जुड़ने पर AI असिस्टेंट काम करेगा।'
              : 'You are offline. The AI assistant will resume when you reconnect.'}
          </span>
        </div>
      )}

      <div className="page-content stagger-children">
        {/* Hero + VoteSathi AI — integrated as one section */}
        <section className="home-hero-chat" aria-label="Welcome and AI assistant">
          {/* Hero top */}
          <div className="home-hero" aria-label="Welcome banner">
            <img
              src="/hero-bg.png"
              alt=""
              className="home-hero-bg-img"
              aria-hidden="true"
            />
            <div className="home-hero-overlay" />
            <div className="home-hero-inner">
              <img
                src="/lokmat-logo.png"
                alt="LokMat voting hand logo"
                className="home-hero-logo"
              />
              <h1 className="home-hero-title">
                {lang === 'hi' ? 'आपका वोट आपकी आवाज़ है।' : 'Your vote is your voice.'}
              </h1>
              <p className="home-hero-subtitle">{t('hero_subtitle')}</p>
            </div>
          </div>

          {/* VoteSathi AI — seamlessly embedded below hero */}
          <div className="votesathi-embedded">
            <div className="votesathi-header">
              <div className="votesathi-header-left">
                <div className="votesathi-avatar">
                  <img src="/lokmat-logo.png" alt="" width="32" height="32" />
                </div>
                <div>
                  <h2>{t('ai_title')}</h2>
                  <p>{t('ai_subtitle')}</p>
                </div>
              </div>
              <div className="votesathi-header-actions">
                {messages.length > 1 && (
                  <button className="clear-chat-btn" onClick={clearConversation} aria-label="Clear conversation" title="Clear conversation">
                    <span className="material-symbols-outlined">delete_sweep</span>
                  </button>
                )}
              </div>
            </div>

            {/* Messages — container-scoped scroll to prevent page jumping */}
            <div
              ref={messagesContainerRef}
              className="votesathi-messages"
              role="log"
              aria-live="polite"
              aria-label={lang === 'hi' ? 'वार्तालाप इतिहास' : 'Conversation history'}
            >
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`vs-msg ${msg.role === 'user' ? 'vs-msg-user' : 'vs-msg-bot'}`}
                  aria-label={`${msg.role === 'user' ? 'You' : 'VoteSathi AI'}: ${msg.content}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="vs-msg-avatar">
                      <img src="/lokmat-logo.png" alt="" width="24" height="24" />
                    </div>
                  )}
                  <div className="vs-msg-bubble">
                    <div className="vs-msg-text">
                      {msg.role === 'assistant' ? formatResponse(msg.content) : msg.content}
                      {/* Streaming cursor — shown while tokens arrive */}
                      {msg.isStreaming && <span className="streaming-cursor" aria-hidden="true" />}
                    </div>
                    {msg.role === 'assistant' && msg.id !== 'greeting' && !msg.isStreaming && (
                      <button className="copy-btn" onClick={() => copyToClipboard(msg.content)} aria-label="Copy to clipboard" title="Copy">
                        <span className="material-symbols-outlined" style={{ fontSize: '14px' }}>content_copy</span>
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {/* Show typing dots only when no streaming message is present yet */}
              {isLoading && !messages.some((m) => m.isStreaming) && (
                <div className="vs-msg vs-msg-bot" aria-label="VoteSathi AI is typing">
                  <div className="vs-msg-avatar">
                    <img src="/lokmat-logo.png" alt="" width="24" height="24" />
                  </div>
                  <div className="vs-msg-bubble vs-typing">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              )}

            </div>

            {/* Chips */}
            {messages.length <= 1 && (
              <div className="votesathi-chips">
                <button className="chip-btn" onClick={() => handleChip(t('ai_chip_booth'))} disabled={isLoading}>{t('ai_chip_booth')}</button>
                <button className="chip-btn" onClick={() => handleChip(t('ai_chip_candidates'))} disabled={isLoading}>{t('ai_chip_candidates')}</button>
                <button className="chip-btn" onClick={() => handleChip(t('ai_chip_process'))} disabled={isLoading}>{t('ai_chip_process')}</button>
                <button className="chip-btn" onClick={() => handleChip(t('ai_chip_rights'))} disabled={isLoading}>{t('ai_chip_rights')}</button>
                <button className="chip-btn" onClick={() => handleChip(lang === 'hi' ? 'लोक सभा क्या है?' : 'What is Lok Sabha?')} disabled={isLoading}>
                  {lang === 'hi' ? 'लोक सभा क्या है?' : 'What is Lok Sabha?'}
                </button>
                <button className="chip-btn" onClick={() => handleChip(lang === 'hi' ? 'विधान सभा क्या है?' : 'What is Vidhan Sabha?')} disabled={isLoading}>
                  {lang === 'hi' ? 'विधान सभा क्या है?' : 'What is Vidhan Sabha?'}
                </button>
              </div>
            )}

            {/* Input */}
            <form className="votesathi-input-bar" onSubmit={handleChatSubmit}>
              <input
                ref={chatInputRef}
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder={t('ai_placeholder')}
                disabled={isLoading}
                aria-label={t('ai_placeholder')}
                autoComplete="off"
              />
              <button
                type="submit"
                className="votesathi-send-btn"
                disabled={!chatInput.trim() || isLoading}
                aria-label={lang === 'hi' ? 'भेजें' : 'Send'}
                aria-busy={isLoading}
              >
                <span className="material-symbols-outlined">
                  {isLoading ? 'hourglass_top' : 'send'}
                </span>
              </button>
            </form>
          </div>
        </section>

        {/* Registration Status — conditional on profile */}
        <section className={`status-card ${isProfileComplete ? 'status-registered' : 'status-incomplete'}`} aria-label="Voter registration status">
          <div className="status-card-left">
            <span
              className="material-symbols-outlined"
              style={{
                color: isProfileComplete ? 'var(--green-india)' : 'var(--saffron)',
                fontVariationSettings: "'FILL' 1",
              }}
            >
              {isProfileComplete ? 'verified_user' : 'info'}
            </span>
            <div>
              <h2 className="status-title">
                {isProfileComplete ? t('status_registered') : t('status_not_registered')}
              </h2>
              <p className="status-desc">
                {isProfileComplete ? t('status_registered_desc') : t('status_not_registered_desc')}
              </p>
            </div>
          </div>
          <Link to={isProfileComplete ? '/my-vote' : '/profile'} className="status-link">
            {isProfileComplete
              ? (lang === 'hi' ? 'विवरण देखें' : 'VIEW DETAILS')
              : (lang === 'hi' ? 'प्रोफ़ाइल भरें' : 'COMPLETE PROFILE')}
          </Link>
        </section>

        {/* Quick Access Bento Grid */}
        <section className="bento-grid" aria-label="Quick access">
          <Link to="/my-vote" className="bento-card bento-full card-interactive">
            <div className="icon-circle icon-circle-saffron">
              <span className="material-symbols-outlined">assignment_ind</span>
            </div>
            <div className="bento-text">
              <h3>{t('home_voter_slip')}</h3>
              <p>{t('home_voter_slip_desc')}</p>
            </div>
            <span className="material-symbols-outlined bento-arrow">arrow_forward_ios</span>
          </Link>

          <Link to="/live" className="bento-card card-interactive">
            <div className="icon-circle icon-circle-navy">
              <span className="material-symbols-outlined">groups</span>
            </div>
            <h3>{t('home_booth_queue')}</h3>
            <p>{t('home_booth_queue_desc')}</p>
          </Link>

          <Link to="/election" className="bento-card card-interactive">
            <div className="icon-circle icon-circle-amber">
              <span className="material-symbols-outlined">person_search</span>
            </div>
            <h3>{t('home_candidates')}</h3>
            <p>{t('home_candidates_desc')}</p>
          </Link>

          <Link to="/election" className="bento-card card-interactive">
            <div className="icon-circle icon-circle-green">
              <span className="material-symbols-outlined">how_to_vote</span>
            </div>
            <h3>{lang === 'hi' ? 'आगामी चुनाव' : 'Upcoming Elections'}</h3>
            <p>{lang === 'hi' ? 'भारत 2024–2028' : 'India 2024–2028'}</p>
          </Link>

          <Link to="/volunteer" className="bento-card card-interactive">
            <div className="icon-circle icon-circle-saffron">
              <span className="material-symbols-outlined">volunteer_activism</span>
            </div>
            <h3>{t('home_volunteer')}</h3>
            <p>{t('home_volunteer_desc')}</p>
          </Link>
        </section>

        {/* Live Election Banner — only shows when an election is actually live */}
        {!electionLoading && liveElection?.is_live && liveElection.election && (
          <section className="live-election-banner" aria-label={lang === 'hi' ? 'लाइव चुनाव' : 'Live Election'} role="region">
            <div className="live-election-header">
              <div className="live-election-badge">
                <span className="live-pulse" />
                <span>{lang === 'hi' ? 'लाइव' : 'LIVE'}</span>
              </div>
              <span className="live-election-type">
                {liveElection.election.election_type === 'LOK_SABHA'
                  ? (lang === 'hi' ? 'लोक सभा' : 'Lok Sabha')
                  : liveElection.election.election_type === 'VIDHAN_SABHA'
                  ? (lang === 'hi' ? 'विधान सभा' : 'Vidhan Sabha')
                  : liveElection.election.election_type === 'BY_ELECTION'
                  ? (lang === 'hi' ? 'उपचुनाव' : 'By-Election')
                  : liveElection.election.election_type}
              </span>
            </div>

            <h2 className="live-election-name">
              {lang === 'hi' ? liveElection.election.name_hi : liveElection.election.name_en}
            </h2>

            <p className="live-election-status">
              {lang === 'hi' ? liveElection.status_message_hi : liveElection.status_message_en}
            </p>

            <div className="live-election-meta">
              <div className="live-election-meta-item">
                <span className="material-symbols-outlined">location_on</span>
                <span>{liveElection.election.states.slice(0, 3).join(', ')}{liveElection.election.states.length > 3 ? ` +${liveElection.election.states.length - 3}` : ''}</span>
              </div>
              <div className="live-election-meta-item">
                <span className="material-symbols-outlined">chair</span>
                <span>{liveElection.election.total_seats} {lang === 'hi' ? 'सीटें' : 'seats'}</span>
              </div>
              {liveElection.election.total_phases > 1 && (
                <div className="live-election-meta-item">
                  <span className="material-symbols-outlined">calendar_today</span>
                  <span>{liveElection.election.total_phases} {lang === 'hi' ? 'चरण' : 'phases'}</span>
                </div>
              )}
            </div>

            {/* Phase progress bar */}
            <div className="live-election-progress">
              <div className="live-election-progress-info">
                {liveElection.current_phase && liveElection.election.total_phases > 1 && (
                  <span className="live-phase-label">
                    {lang === 'hi' ? `चरण ${liveElection.current_phase}` : `Phase ${liveElection.current_phase}`}
                    <span className="live-phase-total">/ {liveElection.election.total_phases}</span>
                  </span>
                )}
                <span className="live-progress-pct">{liveElection.progress_percent}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-bar-fill live-progress-fill"
                  style={{ width: `${liveElection.progress_percent}%` }}
                />
              </div>
            </div>

            {/* Countdown to next phase */}
            {liveElection.days_until_next != null && liveElection.days_until_next > 0 && (
              <div className="live-election-countdown">
                <span className="material-symbols-outlined">timer</span>
                <span>
                  {lang === 'hi'
                    ? `अगले चरण तक ${liveElection.days_until_next} दिन`
                    : `${liveElection.days_until_next} day${liveElection.days_until_next !== 1 ? 's' : ''} until next phase`}
                </span>
              </div>
            )}

            {/* POLLING TODAY highlight */}
            {liveElection.days_until_next === 0 && liveElection.status === 'polling' && (
              <div className="live-election-today" role="alert" aria-live="assertive">
                <span className="material-symbols-outlined">how_to_vote</span>
                <strong>{lang === 'hi' ? '🗳️ आज मतदान है! वोट करने जाएं!' : '🗳️ POLLING TODAY! Go vote!'}</strong>
              </div>
            )}
          </section>
        )}

        {/* Helpline Bar */}
        <section className="helpline-bar" aria-label="Election helpline">
          <div className="helpline-left">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
              emergency
            </span>
            <div>
              <strong>{t('helpline_title')}</strong>
              <span>{lang === 'hi' ? 'चुनाव हेल्पलाइन' : 'Election Helpline'}</span>
            </div>
          </div>
          <a href="tel:1950" className="btn btn-outline btn-sm">{t('helpline_call')}</a>
        </section>
      </div>
    </main>
  );
}
