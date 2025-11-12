import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
  Index,
} from 'typeorm';
import { IsBoolean, IsUUID, IsOptional } from 'class-validator';
import { User } from '../../users/entities/user.entity';

@Entity('user_preferences')
@Index(['user_id'], { unique: true })
export class UserPreference {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid', name: 'user_id', unique: true })
  @IsUUID()
  user_id: string;

  @Column({ type: 'boolean', default: true, name: 'email_enabled' })
  @IsBoolean()
  @IsOptional()
  email_enabled: boolean;

  @Column({ type: 'boolean', default: true, name: 'push_enabled' })
  @IsBoolean()
  @IsOptional()
  push_enabled: boolean;

  @CreateDateColumn({ name: 'created_at', type: 'timestamp' })
  created_at: Date;

  @UpdateDateColumn({ name: 'updated_at', type: 'timestamp' })
  updated_at: Date;

  // Relationship with User

  @ManyToOne(() => User, (user) => user.preference, {
    onDelete: 'CASCADE',
  })
  @JoinColumn({ name: 'user_id' })
  user: User;
}
