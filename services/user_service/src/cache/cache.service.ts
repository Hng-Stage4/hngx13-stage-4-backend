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
        // Enable lazy connect - don't fail on startup if Redis is down
        lazyConnect: false,
        // Retry connection automatically
        enableReadyCheck: true,
      });

      // Test connection (with timeout to avoid blocking startup)
      try {
        await Promise.race([
          this.redisClient.ping(),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Connection timeout')), 5000),
          ),
        ]);
        console.log('✅ Redis connection established');
        console.log(`🔌 Redis: ${host}:${port}`);
      } catch (pingError) {
        console.warn(
          '⚠️ Redis connection test failed, but service will continue:',
          pingError instanceof Error ? pingError.message : 'Unknown error',
        );
        console.warn(
          '⚠️ Redis operations will fail until connection is established',
        );
        // Don't throw - allow service to start without Redis
        // Health check will report Redis as down
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Redis initialization failed:', errorMessage);
      console.warn(
        '⚠️ Service will continue without Redis. Health check will report Redis as down.',
      );
      // Don't throw - allow service to start without Redis
      // This makes the service more resilient
    }
  }

  async onModuleDestroy() {
    if (this.redisClient) {
      try {
        await this.redisClient.quit();
      } catch (error) {
        console.error('Error closing Redis connection:', error);
      }
    }
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
    // Check if client is initialized
    if (!this.redisClient) {
      return {
        status: 'disconnected',
        isConnected: false,
        host: 'unknown',
        port: 6379,
      };
    }

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
