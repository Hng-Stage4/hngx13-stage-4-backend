import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UserPreference } from './entities/preference.entity';
import { PreferencesRepository } from './preferences.repository';

@Module({
  imports: [TypeOrmModule.forFeature([UserPreference])],
  providers: [PreferencesRepository],
  exports: [PreferencesRepository, TypeOrmModule],
})
export class PreferencesModule {}
