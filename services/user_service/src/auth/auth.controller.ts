import {
  Controller,
  Post,
  Body,
  HttpCode,
  HttpStatus,
  UseGuards,
  Request,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiBody,
} from '@nestjs/swagger';
import { AuthService } from './auth.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { RefreshTokenDto } from './dto/refresh-token.dto';
import { TokenResponseDto } from './dto/token-response.dto';
import { JwtAuthGuard } from './jwt-auth.guard';
import { StandardResponseDto } from '../common/dto/standard-response.dto';
import { RateLimit, RateLimitGuard } from '../rate-limit/rate-limit.guard';
import {
  IpRateLimit,
  IpRateLimitGuard,
} from '../rate-limit/ip-rate-limit.guard';

@ApiTags('auth')
@Controller('auth')
@UseGuards(IpRateLimitGuard) // Global IP rate limit for all auth endpoints
@IpRateLimit({ limit: 1000, ttl: 60 }) // 1000 requests per minute per IP
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('register')
  @UseGuards(RateLimitGuard)
  @RateLimit({ limit: 5, ttl: 60 }) // 5 requests per minute
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Register a new user' })
  @ApiResponse({
    status: 201,
    description: 'User registered successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({ status: 400, description: 'Validation error' })
  @ApiResponse({ status: 409, description: 'User already exists' })
  async register(@Body() dto: RegisterDto) {
    const user = await this.authService.register(dto);
    return {
      success: true,
      message: 'User registered successfully',
      data: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
    };
  }

  @Post('login')
  @UseGuards(RateLimitGuard)
  @RateLimit({ limit: 5, ttl: 60 }) // 5 requests per minute
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Login user and get access tokens' })
  @ApiResponse({
    status: 200,
    description: 'Login successful',
    type: StandardResponseDto,
  })
  @ApiResponse({ status: 401, description: 'Invalid credentials' })
  async login(@Body() dto: LoginDto): Promise<{
    success: boolean;
    message: string;
    data: TokenResponseDto;
  }> {
    const tokens = await this.authService.login(dto);
    return {
      success: true,
      message: 'Login successful',
      data: tokens,
    };
  }

  @Post('refresh')
  @UseGuards(RateLimitGuard)
  @RateLimit({ limit: 10, ttl: 60 }) // 10 requests per minute
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Refresh access token using refresh token' })
  @ApiResponse({
    status: 200,
    description: 'Token refreshed successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({ status: 401, description: 'Invalid or expired refresh token' })
  async refresh(@Body() dto: RefreshTokenDto): Promise<{
    success: boolean;
    message: string;
    data: TokenResponseDto;
  }> {
    const tokens = await this.authService.refresh(dto.refresh_token);
    return {
      success: true,
      message: 'Token refreshed successfully',
      data: tokens,
    };
  }

  @Post('logout')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  @ApiBearerAuth('JWT-auth')
  @ApiOperation({ summary: 'Logout user and invalidate tokens' })
  @ApiResponse({
    status: 200,
    description: 'Logged out successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        refresh_token: {
          type: 'string',
          description: 'Refresh token to invalidate',
          example:
            'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
        },
      },
    },
    required: false,
  })
  async logout(
    @Request() req: { headers?: { authorization?: string } },
    @Body() body: { refresh_token?: string },
  ) {
    // Extract token from request
    const authHeader = req.headers?.authorization || '';
    const accessToken = authHeader.replace('Bearer ', '') || '';
    const refreshToken = body.refresh_token || '';

    await this.authService.logout(accessToken, refreshToken);

    return {
      success: true,
      message: 'Logged out successfully',
      data: null,
    };
  }
}
