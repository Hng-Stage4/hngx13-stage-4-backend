import { Injectable } from '@nestjs/common';
import { CacheService } from '../cache/cache.service';
import { ConfigService } from '@nestjs/config';
import * as crypto from 'crypto';

@Injectable()
export class TokenBlacklistService {
  constructor(
    private readonly cacheService: CacheService,
    private readonly configService: ConfigService,
  ) {}

  /**
   * Hash token for storage
   */
  private hashToken(token: string): string {
    return crypto.createHash('sha256').update(token).digest('hex');
  }

  /**
   * Get TTL from JWT expires_in config (default 30 minutes)
   */
  private getTokenTTL(): number {
    const expiresIn = this.configService.get<string>('JWT_EXPIRES_IN', '30m');
    // Parse "30m" to seconds
    if (expiresIn.endsWith('m')) {
      return parseInt(expiresIn.slice(0, -1)) * 60;
    }
    if (expiresIn.endsWith('h')) {
      return parseInt(expiresIn.slice(0, -1)) * 60 * 60;
    }
    return parseInt(expiresIn) || 1800; // default 30 minutes
  }

  /**
   * Blacklist a token
   */
  async blacklistToken(token: string, expiresIn?: number): Promise<void> {
    const tokenHash = this.hashToken(token);
    const ttl = expiresIn || this.getTokenTTL();

    await this.cacheService.set(`token_blacklist:${tokenHash}`, '1', ttl);
  }

  /**
   * Check if token is blacklisted
   */
  async isTokenBlacklisted(token: string): Promise<boolean> {
    const tokenHash = this.hashToken(token);
    const exists = await this.cacheService.exists(
      `token_blacklist:${tokenHash}`,
    );
    return exists;
  }
}
