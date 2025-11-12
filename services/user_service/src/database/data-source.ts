import { DataSource } from 'typeorm';
import { ConfigService } from '@nestjs/config';
import { User } from '../users/entities/user.entity';
import { UserPreference } from '../preferences/entities/preference.entity';

const configService = new ConfigService();

const databaseUrl = configService.get<string>('DATABASE_URL');

export default new DataSource({
  type: 'postgres',
  url: databaseUrl || undefined,
  host: databaseUrl
    ? undefined
    : configService.get<string>('DB_HOST', 'localhost'),
  port: databaseUrl ? undefined : configService.get<number>('DB_PORT', 5432),
  username: databaseUrl
    ? undefined
    : configService.get<string>('DB_USERNAME', 'postgres'),
  password: databaseUrl
    ? undefined
    : configService.get<string>('DB_PASSWORD', 'postgres'),
  database: databaseUrl
    ? undefined
    : configService.get<string>('DB_DATABASE', 'notification_db'),
  entities: [User, UserPreference],
  migrations: ['src/database/migrations/*.ts'],
  synchronize: false, // Always false for migrations
  logging: true,
});
