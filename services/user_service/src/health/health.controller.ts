import { Controller, Get, HttpCode, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { HealthService } from './health.service';

@ApiTags('health')
@Controller('health')
export class HealthController {
  constructor(private readonly healthService: HealthService) {}

  @Get()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Comprehensive health check' })
  @ApiResponse({
    status: 200,
    description: 'Service is healthy (all dependencies up)',
    schema: {
      type: 'object',
      properties: {
        status: {
          type: 'string',
          enum: ['ok', 'error'],
          description: 'Overall health status',
        },
        database: {
          type: 'string',
          enum: ['up', 'down'],
          description: 'Database connection status',
        },
        redis: {
          type: 'string',
          enum: ['up', 'down'],
          description: 'Redis connection status',
        },
        uptime: {
          type: 'number',
          description: 'Service uptime in seconds',
        },
        version: {
          type: 'string',
          description: 'Service version',
        },
        timestamp: {
          type: 'string',
          format: 'date-time',
          description: 'Current timestamp',
        },
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: 'Service is degraded (one or more dependencies down)',
  })
  async getHealth() {
    const healthStatus = await this.healthService.getHealthStatus();
    // Always return 200 so the endpoint is accessible even when degraded
    // Monitoring systems can check the 'status' field in the response body
    // Alternative: Return 503 for degraded state, but this makes the endpoint
    // less resilient if you want to always be able to check health
    return healthStatus;
  }
}
