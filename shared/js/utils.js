/**
 * EoS Shared — Common Utilities
 * Used by: all JavaScript-based platforms
 */

export function debounce(fn, ms = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}

export function throttle(fn, ms = 300) {
  let last = 0;
  return (...args) => {
    const now = Date.now();
    if (now - last >= ms) {
      last = now;
      fn(...args);
    }
  };
}

export function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}

export function formatDate(date, locale = 'en-US') {
  return new Date(date).toLocaleDateString(locale, {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}

export function generateId(prefix = 'eos') {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

export function deepClone(obj) {
  return structuredClone ? structuredClone(obj) : JSON.parse(JSON.stringify(obj));
}

export function isElectron() {
  return typeof window !== 'undefined' &&
    typeof window.process === 'object' &&
    window.process.type === 'renderer';
}

export function isBrowser() {
  return typeof window !== 'undefined' && !isElectron();
}

export function isMobile() {
  return typeof navigator !== 'undefined' && /Mobi|Android/i.test(navigator.userAgent);
}
