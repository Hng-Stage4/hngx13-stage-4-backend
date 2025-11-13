import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { MetricsService } from './metrics.service';

@Injectable()
export class MetricsInterceptor implements NestInterceptor {
  constructor(private readonly metricsService: MetricsService) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const request = context.switchToHttp().getRequest();
    const startTime = Date.now();

    // Skip metrics endpoint itself
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    if (request.path === '/api/metrics') {
      return next.handle();
    }

    // Increment total requests
    this.metricsService.incrementRequestTotal();

    return next.handle().pipe(
      tap(() => {
        // Record successful request duration
        const duration = (Date.now() - startTime) / 1000; // Convert to seconds
        this.metricsService.recordRequestDuration(duration);
      }),
      catchError((error) => {
        // Record failed request
        this.metricsService.incrementRequestFailedTotal();

        // Record duration even for failed requests
        const duration = (Date.now() - startTime) / 1000;
        this.metricsService.recordRequestDuration(duration);

        // eslint-disable-next-line @typescript-eslint/no-unsafe-return
        return throwError(() => error);
      }),
    );
  }
}
