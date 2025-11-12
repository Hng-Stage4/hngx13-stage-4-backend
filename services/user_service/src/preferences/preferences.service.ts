import { Injectable, NotFoundException } from '@nestjs/common';
import { PreferencesRepository } from './preferences.repository';
import { CacheService } from '../cache/cache.service';
import { UpdatePreferenceDto } from './dto/update-preference.dto';
import { UserPreference } from './entities/preference.entity';

@Injectable()
export class PreferencesService {
  private readonly PREFERENCES_CACHE_TTL = 600; // 10 minutes

  constructor(
    private readonly preferencesRepository: PreferencesRepository,
    private readonly cacheService: CacheService,
  ) {}

  /**
   * Get preferences for a user with caching
   */
  async getPreferences(userId: string): Promise<UserPreference> {
    // Check cache first
    const cacheKey = `user:${userId}:preferences`;
    const cached = await this.cacheService.get(cacheKey);

    if (cached) {
      return JSON.parse(cached) as UserPreference;
    }

    // Query database
    const preferences = await this.preferencesRepository.findByUserId(userId);
    if (!preferences) {
      throw new NotFoundException(`Preferences for user ${userId} not found`);
    }

    // Cache the result
    await this.cacheService.set(
      cacheKey,
      JSON.stringify(preferences),
      this.PREFERENCES_CACHE_TTL,
    );

    return preferences;
  }

  /**
   * Update preferences for a user
   */
  async updatePreferences(
    userId: string,
    dto: UpdatePreferenceDto,
  ): Promise<UserPreference> {
    // Check if preferences exist
    const existing = await this.preferencesRepository.findByUserId(userId);
    if (!existing) {
      throw new NotFoundException(`Preferences for user ${userId} not found`);
    }

    // Prepare update data
    const updateData: Partial<UserPreference> = {};
    if (dto.email_enabled !== undefined)
      updateData.email_enabled = dto.email_enabled;
    if (dto.push_enabled !== undefined)
      updateData.push_enabled = dto.push_enabled;

    // Update in database
    const updated = await this.preferencesRepository.update(userId, updateData);

    // Invalidate cache
    await this.invalidatePreferencesCache(userId);

    return updated;
  }

  /**
   * Get default preferences
   */
  getDefaultPreferences(): {
    email_enabled: boolean;
    push_enabled: boolean;
  } {
    return {
      email_enabled: true,
      push_enabled: true,
    };
  }

  /**
   * Create default preferences for a user
   */
  async createDefaultPreferences(userId: string): Promise<UserPreference> {
    const preferences = await this.preferencesRepository.createDefault(userId);

    // Cache the result
    const cacheKey = `user:${userId}:preferences`;
    await this.cacheService.set(
      cacheKey,
      JSON.stringify(preferences),
      this.PREFERENCES_CACHE_TTL,
    );

    return preferences;
  }

  /**
   * Invalidate preferences cache
   */
  private async invalidatePreferencesCache(userId: string): Promise<void> {
    await this.cacheService.delete(`user:${userId}:preferences`);
  }
}
