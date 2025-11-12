import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { DatabaseModule } from './database/database.module';
import { CacheModule } from './cache/cache.module';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { PreferencesModule } from './preferences/preferences.module';
import { RateLimitModule } from './rate-limit/rate-limit.module';

@Module({
  imports: [
    // Load environment variables
    ConfigModule.forRoot({
      isGlobal: true, // Make ConfigModule available globally
      envFilePath: '.env',
    }),
    // Database connection
    DatabaseModule,
    // Redis cache
    CacheModule,
    // Rate limiting (global module)
    RateLimitModule,
    // Feature modules
    UsersModule,
    PreferencesModule,
    AuthModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
