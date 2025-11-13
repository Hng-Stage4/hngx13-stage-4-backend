import { ApiProperty } from '@nestjs/swagger';
import { PaginationMetaDto } from './pagination-meta.dto';

export class StandardResponseDto<T> {
  @ApiProperty({ description: 'Indicates if the request was successful' })
  success: boolean;

  @ApiProperty({ description: 'Human-readable message' })
  message: string;

  @ApiProperty({ description: 'Response data', required: false })
  data?: T | null;

  @ApiProperty({ description: 'Error code (if any)', required: false })
  error?: string;

  @ApiProperty({
    description: 'Pagination metadata (for list endpoints)',
    required: false,
    type: PaginationMetaDto,
  })
  meta?: PaginationMetaDto;
}
