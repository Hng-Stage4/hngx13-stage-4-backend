import {
  Injectable,
  CanActivate,
  ExecutionContext,
  HttpException,
  HttpStatus,
  SetMetadata,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { RateLimitService } from './rate-limit.service';
import { JwtPayload } from '../auth/jwt.service';

export const RATE_LIMIT_KEY = 'rate_limit';

export interface RateLimitOptions {
  limit: number;
  ttl: number; // Time window in seconds
  endpoint?: string; // Optional custom endpoint identifier
}

/**
 * Decorator to set rate limit for an endpoint
 */
export const RateLimit = (options: RateLimitOptions) =>
  SetMetadata(RATE_LIMIT_KEY, options);

@Injectable()
export class RateLimitGuard implements CanActivate {
  constructor(
    private readonly rateLimitService: RateLimitService,
    private readonly reflector: Reflector,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const request = context.switchToHttp().getRequest();
    const handler = context.getHandler();

    // Get rate limit options from decorator metadata
    const rateLimitOptions = this.reflector.get<RateLimitOptions>(
      RATE_LIMIT_KEY,
      handler,
    );

    // If no rate limit is set, allow the request
    if (!rateLimitOptions) {
      return true;
    }

    const { limit, ttl, endpoint } = rateLimitOptions;

    // Extract user ID from JWT token if available
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    const user = request.user as JwtPayload | undefined;
    const userId = user?.sub || 'anonymous';

    // Use custom endpoint or default to request path
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    const endpointKey = endpoint || (request.path as string);

    // Check user-based rate limit
    const userAllowed = await this.rateLimitService.checkRateLimit(
      userId,
      endpointKey,
      limit,
      ttl,
    );

    if (!userAllowed) {
      throw new HttpException(
        {
          success: false,
          message: 'Rate limit exceeded. Please try again later.',
          error: 'TOO_MANY_REQUESTS',
        },
        HttpStatus.TOO_MANY_REQUESTS,
      );
    }

    return true;
  }
}
