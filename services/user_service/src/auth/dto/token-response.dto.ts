export class TokenResponseDto {
  access_token: string;
  refresh_token: string;
  token_type: string = 'bearer';
  expires_in: number; // in seconds
}
