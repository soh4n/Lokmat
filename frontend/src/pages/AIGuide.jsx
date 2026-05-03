import { useState, useRef, useEffect, useCallback } from 'react';
import { useLanguage } from '../context/LanguageContext.jsx';
import { sendChatMessage } from '../services/api.js';
import './AIGuide.css';

const SYSTEM_PROMPT = `You are VoteSathi AI (वोटसाथी AI), a smart election process assistant for Indian voters.

Rules:
- Answer ONLY election-related queries (voting process, candidates, booth info, documents, rights, manifesto, timelines, EVM, NOTA, postal ballots, Lok Sabha, Vidhan Sabha, panchayat, etc.).
- Politely decline unrelated questions with: "I'm specialized in election guidance. Please ask about voting, candidates, or the electoral process."
- Be politically NEUTRAL. Never favor any party, candidate, or ideology.
- Provide factual, concise, and actionable answers.
- When the user asks in Hindi, respond in Hindi. When in English, respond in English.
- Use bullet points and simple language suitable for first-time voters.
- Reference official sources: Election Commission of India (ECI), NVSP portal, Voter Helpline 1950.
- For booth/slip queries, remind users to check their details on voters.eci.gov.in
- Keep responses under 200 words unless the topic requires detailed explanation.
- Include relevant emojis for readability (🗳️ 📋 🆔 📍).
- When asked about Lok Sabha: explain it is the lower house of Parliament with 543 seats, elected every 5 years.
- When asked about Vidhan Sabha: explain it is the state legislative assembly, seats vary by state, elected every 5 years.`;

export default function AIGuide() {
  const { t, lang } = useLanguage();
  const [messages, setMessages] = useState([
    {
      id: 'greeting',
      role: 'assistant',
      content: lang === 'hi'
        ? 'नमस्ते! 🙏 मैं वोटसाथी AI हूं — आपका स्मार्ट चुनाव प्रक्रिया सहायक। मतदान, उम्मीदवारों, या प्रक्रिया के बारे में कुछ भी पूछें!'
        : "Namaste! 🙏 I'm VoteSathi AI — your smart election process assistant. Ask me anything about voting, candidates, booths, or your rights!",
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const sendMessage = async (text) => {
    if (!text.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const history = messages
        .filter((m) => m.id !== 'greeting')
        .map((m) => ({ role: m.role, content: m.content }));

      // Route through backend API — no API key in frontend
      const data = await sendChatMessage(text.trim(), history);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + '_ai',
          role: 'assistant',
          content: data.message,
        },
      ]);
    } catch (error) {
      console.error('Chat API error:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + '_err',
          role: 'assistant',
          content: lang === 'hi'
            ? '⚠️ क्षमा करें, कुछ गलत हो गया। कृपया बाद में पुनः प्रयास करें या 1950 हेल्पलाइन पर कॉल करें।'
            : '⚠️ Sorry, something went wrong. Please try again later or call the 1950 helpline.',
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleChip = (chipText) => {
    sendMessage(chipText);
  };

  const chips = [
    { key: 'ai_chip_booth', label: t('ai_chip_booth') },
    { key: 'ai_chip_candidates', label: t('ai_chip_candidates') },
    { key: 'ai_chip_process', label: t('ai_chip_process') },
    { key: 'ai_chip_rights', label: t('ai_chip_rights') },
    { key: 'ai_chip_id', label: t('ai_chip_id') },
    { key: 'ai_chip_manifesto', label: t('ai_chip_manifesto') },
  ];

  return (
    <main className="page ai-page" role="main">
      <div className="ai-container">
        {/* Header */}
        <div className="ai-header">
          <div className="ai-header-left">
            <div className="ai-avatar">
              <img src="/lokmat-logo.png" alt="" width="32" height="32" />
            </div>
            <div>
              <h1>{t('ai_title')}</h1>
              <p>{t('ai_subtitle')}</p>
            </div>
          </div>
          <div className="ai-header-pill">
            <span className="live-dot" style={{ width: '6px', height: '6px' }} />
            <span>Gemini 2.5 Flash</span>
          </div>
        </div>

        {/* Messages */}
        <div
          className="ai-messages"
          role="log"
          aria-live="polite"
          aria-label={lang === 'hi' ? 'वार्तालाप इतिहास' : 'Conversation history'}
        >
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`ai-msg ${msg.role === 'user' ? 'ai-msg-user' : 'ai-msg-bot'}`}
              aria-label={`${msg.role === 'user' ? (lang === 'hi' ? 'आप' : 'You') : 'VoteSathi AI'}: ${msg.content}`}
            >
              {msg.role === 'assistant' && (
                <div className="ai-msg-avatar">
                  <img src="/lokmat-logo.png" alt="" width="24" height="24" />
                </div>
              )}
              <div className="ai-msg-bubble">
                <p style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="ai-msg ai-msg-bot" aria-label="VoteSathi AI is typing">
              <div className="ai-msg-avatar">
                <img src="/lokmat-logo.png" alt="" width="24" height="24" />
              </div>
              <div className="ai-msg-bubble ai-typing">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggestion Chips */}
        {messages.length <= 1 && (
          <div className="ai-chips">
            {chips.map((chip) => (
              <button
                key={chip.key}
                className="chip-btn"
                onClick={() => handleChip(chip.label)}
                disabled={isLoading}
              >
                {chip.label}
              </button>
            ))}
          </div>
        )}

        {/* Input Bar */}
        <form className="ai-input-bar" onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t('ai_placeholder')}
            disabled={isLoading}
            aria-label={t('ai_placeholder')}
            autoComplete="off"
          />
          <button
            type="submit"
            className="ai-send-btn"
            disabled={!input.trim() || isLoading}
            aria-label={lang === 'hi' ? 'भेजें' : 'Send'}
            aria-busy={isLoading}
          >
            <span className="material-symbols-outlined">
              {isLoading ? 'hourglass_top' : 'send'}
            </span>
          </button>
        </form>
      </div>
    </main>
  );
}
