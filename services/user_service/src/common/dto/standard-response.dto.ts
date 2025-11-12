import { ApiProperty } from '@nestjs/swagger';

export class StandardResponseDto<T> {
  @ApiProperty({ description: 'Indicates if the request was successful' })
  success: boolean;

  @ApiProperty({ description: 'Human-readable message' })
  message: string;

  @ApiProperty({ description: 'Response data', required: false })
  data?: T | null;

  @ApiProperty({ description: 'Error code (if any)', required: false })
  error?: string;
}
