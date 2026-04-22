/**
 * EoS Shared — Authentication Helpers
 * Used by: extensions, desktop (Electron), web apps
 */

export class EosAuth {
  constructor(config = {}) {
    this.baseUrl = config.baseUrl || 'https://embeddedos-org.github.io/api';
    this.tokenKey = config.tokenKey || 'eos_auth_token';
  }

  async login(email, password) {
    const res = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error(`Login failed: ${res.status}`);
    const data = await res.json();
    this.setToken(data.token);
    return data;
  }

  async logout() {
    this.clearToken();
  }

  getToken() {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem(this.tokenKey);
    }
    return null;
  }

  setToken(token) {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(this.tokenKey, token);
    }
  }

  clearToken() {
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(this.tokenKey);
    }
  }

  isAuthenticated() {
    return !!this.getToken();
  }

  getAuthHeaders() {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}

export default new EosAuth();
