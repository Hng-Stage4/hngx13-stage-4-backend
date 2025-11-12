import { Module, Global } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { CacheService } from './cache.service';

@Global() // Make CacheModule available globally
@Module({
  imports: [ConfigModule],
  providers: [CacheService],
  exports: [CacheService],
})
export class CacheModule {
  static forRoot() {
    return {
      module: CacheModule,
      providers: [CacheService],
      exports: [CacheService],
    };
  }
}
