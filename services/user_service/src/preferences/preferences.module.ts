import { Module, forwardRef } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UserPreference } from './entities/preference.entity';
import { PreferencesRepository } from './preferences.repository';
import { PreferencesService } from './preferences.service';
import { PreferencesController } from './preferences.controller';
import { CacheModule } from '../cache/cache.module';
import { UsersModule } from '../users/users.module';

@Module({
  imports: [
    TypeOrmModule.forFeature([UserPreference]),
    CacheModule,
    forwardRef(() => UsersModule),
  ],
  providers: [PreferencesRepository, PreferencesService],
  controllers: [PreferencesController],
  exports: [PreferencesRepository, PreferencesService, TypeOrmModule],
})
export class PreferencesModule {}
