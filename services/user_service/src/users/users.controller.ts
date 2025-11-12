import {
  Controller,
  Get,
  Put,
  Delete,
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
import { UsersService } from './users.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { UpdateUserDto } from './dto/update-user.dto';
import { UpdateContactInfoDto } from './dto/update-contact-info.dto';
import { UserResponseDto } from './dto/user-response.dto';
import { JwtPayload } from '../auth/jwt.service';
import { StandardResponseDto } from '../common/dto/standard-response.dto';

interface AuthenticatedRequest extends Request {
  user?: JwtPayload;
}

@ApiTags('users')
@ApiBearerAuth('JWT-auth')
@Controller('users')
@UseGuards(JwtAuthGuard)
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  /**
   * Get user by ID
   * GET /users/:id
   */
  @Get(':id')
  @ApiOperation({ summary: 'Get user by ID' })
  @ApiParam({
    name: 'id',
    description: 'User UUID',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @ApiResponse({
    status: 200,
    description: 'User retrieved successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({ status: 404, description: 'User not found' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  async findById(@Param('id') id: string): Promise<{
    success: boolean;
    message: string;
    data: UserResponseDto;
  }> {
    const user = await this.usersService.findById(id);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { password_hash, ...userResponse } = user;

    return {
      success: true,
      message: 'User retrieved successfully',
      data: userResponse as UserResponseDto,
    };
  }

  /**
   * Get current user (from JWT token)
   * GET /users/me
   */
  @Get('me')
  @ApiOperation({ summary: 'Get current authenticated user' })
  @ApiResponse({
    status: 200,
    description: 'Current user retrieved successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  async getCurrentUser(@Request() req: AuthenticatedRequest): Promise<{
    success: boolean;
    message: string;
    data: UserResponseDto;
  }> {
    const userId = req.user?.sub;
    if (!userId) {
      throw new ForbiddenException('User not authenticated');
    }

    const user = await this.usersService.getCurrentUser(userId);

    return {
      success: true,
      message: 'Current user retrieved successfully',
      data: user,
    };
  }

  /**
   * Get user by email (for other services, optional auth)
   * GET /users/email/:email
   */
  @Get('email/:email')
  @ApiOperation({ summary: 'Get user by email address' })
  @ApiParam({
    name: 'email',
    description: 'User email address',
    example: 'user@example.com',
  })
  @ApiResponse({
    status: 200,
    description: 'User retrieved successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({ status: 404, description: 'User not found' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  async findByEmail(@Param('email') email: string): Promise<{
    success: boolean;
    message: string;
    data: UserResponseDto;
  }> {
    const user = await this.usersService.findByEmail(email);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { password_hash, ...userResponse } = user;

    return {
      success: true,
      message: 'User retrieved successfully',
      data: userResponse as UserResponseDto,
    };
  }

  /**
   * Update user
   * PUT /users/:id
   */
  @Put(':id')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Update user information' })
  @ApiParam({
    name: 'id',
    description: 'User UUID',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @ApiResponse({
    status: 200,
    description: 'User updated successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - Cannot update other users',
  })
  @ApiResponse({ status: 404, description: 'User not found' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  async update(
    @Param('id') id: string,
    @Body() dto: UpdateUserDto,
    @Request() req: AuthenticatedRequest,
  ): Promise<{
    success: boolean;
    message: string;
    data: UserResponseDto;
  }> {
    const userId = req.user?.sub;
    const userRole = req.user?.role || 'user';

    if (!userId) {
      throw new ForbiddenException('User not authenticated');
    }

    // Check authorization: user can only update themselves, unless admin
    if (!this.usersService.canAccessResource(userId, id, userRole)) {
      throw new ForbiddenException(
        'You do not have permission to update this user',
      );
    }

    const updatedUser = await this.usersService.update(id, dto);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { password_hash, ...userResponse } = updatedUser;

    return {
      success: true,
      message: 'User updated successfully',
      data: userResponse as UserResponseDto,
    };
  }

  /**
   * Update contact info
   * PUT /users/:id/contact-info
   */
  @Put(':id/contact-info')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Update user contact information (push_token, phone_number)',
  })
  @ApiParam({
    name: 'id',
    description: 'User UUID',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @ApiResponse({
    status: 200,
    description: 'Contact info updated successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - Cannot update other users',
  })
  @ApiResponse({ status: 404, description: 'User not found' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  async updateContactInfo(
    @Param('id') id: string,
    @Body() dto: UpdateContactInfoDto,
    @Request() req: AuthenticatedRequest,
  ): Promise<{
    success: boolean;
    message: string;
    data: UserResponseDto;
  }> {
    const userId = req.user?.sub;
    const userRole = req.user?.role || 'user';

    if (!userId) {
      throw new ForbiddenException('User not authenticated');
    }

    // Check authorization: user can only update themselves, unless admin
    if (!this.usersService.canAccessResource(userId, id, userRole)) {
      throw new ForbiddenException(
        'You do not have permission to update this user',
      );
    }

    const updatedUser = await this.usersService.updateContactInfo(id, dto);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { password_hash, ...userResponse } = updatedUser;

    return {
      success: true,
      message: 'Contact info updated successfully',
      data: userResponse as UserResponseDto,
    };
  }

  /**
   * Delete user (soft delete)
   * DELETE /users/:id
   */
  @Delete(':id')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Delete user account (soft delete)' })
  @ApiParam({
    name: 'id',
    description: 'User UUID',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @ApiResponse({
    status: 200,
    description: 'User deleted successfully',
    type: StandardResponseDto,
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - Cannot delete other users',
  })
  @ApiResponse({ status: 404, description: 'User not found' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  async delete(
    @Param('id') id: string,
    @Request() req: AuthenticatedRequest,
  ): Promise<{
    success: boolean;
    message: string;
    data: null;
  }> {
    const userId = req.user?.sub;
    const userRole = req.user?.role || 'user';

    if (!userId) {
      throw new ForbiddenException('User not authenticated');
    }

    // Check authorization: user can only delete themselves, unless admin
    if (!this.usersService.canAccessResource(userId, id, userRole)) {
      throw new ForbiddenException(
        'You do not have permission to delete this user',
      );
    }

    await this.usersService.delete(id);

    return {
      success: true,
      message: 'User deleted successfully',
      data: null,
    };
  }
}
