import { Controller, Get, Res } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import express from 'express';
import { MetricsService } from './metrics.service';

@ApiTags('metrics')
@Controller('api/metrics')
export class MetricsController {
  constructor(private readonly metricsService: MetricsService) {}

  @Get()
  @ApiOperation({ summary: 'Prometheus metrics endpoint' })
  @ApiResponse({
    status: 200,
    description: 'Metrics in Prometheus format',
    content: {
      'text/plain': {
        schema: {
          type: 'string',
          example: `# HELP user_requests_total Total number of API requests
# TYPE user_requests_total counter
user_requests_total 150

# HELP user_requests_failed_total Total number of failed API requests
# TYPE user_requests_failed_total counter
user_requests_failed_total 5

# HELP user_request_duration_seconds API request latency in seconds
# TYPE user_request_duration_seconds histogram
user_request_duration_seconds_count 150
user_request_duration_seconds_sum 12.345
user_request_duration_seconds_avg 0.082

# HELP user_auth_fail_total Total number of failed authentication attempts
# TYPE user_auth_fail_total counter
user_auth_fail_total 3

# HELP user_service_health_status Service health status (1 = healthy, 0 = unhealthy)
# TYPE user_service_health_status gauge
user_service_health_status 1`,
        },
      },
    },
  })
  async getMetrics(@Res() res: express.Response) {
    const metrics = await this.metricsService.getMetrics();
    res.set('Content-Type', 'text/plain; version=0.0.4');
    return res.send(metrics);
  }
}
