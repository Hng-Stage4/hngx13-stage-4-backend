import { Injectable } from '@nestjs/common';
import { readFileSync } from 'fs';
import { join } from 'path';
import { DatabaseService } from '../database/database.service';
import { CacheService } from '../cache/cache.service';

@Injectable()
export class HealthService {
  private readonly startTime = Date.now();

  constructor(
    private readonly databaseService: DatabaseService,
    private readonly cacheService: CacheService,
  ) {}

  /**
   * Check database connection status
   */
  async checkDatabase(): Promise<{ status: string }> {
    try {
      const dbStatus = await this.databaseService.getConnectionStatus();
      return {
        status: dbStatus.isConnected ? 'up' : 'down',
      };
    } catch {
      return {
        status: 'down',
      };
    }
  }

  /**
   * Check Redis connection status
   */
  async checkRedis(): Promise<{ status: string }> {
    try {
      const redisStatus = await this.cacheService.getConnectionStatus();
      return {
        status: redisStatus.isConnected ? 'up' : 'down',
      };
    } catch {
      return {
        status: 'down',
      };
    }
  }

  /**
   * Get service uptime in seconds
   */
  getUptime(): number {
    return Math.floor((Date.now() - this.startTime) / 1000);
  }

  /**
   * Get service version from package.json
   */
  getVersion(): string {
    try {
      // Try multiple possible paths (local dev vs Docker)
      const possiblePaths = [
        join(process.cwd(), 'package.json'),
        join(__dirname, '../../package.json'),
        join(__dirname, '../../../package.json'),
      ];

      for (const packageJsonPath of possiblePaths) {
        try {
          const packageJson = JSON.parse(
            readFileSync(packageJsonPath, 'utf-8'),
          ) as { version?: string };
          if (packageJson.version) {
            return packageJson.version;
          }
        } catch {
          // Try next path
          continue;
        }
      }
      return '0.0.1';
    } catch {
      return '0.0.1';
    }
  }

  /**
   * Get comprehensive health status
   */
  async getHealthStatus(): Promise<{
    status: 'ok' | 'error';
    database: 'up' | 'down';
    redis: 'up' | 'down';
    uptime: number;
    version: string;
    timestamp: string;
  }> {
    const [databaseStatus, redisStatus] = await Promise.all([
      this.checkDatabase(),
      this.checkRedis(),
    ]);

    const database = databaseStatus.status as 'up' | 'down';
    const redis = redisStatus.status as 'up' | 'down';
    const overallStatus: 'ok' | 'error' =
      database === 'up' && redis === 'up' ? 'ok' : 'error';

    return {
      status: overallStatus,
      database,
      redis,
      uptime: this.getUptime(),
      version: this.getVersion(),
      timestamp: new Date().toISOString(),
    };
  }
}
