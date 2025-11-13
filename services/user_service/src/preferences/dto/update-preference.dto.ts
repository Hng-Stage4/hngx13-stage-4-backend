import { IsBoolean, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class UpdatePreferenceDto {
  @ApiProperty({
    description: 'Enable or disable email notifications',
    example: true,
    required: false,
  })
  @IsBoolean()
  @IsOptional()
  email_enabled?: boolean;

  @ApiProperty({
    description: 'Enable or disable push notifications',
    example: true,
    required: false,
  })
  @IsBoolean()
  @IsOptional()
  push_enabled?: boolean;
}
