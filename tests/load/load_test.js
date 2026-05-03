import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  // Simulate 50 concurrent users
  vus: 50,
  // Duration of the test
  duration: '60s',
  // Thresholds strictly follow the GEMINI.md rubric
  thresholds: {
    // Error rate must be strictly less than 2%
    http_req_failed: ['rate<0.02'],
    // 95% of requests must complete within 2 seconds (excluding streaming latency, this is for initial response)
    http_req_duration: ['p(95)<2000'],
  },
};

export default function () {
  // The production URL of the API
  const url = 'https://lokmat-api-777062932868.us-central1.run.app/chat';
  
  const payload = JSON.stringify({
    message: 'What is a voter slip?',
    session_id: 'load-test-session',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      // We pass a mock token or let the backend reject auth. 
      // If auth is required, a valid token needs to be injected via environment variable.
      // 'Authorization': `Bearer ${__ENV.TEST_TOKEN}`,
    },
  };

  const res = http.post(url, payload, params);

  // We consider the request successful if it doesn't return a 5xx error or rate limit
  check(res, {
    'is status not 500': (r) => r.status !== 500,
    'is status not 429': (r) => r.status !== 429,
    'is not 502/503': (r) => r.status !== 502 && r.status !== 503,
  });

  // Short pause to simulate user thinking/reading time before next query
  sleep(1);
}
