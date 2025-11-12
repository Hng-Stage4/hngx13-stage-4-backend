import {
  Controller,
  Get,
  Put,
  Param,
  Body,
  UseGuards,
  Request,
  HttpCode,
  HttpStatus,
  ForbiddenException,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiParam,
} from '@nestjs/swagger';
import { PreferencesService } from './preferences.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { UpdatePreferenceDto } from './dto/update-preference.dto';
import { PreferenceResponseDto } from './dto/preference-response.dto';
import { JwtPayload } from '../auth/jwt.service';
import { UsersService } from '../users/users.service';
import { StandardResponseDto } from '../common/dto/standard-response.dto';
import { RateLimit, RateLimitGuard } from '../rate-limit/rate-limit.guard';
import {
  IpRateLimit,
  IpRateLimitGuard,
} from '../rate-limit/ip-rate-limit.guard';

interface AuthenticatedRequest extends Request {
  user?: JwtPayload;
}

@ApiTags('preferences')
@Controller('users/:id/preferences')
@UseGuards(IpRateLimitGuard) // IP rate limit for all preference endpoints
@IpRateLimit({ limit: 1000, ttl: 60 }) // 1000 requests per minute per IP
export class PreferencesController {
  constructor(
    private readonly preferencesService: PreferencesService,
    private readonly usersService: UsersService,
  ) {}

  /**
   * Get user preferences
   * GET /users/:id/preferences
   * Can be accessed without auth (for Email/Push services via API Gateway)
   */
  @Get()
  @UseGuards(RateLimitGuard)
  @RateLimit({ limit: 50, ttl: 60 }) // 50 requests per minute (IP-based since no auth)
  @ApiOperation({ summary: 'Get user preferences' })
  @ApiParam({
    name: 'id',
    description: 'User UUID',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @ApiResponse({
    status: 200,
    description: 'Preferences retrieved successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({ status: 404, description: 'Preferences not found' })
  async getPreferences(@Param('id') id: string): Promise<{
    success: boolean;
    message: string;
    data: PreferenceResponseDto;
  }> {
    const preferences = await this.preferencesService.getPreferences(id);

    return {
      success: true,
      message: 'Preferences retrieved successfully',
      data: preferences as PreferenceResponseDto,
    };
  }

  /**
   * Update user preferences
   * PUT /users/:id/preferences
   * Protected - user can only update their own preferences
   */
  @Put()
  @UseGuards(JwtAuthGuard, RateLimitGuard)
  @RateLimit({ limit: 50, ttl: 60 }) // 50 requests per minute per user
  @ApiBearerAuth('JWT-auth')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Update user preferences' })
  @ApiParam({
    name: 'id',
    description: 'User UUID',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @ApiResponse({
    status: 200,
    description: 'Preferences updated successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - Cannot update other users preferences',
  })
  @ApiResponse({ status: 404, description: 'Preferences not found' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  async updatePreferences(
    @Param('id') id: string,
    @Body() dto: UpdatePreferenceDto,
    @Request() req: AuthenticatedRequest,
  ): Promise<{
    success: boolean;
    message: string;
    data: PreferenceResponseDto;
  }> {
    const userId = req.user?.sub;
    const userRole = req.user?.role || 'user';

    if (!userId) {
      throw new ForbiddenException('User not authenticated');
    }

    // Check authorization: user can only update their own preferences, unless admin
    if (!this.usersService.canAccessResource(userId, id, userRole)) {
      throw new ForbiddenException(
        'You do not have permission to update these preferences',
      );
    }

    const updated = await this.preferencesService.updatePreferences(id, dto);

    return {
      success: true,
      message: 'Preferences updated successfully',
      data: updated as PreferenceResponseDto,
    };
  }
}
