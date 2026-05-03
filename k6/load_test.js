/**
 * LokMat — k6 Load Test
 *
 * Target: 50 concurrent users, <2% error rate, p95 latency <2s
 *
 * Run with:
 *   k6 run k6/load_test.js
 *   k6 run --env API_URL=https://your-api.run.app k6/load_test.js
 *
 * Per GEMINI.md: validate 50 concurrent users with <2% errors.
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// --- Custom metrics ---
const errorRate = new Rate('errors');
const chatLatency = new Trend('chat_latency', true);
const intentLatency = new Trend('intent_latency', true);
const streamLatency = new Trend('stream_first_token_latency', true);

// --- Test config ---
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp up to 10 users
    { duration: '1m', target: 50 },    // Ramp up to 50 users
    { duration: '2m', target: 50 },    // Hold at 50 users
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    errors: ['rate<0.02'],              // <2% error rate
    http_req_duration: ['p(95)<2000'],  // p95 latency < 2s
    chat_latency: ['p(95)<3000'],       // Chat can be slower (AI call)
    stream_first_token_latency: ['p(95)<1000'], // First token < 1s per GEMINI.md
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

// Sample election questions for realistic load
const QUESTIONS = [
  'How do I find my polling booth?',
  'What documents do I need to vote?',
  'What is NOTA?',
  'How can I check my name on the voter list?',
  'What is the voting age in India?',
  'How do I apply for a postal ballot?',
  'What is EVM?',
  'Tell me about Lok Sabha elections',
  'How do I update my voter ID address?',
  'What is the Election Commission of India?',
];

function randomQuestion() {
  return QUESTIONS[Math.floor(Math.random() * QUESTIONS.length)];
}

// --- Test Scenarios ---

export default function () {
  const headers = { 'Content-Type': 'application/json' };

  // 1. Health check (lightweight — always included)
  const healthRes = http.get(`${BASE_URL}/health`, { headers });
  check(healthRes, {
    'health returns 200': (r) => r.status === 200,
    'health status ok or degraded': (r) => {
      const body = JSON.parse(r.body);
      return ['ok', 'degraded'].includes(body.status);
    },
  });
  errorRate.add(healthRes.status !== 200);

  sleep(0.5);

  // 2. Chat request (AI inference — heaviest endpoint)
  const chatPayload = JSON.stringify({
    message: randomQuestion(),
    history: [],
    session_id: `k6-${__VU}-${__ITER}`,
  });

  const chatStart = Date.now();
  const chatRes = http.post(`${BASE_URL}/chat`, chatPayload, { headers });
  chatLatency.add(Date.now() - chatStart);

  check(chatRes, {
    'chat returns 200 or 429': (r) => [200, 429].includes(r.status),
    'chat response has message': (r) => {
      if (r.status !== 200) return true; // 429 is acceptable under load
      const body = JSON.parse(r.body);
      return typeof body.message === 'string' && body.message.length > 0;
    },
    'chat response has session_id': (r) => {
      if (r.status !== 200) return true;
      const body = JSON.parse(r.body);
      return typeof body.session_id === 'string';
    },
  });
  errorRate.add(chatRes.status >= 500); // 5xx = error; 429 = acceptable

  sleep(1);

  // 3. Elections check (no AI call — fast)
  const electionsRes = http.get(`${BASE_URL}/elections/live`, { headers });
  check(electionsRes, {
    'elections returns 200': (r) => r.status === 200,
    'elections has is_live field': (r) => {
      const body = JSON.parse(r.body);
      return typeof body.is_live === 'boolean';
    },
  });
  errorRate.add(electionsRes.status >= 500);

  // 4. Stream chat request — verify SSE endpoint is live under load
  // k6 doesn't natively handle SSE chunked reads, so we measure to-response latency
  const streamPayload = JSON.stringify({
    message: randomQuestion(),
    history: [],
    session_id: `k6-stream-${__VU}-${__ITER}`,
  });

  const streamStart = Date.now();
  const streamRes = http.post(`${BASE_URL}/chat/stream`, streamPayload, { headers });
  streamLatency.add(Date.now() - streamStart);

  check(streamRes, {
    'stream returns 200 or 429': (r) => [200, 429].includes(r.status),
    'stream response has SSE data': (r) => {
      if (r.status !== 200) return true;
      return r.body.includes('data:');
    },
  });
  errorRate.add(streamRes.status >= 500);

  sleep(1);
}

/**
 * Summary handler — prints a human-readable summary at the end.
 */
export function handleSummary(data) {
  const errorPct = (data.metrics.errors?.values?.rate * 100 || 0).toFixed(2);
  const p95 = (data.metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(0);
  const chatP95 = (data.metrics.chat_latency?.values?.['p(95)'] || 0).toFixed(0);

  console.log(`
=== LokMat Load Test Summary ===
Total requests:   ${data.metrics.http_reqs?.values?.count || 0}
Error rate:       ${errorPct}% (threshold: <2%)
p95 latency:      ${p95}ms (threshold: <2000ms)
Chat p95 latency: ${chatP95}ms (threshold: <3000ms)
Pass: errors<2%   ${parseFloat(errorPct) < 2 ? 'YES' : 'NO'}
Pass: p95<2s      ${parseInt(p95) < 2000 ? 'YES' : 'NO'}
================================
  `);

  return {
    'k6/results.json': JSON.stringify(data, null, 2),
  };
}
