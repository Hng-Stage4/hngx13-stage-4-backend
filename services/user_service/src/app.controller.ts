import { Controller, Get } from '@nestjs/common';
import { AppService } from './app.service';
import { DatabaseService } from './database/database.service';

@Controller()
export class AppController {
  constructor(
    private readonly appService: AppService,
    private readonly databaseService: DatabaseService,
  ) {}

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }

  @Get('db-test')
  async testDatabase() {
    const status = await this.databaseService.getConnectionStatus();
    return {
      success: status.isConnected,
      message: status.isConnected
        ? 'Database connection successful'
        : 'Database connection failed',
      data: status,
    };
  }
}
