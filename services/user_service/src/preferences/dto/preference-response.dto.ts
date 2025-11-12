import { ApiProperty } from '@nestjs/swagger';

export class PreferenceResponseDto {
  @ApiProperty({
    description: 'Preference unique identifier',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  id: string;

  @ApiProperty({
    description: 'User ID',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  user_id: string;

  @ApiProperty({
    description: 'Whether email notifications are enabled',
    example: true,
  })
  email_enabled: boolean;

  @ApiProperty({
    description: 'Whether push notifications are enabled',
    example: true,
  })
  push_enabled: boolean;

  @ApiProperty({
    description: 'Creation timestamp',
    example: '2024-01-01T00:00:00.000Z',
  })
  created_at: Date;

  @ApiProperty({
    description: 'Last update timestamp',
    example: '2024-01-01T00:00:00.000Z',
  })
  updated_at: Date;
}
