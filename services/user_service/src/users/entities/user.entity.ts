import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  CreateDateColumn,
  UpdateDateColumn,
  DeleteDateColumn,
  Index,
  OneToOne,
} from 'typeorm';
import {
  IsEmail,
  IsString,
  MinLength,
  MaxLength,
  IsBoolean,
  IsOptional,
} from 'class-validator';
import { UserPreference } from '../../preferences/entities/preference.entity';

@Entity('users')
@Index(['active']) // Keep only the index on 'active' here
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'varchar', length: 255, unique: true })
  @IsEmail()
  email: string;

  @Column({ type: 'varchar', length: 100 })
  @IsString()
  @MinLength(2)
  @MaxLength(100)
  name: string;

  @Column({ type: 'varchar', length: 255, name: 'password_hash' })
  @IsString()
  password_hash: string;

  @Column({ type: 'varchar', length: 20, default: 'user' })
  @IsString()
  @IsOptional()
  role: string;

  @Column({ type: 'boolean', default: true })
  @IsBoolean()
  @IsOptional()
  active: boolean;

  @Column({ type: 'varchar', length: 500, nullable: true, name: 'push_token' })
  @IsString()
  @IsOptional()
  push_token: string | null;

  @Column({ type: 'varchar', length: 20, nullable: true, name: 'phone_number' })
  @IsString()
  @IsOptional()
  phone_number: string | null;

  @CreateDateColumn({ name: 'created_at', type: 'timestamp' })
  created_at: Date;

  @UpdateDateColumn({ name: 'updated_at', type: 'timestamp' })
  updated_at: Date;

  @DeleteDateColumn({ name: 'deleted_at', type: 'timestamp', nullable: true })
  deleted_at: Date | null;

  // Relationship with UserPreference

  @OneToOne(() => UserPreference, (preference) => preference.user)
  preference?: UserPreference;
}
