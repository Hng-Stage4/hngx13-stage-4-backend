import { Module, forwardRef } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './entities/user.entity';
import { UsersRepository } from './users.repository';
import { UsersService } from './users.service';
import { UsersController } from './users.controller';
import { CacheModule } from '../cache/cache.module';
import { AuthModule } from '../auth/auth.module';
import { PreferencesModule } from '../preferences/preferences.module';

@Module({
  imports: [
    TypeOrmModule.forFeature([User]),
    CacheModule,
    forwardRef(() => AuthModule),
    PreferencesModule,
  ],
  providers: [UsersRepository, UsersService],
  controllers: [UsersController],
  exports: [UsersRepository, UsersService, TypeOrmModule],
})
export class UsersModule {}
