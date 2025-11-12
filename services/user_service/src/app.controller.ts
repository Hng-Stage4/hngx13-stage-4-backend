import { Controller, Get, Post, Body } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { AppService } from './app.service';
import { DatabaseService } from './database/database.service';
import { CacheService } from './cache/cache.service';

@ApiTags('health')
@Controller()
export class AppController {
  constructor(
    private readonly appService: AppService,
    private readonly databaseService: DatabaseService,
    private readonly cacheService: CacheService,
  ) {}

  @Get()
  @ApiOperation({ summary: 'Health check endpoint' })
  @ApiResponse({ status: 200, description: 'Service is running' })
  getHello(): string {
    return this.appService.getHello();
  }

  @Get('db-test')
  @ApiOperation({ summary: 'Test database connection' })
  @ApiResponse({ status: 200, description: 'Database connection status' })
  async testDatabase() {
    const status = await this.databaseService.getConnectionStatus();
    return {
      success: status.isConnected,
      message: status.isConnected
        ? 'Database connection successful'
        : 'Database connection failed',
      data: status,
    };
  }

  @Get('redis-test')
  @ApiOperation({ summary: 'Test Redis connection' })
  @ApiResponse({ status: 200, description: 'Redis connection status' })
  async testRedis() {
    const status = await this.cacheService.getConnectionStatus();
    return {
      success: status.isConnected,
      message: status.isConnected
        ? 'Redis connection successful'
        : 'Redis connection failed',
      data: status,
    };
  }

  @Post('redis-test')
  @ApiOperation({
    summary: 'Test Redis operations (set, get, exists, increment)',
  })
  @ApiResponse({ status: 200, description: 'Redis operations test results' })
  async testRedisOperations(@Body() body: { key?: string; value?: string }) {
    const testKey = body.key || 'test:key';
    const testValue = body.value || 'test-value';

    try {
      // Test set
      await this.cacheService.set(testKey, testValue, 60);
      const getValue = await this.cacheService.get(testKey);
      const exists = await this.cacheService.exists(testKey);
      const increment = await this.cacheService.increment('test:counter', 60);

      return {
        success: true,
        message: 'All Redis operations successful',
        data: {
          set: 'OK',
          get: getValue,
          exists,
          increment,
        },
      };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: 'Redis operations failed',
        error: errorMessage,
      };
    }
  }
}
