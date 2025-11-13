import { Injectable } from '@nestjs/common';
import { HealthService } from '../health/health.service';

interface MetricValue {
  value: number;
  labels?: Record<string, string>;
}

@Injectable()
export class MetricsService {
  private requestTotal = 0;
  private requestFailedTotal = 0;
  private requestDurations: number[] = [];
  private authFailTotal = 0;
  private healthStatus = 1; // 1 = healthy, 0 = unhealthy

  constructor(private readonly healthService: HealthService) {}

  /**
   * Increment total requests counter
   */
  incrementRequestTotal(): void {
    this.requestTotal++;
  }

  /**
   * Increment failed requests counter
   */
  incrementRequestFailedTotal(): void {
    this.requestFailedTotal++;
  }

  /**
   * Record request duration in seconds
   */
  recordRequestDuration(durationSeconds: number): void {
    this.requestDurations.push(durationSeconds);
    // Keep only last 1000 durations to prevent memory issues
    if (this.requestDurations.length > 1000) {
      this.requestDurations.shift();
    }
  }

  /**
   * Increment auth failure counter
   */
  incrementAuthFailTotal(): void {
    this.authFailTotal++;
  }

  /**
   * Update health status
   */
  async updateHealthStatus(): Promise<void> {
    try {
      const health = await this.healthService.getHealthStatus();
      this.healthStatus = health.status === 'ok' ? 1 : 0;
    } catch {
      this.healthStatus = 0;
    }
  }

  /**
   * Get all metrics in Prometheus format
   */
  async getMetrics(): Promise<string> {
    // Update health status
    await this.updateHealthStatus();

    // Calculate request duration statistics
    const durationCount = this.requestDurations.length;
    const durationSum = this.requestDurations.reduce((a, b) => a + b, 0);
    const durationAvg = durationCount > 0 ? durationSum / durationCount : 0;

    // Build Prometheus metrics format
    const metrics: string[] = [];

    // user_requests_total
    metrics.push(`# HELP user_requests_total Total number of API requests`);
    metrics.push(`# TYPE user_requests_total counter`);
    metrics.push(`user_requests_total ${this.requestTotal}`);

    // user_requests_failed_total
    metrics.push(`# HELP user_requests_failed_total Total number of failed API requests`);
    metrics.push(`# TYPE user_requests_failed_total counter`);
    metrics.push(`user_requests_failed_total ${this.requestFailedTotal}`);

    // user_request_duration_seconds
    metrics.push(`# HELP user_request_duration_seconds API request latency in seconds`);
    metrics.push(`# TYPE user_request_duration_seconds histogram`);
    metrics.push(`user_request_duration_seconds_count ${durationCount}`);
    metrics.push(`user_request_duration_seconds_sum ${durationSum.toFixed(6)}`);
    metrics.push(`user_request_duration_seconds_avg ${durationAvg.toFixed(6)}`);

    // user_auth_fail_total
    metrics.push(`# HELP user_auth_fail_total Total number of failed authentication attempts`);
    metrics.push(`# TYPE user_auth_fail_total counter`);
    metrics.push(`user_auth_fail_total ${this.authFailTotal}`);

    // user_service_health_status
    metrics.push(`# HELP user_service_health_status Service health status (1 = healthy, 0 = unhealthy)`);
    metrics.push(`# TYPE user_service_health_status gauge`);
    metrics.push(`user_service_health_status ${this.healthStatus}`);

    return metrics.join('\n') + '\n';
  }

  /**
   * Get current metrics values (for testing/debugging)
   */
  getMetricsValues() {
    const durationCount = this.requestDurations.length;
    const durationSum = this.requestDurations.reduce((a, b) => a + b, 0);
    const durationAvg = durationCount > 0 ? durationSum / durationCount : 0;

    return {
      requestTotal: this.requestTotal,
      requestFailedTotal: this.requestFailedTotal,
      requestDurationCount: durationCount,
      requestDurationSum: durationSum,
      requestDurationAvg: durationAvg,
      authFailTotal: this.authFailTotal,
      healthStatus: this.healthStatus,
    };
  }
}

