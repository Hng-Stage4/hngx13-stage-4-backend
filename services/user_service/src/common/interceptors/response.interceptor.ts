import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

interface StandardResponse<T> {
  success: boolean;
  message: string;
  data?: T | null;
  error?: string;
  meta?: unknown;
}

@Injectable()
export class ResponseInterceptor<T>
  implements NestInterceptor<T, StandardResponse<T>>
{
  intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Observable<StandardResponse<T>> {
    return next.handle().pipe(
      map((data) => {
        // If response is already in standard format, return as is
        if (
          data &&
          typeof data === 'object' &&
          'success' in data &&
          'message' in data
        ) {
          return data as StandardResponse<T>;
        }

        // If response is from health check (different format), return as is
        if (
          data &&
          typeof data === 'object' &&
          ('status' in data || 'database' in data || 'redis' in data)
        ) {
          return data as unknown as StandardResponse<T>;
        }

        // Transform to standard format
        return {
          success: true,
          message: 'Operation successful',
          data: (data ?? null) as T | null,
        };
      }),
    );
  }
}
