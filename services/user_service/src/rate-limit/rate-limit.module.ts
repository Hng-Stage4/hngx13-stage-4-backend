import { Module, Global } from '@nestjs/common';
import { RateLimitService } from './rate-limit.service';
import { RateLimitGuard } from './rate-limit.guard';
import { IpRateLimitGuard } from './ip-rate-limit.guard';
import { CacheModule } from '../cache/cache.module';

@Global() // Make rate limit guards available globally
@Module({
  imports: [CacheModule],
  providers: [RateLimitService, RateLimitGuard, IpRateLimitGuard],
  exports: [RateLimitService, RateLimitGuard, IpRateLimitGuard],
})
export class RateLimitModule {}
