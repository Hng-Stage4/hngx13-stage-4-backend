import {
  Controller,
  Post,
  Body,
  HttpCode,
  HttpStatus,
  UseGuards,
  Request,
} from '@nestjs/common';
import { AuthService } from './auth.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { RefreshTokenDto } from './dto/refresh-token.dto';
import { TokenResponseDto } from './dto/token-response.dto';
import { JwtAuthGuard } from './jwt-auth.guard';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('register')
  @HttpCode(HttpStatus.CREATED)
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
  @HttpCode(HttpStatus.OK)
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
  @HttpCode(HttpStatus.OK)
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
