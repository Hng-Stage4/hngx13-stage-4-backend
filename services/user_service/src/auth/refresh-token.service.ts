import { Injectable } from '@nestjs/common';
import { CacheService } from '../cache/cache.service';
import * as crypto from 'crypto';

interface RefreshTokenData {
  userId: string;
  expiresAt: number;
  createdAt: number;
}

@Injectable()
export class RefreshTokenService {
  private readonly ttl = 7 * 24 * 60 * 60; // 7 days in seconds

  constructor(private readonly cacheService: CacheService) {}

  /**
   * Hash token for storage (security)
   */
  private hashToken(token: string): string {
    return crypto.createHash('sha256').update(token).digest('hex');
  }

  /**
   * Store refresh token in Redis
   */
  async storeRefreshToken(
    token: string,
    userId: string,
    expiresIn?: number,
  ): Promise<void> {
    const tokenHash = this.hashToken(token);
    const ttl = expiresIn || this.ttl;
    const expiresAt = Date.now() + ttl * 1000;

    const data: RefreshTokenData = {
      userId,
      expiresAt,
      createdAt: Date.now(),
    };

    await this.cacheService.set(
      `refresh_token:${tokenHash}`,
      JSON.stringify(data),
      ttl,
    );
  }

  /**
   * Get refresh token data from Redis
   */
  async getRefreshToken(
    token: string,
  ): Promise<{ userId: string; expiresAt: number } | null> {
    const tokenHash = this.hashToken(token);
    const data = await this.cacheService.get(`refresh_token:${tokenHash}`);

    if (!data) {
      return null;
    }

    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const parsed: RefreshTokenData = JSON.parse(data);

    // Check if expired
    if (Date.now() > parsed.expiresAt) {
      await this.deleteRefreshToken(token);
      return null;
    }

    return {
      userId: parsed.userId,
      expiresAt: parsed.expiresAt,
    };
  }

  /**
   * Delete refresh token from Redis
   */
  async deleteRefreshToken(token: string): Promise<void> {
    const tokenHash = this.hashToken(token);
    await this.cacheService.delete(`refresh_token:${tokenHash}`);
  }

  /**
   * Delete all refresh tokens for a user
   */
  //   async deleteAllUserTokens(userId: string): Promise<void> {
  //     // Note: This requires scanning all keys, which is not ideal for production
  //     // In production, consider maintaining a set of tokens per user
  //     // For now, we'll implement a simple version
  //     // For better performance, maintain a Redis set: `user_tokens:{userId}`
  //     const pattern = `refresh_token:*`;
  //     // This is a simplified version - in production, use SCAN
  //     // For now, tokens will expire naturally
  //   }
}
