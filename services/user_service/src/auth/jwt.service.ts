import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import * as crypto from 'crypto';

export interface JwtPayload {
  sub: string; // user ID
  email: string;
  role: string;
  name: string;
}

@Injectable()
export class AuthJwtService {
  constructor(
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
  ) {}

  /**
   * Generate access token (JWT)
   * Uses the expiresIn configured in JwtModule
   */
  generateAccessToken(payload: JwtPayload): string {
    return this.jwtService.sign(payload as unknown as Record<string, unknown>);
  }

  /**
   * Generate refresh token (random string, not JWT)
   */
  generateRefreshToken(): string {
    // Generate a secure random string
    return crypto.randomBytes(32).toString('hex');
  }

  /**
   * Verify access token
   */
  verifyAccessToken(token: string): JwtPayload {
    try {
      return this.jwtService.verify<JwtPayload>(token);
    } catch {
      throw new UnauthorizedException('Invalid token');
    }
  }
}
