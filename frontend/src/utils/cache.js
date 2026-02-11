/**
 * Simple in-memory cache với TTL
 * Dùng để cache API responses
 */
class SimpleCache {
  constructor() {
    this.cache = new Map();
  }

  set(key, value, ttl = 60000) {
    // Default TTL: 60 seconds
    const expiry = Date.now() + ttl;
    this.cache.set(key, { value, expiry });
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }

    return item.value;
  }

  clear(pattern) {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    // Clear keys matching pattern
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }

  has(key) {
    const item = this.cache.get(key);
    if (!item) return false;
    
    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return false;
    }
    
    return true;
  }
}

export const apiCache = new SimpleCache();

/**
 * Wrapper function để cache API calls
 */
export async function cachedApiCall(key, apiFunction, ttl = 60000) {
  // Check cache first
  const cached = apiCache.get(key);
  if (cached) {
    return cached;
  }

  // Call API
  const result = await apiFunction();
  
  // Store in cache
  apiCache.set(key, result, ttl);
  
  return result;
}
