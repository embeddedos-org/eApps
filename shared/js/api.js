/**
 * EoS Shared — API Client
 * Used by: extensions, desktop (Electron), web apps
 */

import auth from './auth.js';

export class EosApiClient {
  constructor(config = {}) {
    this.baseUrl = config.baseUrl || 'https://api.embeddedos.org';
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...auth.getAuthHeaders(),
      ...options.headers,
    };

    const res = await fetch(url, { ...options, headers });

    if (!res.ok) {
      const error = new Error(`API ${res.status}: ${res.statusText}`);
      error.status = res.status;
      try { error.body = await res.json(); } catch {}
      throw error;
    }

    return res.json();
  }

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  post(endpoint, body) {
    return this.request(endpoint, { method: 'POST', body: JSON.stringify(body) });
  }

  put(endpoint, body) {
    return this.request(endpoint, { method: 'PUT', body: JSON.stringify(body) });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

export default new EosApiClient();
