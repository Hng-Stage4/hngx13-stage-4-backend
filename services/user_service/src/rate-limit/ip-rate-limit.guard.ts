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

export const IP_RATE_LIMIT_KEY = 'ip_rate_limit';

export interface IpRateLimitOptions {
  limit: number;
  ttl: number; // Time window in seconds
}

/**
 * Decorator to set IP-based rate limit for an endpoint
 */
export const IpRateLimit = (options: IpRateLimitOptions) =>
  SetMetadata(IP_RATE_LIMIT_KEY, options);

@Injectable()
export class IpRateLimitGuard implements CanActivate {
  constructor(
    private readonly rateLimitService: RateLimitService,
    private readonly reflector: Reflector,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const request = context.switchToHttp().getRequest();
    const handler = context.getHandler();

    // Get IP rate limit options from decorator metadata
    const ipRateLimitOptions = this.reflector.get<IpRateLimitOptions>(
      IP_RATE_LIMIT_KEY,
      handler,
    );

    // If no IP rate limit is set, allow the request
    if (!ipRateLimitOptions) {
      return true;
    }

    const { limit, ttl } = ipRateLimitOptions;

    // Extract IP address
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    const forwardedFor = request.headers?.['x-forwarded-for'] as
      | string
      | undefined;
    const ip =
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      (request.ip as string | undefined) ||
      forwardedFor?.split(',')[0] ||
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      (request.connection?.remoteAddress as string | undefined) ||
      'unknown';

    // Check IP-based rate limit
    const ipAllowed = await this.rateLimitService.checkIpRateLimit(
      ip,
      limit,
      ttl,
    );

    if (!ipAllowed) {
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
