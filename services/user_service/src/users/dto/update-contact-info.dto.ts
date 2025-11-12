/* eslint-disable @typescript-eslint/no-unsafe-call */
import { IsString, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class UpdateContactInfoDto {
  @ApiProperty({
    description: 'Push notification token',
    example: 'fcm-token-here',
    required: false,
  })
  @IsString()
  @IsOptional()
  push_token?: string;

  @ApiProperty({
    description: 'Phone number',
    example: '+1234567890',
    required: false,
  })
  @IsString()
  @IsOptional()
  phone_number?: string;
}
