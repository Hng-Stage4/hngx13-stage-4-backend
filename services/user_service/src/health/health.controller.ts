import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { HealthService } from './health.service';

@ApiTags('health')
@Controller('health')
export class HealthController {
  constructor(private readonly healthService: HealthService) {}

  @Get()
  @ApiOperation({ summary: 'Comprehensive health check' })
  @ApiResponse({
    status: 200,
    description: 'Health check results',
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
  async getHealth() {
    return await this.healthService.getHealthStatus();
  }
}
