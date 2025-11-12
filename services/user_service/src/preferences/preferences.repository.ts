import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { UserPreference } from './entities/preference.entity';

@Injectable()
export class PreferencesRepository {
  constructor(
    @InjectRepository(UserPreference)
    private readonly preferenceRepository: Repository<UserPreference>,
  ) {}

  /**
   * Find preferences by user ID
   */
  async findByUserId(userId: string): Promise<UserPreference | null> {
    return await this.preferenceRepository.findOne({
      where: { user_id: userId },
      relations: ['user'],
    });
  }

  /**
   * Create preferences for a user
   */
  async create(
    userId: string,
    preferences: Partial<UserPreference>,
  ): Promise<UserPreference> {
    const preference = this.preferenceRepository.create({
      user_id: userId,
      ...preferences,
    });
    return await this.preferenceRepository.save(preference);
  }

  /**
   * Update preferences for a user
   */
  async update(
    userId: string,
    preferences: Partial<UserPreference>,
  ): Promise<UserPreference> {
    const existing = await this.findByUserId(userId);
    if (!existing) {
      throw new Error(`Preferences for user ${userId} not found`);
    }

    await this.preferenceRepository.update(existing.id, preferences);
    const updated = await this.findByUserId(userId);
    if (!updated) {
      throw new Error(`Failed to update preferences for user ${userId}`);
    }
    return updated;
  }

  /**
   * Create default preferences for a user
   */
  async createDefault(userId: string): Promise<UserPreference> {
    return await this.create(userId, {
      email_enabled: true,
      push_enabled: true,
    });
  }

  /**
   * Delete preferences by user ID
   */
  async deleteByUserId(userId: string): Promise<void> {
    await this.preferenceRepository.delete({ user_id: userId });
  }

  /**
   * Get repository instance (for advanced queries if needed)
   */
  getRepository(): Repository<UserPreference> {
    return this.preferenceRepository;
  }
}
