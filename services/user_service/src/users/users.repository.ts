import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UsersRepository {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  /**
   * Find user by ID
   */
  async findById(id: string): Promise<User | null> {
    return await this.userRepository.findOne({
      where: { id },
      relations: ['preference'],
    });
  }

  /**
   * Find user by email
   */
  async findByEmail(email: string): Promise<User | null> {
    return await this.userRepository.findOne({
      where: { email },
      relations: ['preference'],
    });
  }

  /**
   * Create new user
   */
  async create(userData: Partial<User>): Promise<User> {
    const user = this.userRepository.create(userData);
    return await this.userRepository.save(user);
  }

  /**
   * Update user
   */
  async update(id: string, userData: Partial<User>): Promise<User> {
    await this.userRepository.update(id, userData);
    const updatedUser = await this.findById(id);
    if (!updatedUser) {
      throw new Error(`User with ID ${id} not found`);
    }
    return updatedUser;
  }

  /**
   * Soft delete user (sets deleted_at)
   */
  async softDelete(id: string): Promise<void> {
    await this.userRepository.softDelete(id);
  }

  /**
   * Find all active users
   */
  async findActiveUsers(): Promise<User[]> {
    return await this.userRepository.find({
      where: { active: true },
      relations: ['preference'],
    });
  }

  /**
   * Get repository instance (for advanced queries if needed)
   */
  getRepository(): Repository<User> {
    return this.userRepository;
  }
}
