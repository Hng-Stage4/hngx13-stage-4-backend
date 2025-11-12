import {
  Injectable,
  NotFoundException,
  //   ForbiddenException,
} from '@nestjs/common';
import { UsersRepository } from './users.repository';
import { CacheService } from '../cache/cache.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { UpdateContactInfoDto } from './dto/update-contact-info.dto';
import { UserResponseDto } from './dto/user-response.dto';
import { User } from './entities/user.entity';
import { PasswordService } from '../auth/password.service';
import { PreferencesRepository } from '../preferences/preferences.repository';

@Injectable()
export class UsersService {
  private readonly USER_CACHE_TTL = 300; // 5 minutes
  private readonly EMAIL_CACHE_TTL = 300; // 5 minutes

  constructor(
    private readonly usersRepository: UsersRepository,
    private readonly cacheService: CacheService,
    private readonly passwordService: PasswordService,
    private readonly preferencesRepository: PreferencesRepository,
  ) {}

  /**
   * Find user by ID with caching
   */
  async findById(id: string): Promise<User> {
    // Check cache first
    const cacheKey = `user:${id}`;
    const cached = await this.cacheService.get(cacheKey);

    if (cached) {
      return JSON.parse(cached) as User;
    }

    // Query database
    const user = await this.usersRepository.findById(id);
    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }

    // Cache the result (exclude password_hash)
    const userWithoutPassword = { ...user };
    delete (userWithoutPassword as { password_hash?: string }).password_hash;
    await this.cacheService.set(
      cacheKey,
      JSON.stringify(userWithoutPassword),
      this.USER_CACHE_TTL,
    );

    return user;
  }

  /**
   * Find user by email with caching
   */
  async findByEmail(email: string): Promise<User> {
    // Check email -> user_id cache
    const emailCacheKey = `user:${email}:id`;
    const cachedUserId = await this.cacheService.get(emailCacheKey);

    if (cachedUserId) {
      return await this.findById(cachedUserId);
    }

    // Query database
    const user = await this.usersRepository.findByEmail(email);
    if (!user) {
      throw new NotFoundException(`User with email ${email} not found`);
    }

    // Cache email -> user_id mapping
    await this.cacheService.set(emailCacheKey, user.id, this.EMAIL_CACHE_TTL);

    // Also cache the user
    const cacheKey = `user:${user.id}`;
    const userWithoutPassword = { ...user };
    delete (userWithoutPassword as { password_hash?: string }).password_hash;
    await this.cacheService.set(
      cacheKey,
      JSON.stringify(userWithoutPassword),
      this.USER_CACHE_TTL,
    );

    return user;
  }

  /**
   * Get current user (excludes password)
   */
  async getCurrentUser(userId: string): Promise<UserResponseDto> {
    const user = await this.findById(userId);

    // Exclude password_hash from response
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { password_hash, ...userResponse } = user;
    return userResponse as UserResponseDto;
  }

  /**
   * Create user (for admin/system use)
   */
  async create(dto: CreateUserDto): Promise<User> {
    // Hash password
    const password_hash = await this.passwordService.hashPassword(dto.password);

    // Create user
    const user = await this.usersRepository.create({
      email: dto.email,
      name: dto.name,
      password_hash,
      role: dto.role || 'user',
    });

    // Create default preferences
    await this.preferencesRepository.create(user.id, {
      email_enabled: true,
      push_enabled: true,
    });

    // Cache the user
    const cacheKey = `user:${user.id}`;
    const emailCacheKey = `user:${user.email}:id`;
    const userWithoutPassword = { ...user };
    delete (userWithoutPassword as { password_hash?: string }).password_hash;

    await this.cacheService.set(
      cacheKey,
      JSON.stringify(userWithoutPassword),
      this.USER_CACHE_TTL,
    );
    await this.cacheService.set(emailCacheKey, user.id, this.EMAIL_CACHE_TTL);

    return user;
  }

  /**
   * Update user
   */
  async update(id: string, dto: UpdateUserDto): Promise<User> {
    const user = await this.findById(id);

    // Prepare update data
    const updateData: Partial<User> = {};
    if (dto.email !== undefined) updateData.email = dto.email;
    if (dto.name !== undefined) updateData.name = dto.name;
    if (dto.push_token !== undefined) updateData.push_token = dto.push_token;
    if (dto.phone_number !== undefined)
      updateData.phone_number = dto.phone_number;

    // Update in database
    const updatedUser = await this.usersRepository.update(id, updateData);

    // Invalidate cache
    await this.invalidateUserCache(id, user.email);

    // If email changed, invalidate old email cache too
    if (dto.email && dto.email !== user.email) {
      await this.invalidateUserCache(id, dto.email);
    }

    return updatedUser;
  }

  /**
   * Update contact info (push_token, phone_number)
   */
  async updateContactInfo(
    id: string,
    dto: UpdateContactInfoDto,
  ): Promise<User> {
    const user = await this.findById(id);

    const updateData: Partial<User> = {};
    if (dto.push_token !== undefined) updateData.push_token = dto.push_token;
    if (dto.phone_number !== undefined)
      updateData.phone_number = dto.phone_number;

    const updatedUser = await this.usersRepository.update(id, updateData);

    // Invalidate cache
    await this.invalidateUserCache(id, user.email);

    return updatedUser;
  }

  /**
   * Delete user (soft delete)
   */
  async delete(id: string): Promise<void> {
    const user = await this.findById(id);

    // Soft delete user
    await this.usersRepository.softDelete(id);

    // Delete user preferences
    await this.preferencesRepository.deleteByUserId(id);

    // Invalidate all user cache
    await this.invalidateUserCache(id, user.email);
  }

  /**
   * Get contact info for other services (Email/Push)
   */
  async getContactInfo(id: string): Promise<{
    email: string;
    push_token: string | null;
    phone_number: string | null;
  }> {
    const user = await this.findById(id);

    return {
      email: user.email,
      push_token: user.push_token,
      phone_number: user.phone_number,
    };
  }

  /**
   * Check if user can access resource (own user or admin)
   */
  canAccessResource(
    userId: string,
    resourceUserId: string,
    userRole: string,
  ): boolean {
    return userId === resourceUserId || userRole === 'admin';
  }

  /**
   * Invalidate user cache
   */
  private async invalidateUserCache(
    userId: string,
    email: string,
  ): Promise<void> {
    await this.cacheService.delete(`user:${userId}`);
    await this.cacheService.delete(`user:${email}:id`);
  }
}
