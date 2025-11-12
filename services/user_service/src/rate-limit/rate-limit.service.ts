import { Injectable } from '@nestjs/common';
import { CacheService } from '../cache/cache.service';

@Injectable()
export class RateLimitService {
  constructor(private readonly cacheService: CacheService) {}

  /**
   * Check rate limit for a user on a specific endpoint
   * @param userId - User ID (or 'anonymous' if not authenticated)
   * @param endpoint - Endpoint path
   * @param limit - Maximum number of requests
   * @param ttl - Time window in seconds
   * @returns true if allowed, false if rate limit exceeded
   */
  async checkRateLimit(
    userId: string,
    endpoint: string,
    limit: number,
    ttl: number,
  ): Promise<boolean> {
    const key = `rate_limit:user:${userId}:${endpoint}`;
    const count = await this.cacheService.increment(key, ttl);

    return count <= limit;
  }

  /**
   * Check rate limit for an IP address
   * @param ip - IP address
   * @param limit - Maximum number of requests
   * @param ttl - Time window in seconds
   * @returns true if allowed, false if rate limit exceeded
   */
  async checkIpRateLimit(
    ip: string,
    limit: number,
    ttl: number,
  ): Promise<boolean> {
    const key = `rate_limit:ip:${ip}`;
    const count = await this.cacheService.increment(key, ttl);

    return count <= limit;
  }

  /**
   * Get current rate limit count for a user endpoint
   * Useful for debugging or showing remaining requests
   */
  async getRateLimitCount(userId: string, endpoint: string): Promise<number> {
    const key = `rate_limit:user:${userId}:${endpoint}`;
    const count = await this.cacheService.get(key);
    return count ? parseInt(count, 10) : 0;
  }

  /**
   * Get current rate limit count for an IP
   */
  async getIpRateLimitCount(ip: string): Promise<number> {
    const key = `rate_limit:ip:${ip}`;
    const count = await this.cacheService.get(key);
    return count ? parseInt(count, 10) : 0;
  }

  /**
   * Reset rate limit for a user endpoint
   * Useful for testing or admin operations
   */
  async resetRateLimit(userId: string, endpoint: string): Promise<void> {
    const key = `rate_limit:user:${userId}:${endpoint}`;
    await this.cacheService.delete(key);
  }

  /**
   * Reset rate limit for an IP
   */
  async resetIpRateLimit(ip: string): Promise<void> {
    const key = `rate_limit:ip:${ip}`;
    await this.cacheService.delete(key);
  }
}
