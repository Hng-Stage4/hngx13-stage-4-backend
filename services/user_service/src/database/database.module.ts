import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { DatabaseService } from './database.service';

@Module({
  imports: [
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (configService: ConfigService) => {
        // Get database URL from environment or construct it
        const databaseUrl = configService.get<string>('DATABASE_URL');
        if (databaseUrl) {
          // Parse DATABASE_URL if provided
          return {
            type: 'postgres',
            url: databaseUrl,
            autoLoadEntities: true,
            synchronize: configService.get<string>('APP_ENV') === 'development', // Only in dev
            logging: configService.get<string>('APP_ENV') === 'development',
          };
        }

        // Fallback to individual environment variables
        return {
          type: 'postgres',
          host: configService.get<string>('DB_HOST', 'localhost'),
          port: configService.get<number>('DB_PORT', 5432),
          username: configService.get<string>('DB_USERNAME', 'postgres'),
          password: configService.get<string>('DB_PASSWORD', 'postgres'),
          database: configService.get<string>('DB_DATABASE', 'notification_db'),
          autoLoadEntities: true,
          synchronize: configService.get<string>('APP_ENV') === 'development', // Only in dev
          logging: configService.get<string>('APP_ENV') === 'development',
        };
      },
      inject: [ConfigService],
    }),
  ],
  providers: [DatabaseService],
  exports: [DatabaseService],
})
export class DatabaseModule {}
