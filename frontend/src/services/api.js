/**
 * LokMat Frontend — Typed API client.
 *
 * Centralizes all backend HTTP calls. Uses fetch with structured error handling.
 * Per GEMINI.md: server state via typed wrappers, no raw fetch in components.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generic API error with structured detail.
 */
class ApiError extends Error {
  constructor(status, detail) {
    super(detail);
    this.status = status;
    this.name = 'ApiError';
  }
}

/**
 * Make an authenticated API request.
 * @param {string} path - API endpoint path (e.g. '/auth/send-otp')
 * @param {object} options - Fetch options (method, body, etc.)
 * @param {string|null} token - JWT auth token
 * @returns {Promise<any>} Parsed JSON response
 */
async function apiRequest(path, options = {}, token = null) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new ApiError(res.status, body.detail || 'Request failed');
  }

  return res.json();
}

// --- Auth API ---

/**
 * Send OTP to the given phone number.
 * @param {string} phone - Phone with +91 prefix (e.g. '+919876543210')
 * @returns {Promise<{message: string, phone: string, demo_otp: string}>}
 */
export async function sendOtp(phone) {
  return apiRequest('/auth/send-otp', {
    method: 'POST',
    body: JSON.stringify({ phone }),
  });
}

/**
 * Verify OTP and get JWT access token.
 * @param {string} phone - Phone with +91 prefix
 * @param {string} otp - 6-digit OTP code
 * @returns {Promise<{access_token: string, token_type: string, expires_in: number}>}
 */
export async function verifyOtp(phone, otp) {
  return apiRequest('/auth/verify-otp', {
    method: 'POST',
    body: JSON.stringify({ phone, otp }),
  });
}

// --- Voter Profile API ---

/**
 * Create or update voter profile.
 * @param {object} profile - Voter profile data
 * @param {string} token - JWT auth token
 * @returns {Promise<object>} Saved profile response
 */
export async function saveProfile(profile, token) {
  return apiRequest('/voter/profile', {
    method: 'POST',
    body: JSON.stringify(profile),
  }, token);
}

/**
 * Get current user's voter profile.
 * @param {string} token - JWT auth token
 * @returns {Promise<object>} Voter profile
 */
export async function getProfile(token) {
  return apiRequest('/voter/profile', { method: 'GET' }, token);
}

// --- Chat API ---

/**
 * Send a message to the AI election assistant.
 * @param {string} message - User message text
 * @param {Array} history - Previous chat messages [{role, content}]
 * @param {string} sessionId - Chat session ID
 * @returns {Promise<{message: string, intent: string, session_id: string, suggestions: string[]}>}
 */
export async function sendChatMessage(message, history = [], sessionId = '') {
  return apiRequest('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      history,
      session_id: sessionId,
    }),
  });
}

/**
 * Stream a chat response via Server-Sent Events (SSE).
 *
 * Yields parsed SSE events as they arrive from the /chat/stream endpoint.
 * First token appears within ~500ms per GEMINI.md UX requirements.
 *
 * @param {string} message - User message text
 * @param {Array} history - Previous chat messages [{role, content}]
 * @param {string} sessionId - Chat session ID
 * @param {function} onChunk - Called with each text chunk: (text: string) => void
 * @param {function} onDone - Called when stream ends: ({suggestions, model}) => void
 * @param {function} onError - Called on error: (message: string) => void
 * @returns {Promise<void>}
 */
export async function sendChatStream(message, history = [], sessionId = '', onChunk, onDone, onError) {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history, session_id: sessionId }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Stream request failed' }));
    onError?.(body.detail || 'Stream request failed');
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Process all complete SSE messages (separated by \n\n)
    const parts = buffer.split('\n\n');
    buffer = parts.pop(); // Keep incomplete last part

    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith('data: ')) continue;

      const raw = line.slice(6); // Strip "data: " prefix
      try {
        const event = JSON.parse(raw);
        if (event.type === 'chunk') {
          onChunk?.(event.text);
        } else if (event.type === 'done') {
          onDone?.({ suggestions: event.suggestions || [], model: event.model });
        } else if (event.type === 'error') {
          onError?.(event.message || 'Unknown streaming error');
        }
      } catch {
        // Malformed SSE event — skip silently
      }
    }
  }
}

// --- Health API ---

/**
 * Check backend health status.
 * @returns {Promise<{status: string, gemini: string, version: string}>}
 */
export async function checkHealth() {
  return apiRequest('/health', { method: 'GET' });
}

// --- Elections API ---

/**
 * Get the currently live election (if any).
 * Returns is_live: false if no election is active.
 * @returns {Promise<{is_live: boolean, election: object|null, status: string, current_phase: number, progress_percent: number}>}
 */
export async function getLiveElection() {
  return apiRequest('/elections/live', { method: 'GET' });
}

/**
 * Get upcoming elections sorted by polling date.
 * @returns {Promise<{elections: object[]}>}
 */
export async function getUpcomingElections() {
  return apiRequest('/elections/upcoming', { method: 'GET' });
}
