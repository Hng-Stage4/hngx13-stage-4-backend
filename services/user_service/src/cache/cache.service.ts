import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import Redis from 'ioredis';

@Injectable()
export class CacheService implements OnModuleInit, OnModuleDestroy {
  private redisClient: Redis;

  constructor(private configService: ConfigService) {}

  async onModuleInit() {
    try {
      const host = this.configService.get<string>('REDIS_HOST', 'localhost');
      const port = this.configService.get<number>('REDIS_PORT', 6379);
      const password = this.configService.get<string>('REDIS_PASSWORD', '');

      this.redisClient = new Redis({
        host,
        port,
        password: password || undefined,
        retryStrategy: (times) => {
          const delay = Math.min(times * 50, 2000);
          return delay;
        },
        maxRetriesPerRequest: 3,
      });

      // Test connection
      await this.redisClient.ping();
      console.log('✅ Redis connection established');
      console.log(`🔌 Redis: ${host}:${port}`);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Redis connection failed:', errorMessage);
      throw error;
    }
  }

  async onModuleDestroy() {
    await this.redisClient.quit();
  }

  /**
   * Get value from Redis
   */
  async get(key: string): Promise<string | null> {
    try {
      return await this.redisClient.get(key);
    } catch (error) {
      console.error(`Error getting key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Set value in Redis with optional TTL (Time To Live) in seconds
   */
  async set(key: string, value: string, ttl?: number): Promise<void> {
    try {
      if (ttl) {
        await this.redisClient.setex(key, ttl, value);
      } else {
        await this.redisClient.set(key, value);
      }
    } catch (error) {
      console.error(`Error setting key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Delete key from Redis
   */
  async delete(key: string): Promise<number> {
    try {
      return await this.redisClient.del(key);
    } catch (error) {
      console.error(`Error deleting key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Check if key exists in Redis
   */
  async exists(key: string): Promise<boolean> {
    try {
      const result = await this.redisClient.exists(key);
      return result === 1;
    } catch (error) {
      console.error(`Error checking existence of key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Increment key value (for rate limiting counters)
   * Returns the new value after increment
   */
  async increment(key: string, ttl?: number): Promise<number> {
    try {
      const result = await this.redisClient.incr(key);
      if (ttl && result === 1) {
        // Set TTL only on first increment
        await this.redisClient.expire(key, ttl);
      }
      return result;
    } catch (error) {
      console.error(`Error incrementing key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get Redis connection status
   */
  async getConnectionStatus(): Promise<{
    status: string;
    isConnected: boolean;
    host: string;
    port: number;
  }> {
    try {
      await this.redisClient.ping();
      const options = this.redisClient.options;
      return {
        status: 'connected',
        isConnected: true,
        host: options.host || 'unknown',
        port: options.port || 6379,
      };
    } catch {
      const options = this.redisClient.options;
      return {
        status: 'disconnected',
        isConnected: false,
        host: options.host || 'unknown',
        port: options.port || 6379,
      };
    }
  }

  /**
   * Get Redis client (for advanced operations if needed)
   */
  getClient(): Redis {
    return this.redisClient;
  }
}
