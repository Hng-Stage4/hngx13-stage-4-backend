import {
  Injectable,
  ConflictException,
  UnauthorizedException,
  //   NotFoundException,
} from '@nestjs/common';
import { UsersRepository } from '../users/users.repository';
import { PreferencesRepository } from '../preferences/preferences.repository';
import { PasswordService } from './password.service';
import { AuthJwtService, JwtPayload } from './jwt.service';
import { RefreshTokenService } from './refresh-token.service';
import { TokenBlacklistService } from './token-blacklist.service';
import { MetricsService } from '../metrics/metrics.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { TokenResponseDto } from './dto/token-response.dto';
import { User } from '../users/entities/user.entity';

@Injectable()
export class AuthService {
  constructor(
    private readonly usersRepository: UsersRepository,
    private readonly preferencesRepository: PreferencesRepository,
    private readonly passwordService: PasswordService,
    private readonly jwtService: AuthJwtService,
    private readonly refreshTokenService: RefreshTokenService,
    private readonly tokenBlacklistService: TokenBlacklistService,
    private readonly metricsService: MetricsService,
  ) { }

  /**
   * Register a new user
   */
  async register(dto: RegisterDto): Promise<Omit<User, 'password_hash'>> {
    // Check if user already exists
    const existingUser = await this.usersRepository.findByEmail(dto.email);
    if (existingUser) {
      throw new ConflictException('User with this email already exists');
    }

    // Hash password
    const passwordHash = await this.passwordService.hashPassword(dto.password);

    // Create user
    const user = await this.usersRepository.create({
      email: dto.email,
      name: dto.name,
      password_hash: passwordHash,
      role: 'user',
      active: true,
    });

    // Create default preferences
    await this.preferencesRepository.createDefault(user.id);

    // Return user without password
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { password_hash, ...userWithoutPassword } = user;
    return userWithoutPassword;
  }

  /**
   * Login user and return tokens
   */
  async login(dto: LoginDto): Promise<TokenResponseDto> {
    // Find user by email
    const user = await this.usersRepository.findByEmail(dto.email);
    if (!user) {
      this.metricsService.incrementAuthFailTotal();
      throw new UnauthorizedException('Invalid email or password');
    }

    // Verify password
    const isPasswordValid = await this.passwordService.verifyPassword(
      dto.password,
      user.password_hash,
    );
    if (!isPasswordValid) {
      this.metricsService.incrementAuthFailTotal();
      throw new UnauthorizedException('Invalid email or password');
    }

    // Check if user is active
    if (!user.active) {
      this.metricsService.incrementAuthFailTotal();
      throw new UnauthorizedException('User account is inactive');
    }

    // Generate tokens
    const payload: JwtPayload = {
      sub: user.id,
      email: user.email,
      role: user.role,
      name: user.name,
    };

    const accessToken = this.jwtService.generateAccessToken(payload);
    const refreshToken = this.jwtService.generateRefreshToken();

    // Store refresh token in Redis
    await this.refreshTokenService.storeRefreshToken(refreshToken, user.id);

    // Return tokens
    return {
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'bearer',
      expires_in: 30 * 60, // 30 minutes in seconds
    };
  }

  /**
   * Refresh access token
   */
  async refresh(refreshToken: string): Promise<TokenResponseDto> {
    // Get token data from Redis
    const tokenData =
      await this.refreshTokenService.getRefreshToken(refreshToken);

    if (!tokenData) {
      this.metricsService.incrementAuthFailTotal();
      throw new UnauthorizedException('Invalid or expired refresh token');
    }

    // Get user
    const user = await this.usersRepository.findById(tokenData.userId);
    if (!user || !user.active) {
      this.metricsService.incrementAuthFailTotal();
      throw new UnauthorizedException('User not found or inactive');
    }

    // Generate new access token
    const payload: JwtPayload = {
      sub: user.id,
      email: user.email,
      role: user.role,
      name: user.name,
    };

    const accessToken = this.jwtService.generateAccessToken(payload);

    // Optionally rotate refresh token (for security)
    const newRefreshToken = this.jwtService.generateRefreshToken();
    await this.refreshTokenService.deleteRefreshToken(refreshToken);
    await this.refreshTokenService.storeRefreshToken(newRefreshToken, user.id);

    return {
      access_token: accessToken,
      refresh_token: newRefreshToken,
      token_type: 'bearer',
      expires_in: 30 * 60, // 30 minutes in seconds
    };
  }

  /**
   * Logout user
   */
  async logout(accessToken: string, refreshToken: string): Promise<void> {
    // Blacklist access token
    await this.tokenBlacklistService.blacklistToken(accessToken);

    // Delete refresh token
    if (refreshToken) {
      await this.refreshTokenService.deleteRefreshToken(refreshToken);
    }
  }

  /**
   * Validate token (check blacklist and verify signature)
   */
  async validateToken(token: string): Promise<boolean> {
    // Check if token is blacklisted
    const isBlacklisted =
      await this.tokenBlacklistService.isTokenBlacklisted(token);
    if (isBlacklisted) {
      return false;
    }

    // Verify JWT signature
    try {
      this.jwtService.verifyAccessToken(token);
      return true;
    } catch {
      return false;
    }
  }
}
