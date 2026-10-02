/**
 * Client for the TODO REST API.
 *
 * This is the only module that knows endpoint URLs and the response envelope:
 *   success: { data: ... }
 *   failure: { error: { code, message, details? } }
 * Every failure is thrown as an ApiError, so callers handle a single error type.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(message, { status = null, code = 'unknown_error', details = null } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export function fetchTodos() {
  return request('/todos');
}

export function createTodo(description) {
  return request('/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ description }),
  });
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: { Accept: 'application/json', ...options.headers },
    });
  } catch (error) {
    // fetch only rejects when no HTTP response arrived at all
    // (server down, DNS failure, request blocked by CORS).
    throw new ApiError('Unable to reach the server. Please check your connection and try again.', {
      code: 'network_error',
    });
  }

  const body = await parseJsonSafely(response);

  // fetch resolves for every HTTP status, so 4xx/5xx must be detected here.
  if (!response.ok) {
    const error = (body && body.error) || {};
    throw new ApiError(error.message || `Request failed with status ${response.status}.`, {
      status: response.status,
      code: error.code || 'http_error',
      details: error.details || null,
    });
  }

  if (body === null || typeof body !== 'object' || !('data' in body)) {
    throw new ApiError('Received an unexpected response from the server.', {
      status: response.status,
      code: 'invalid_response',
    });
  }

  return body.data;
}

async function parseJsonSafely(response) {
  try {
    return await response.json();
  } catch (error) {
    // Non-JSON body, e.g. an HTML error page from a proxy.
    return null;
  }
}
