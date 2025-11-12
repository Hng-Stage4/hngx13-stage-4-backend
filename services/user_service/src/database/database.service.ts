import { Injectable, OnModuleInit } from '@nestjs/common';
import { InjectConnection } from '@nestjs/typeorm';
import { Connection } from 'typeorm';

interface PostgresConnectionOptions {
  type?: string;
  database?: string;
  host?: string;
  url?: string;
}

@Injectable()
export class DatabaseService implements OnModuleInit {
  constructor(
    @InjectConnection()
    private readonly connection: Connection,
  ) {}

  private getConnectionInfo(): { database: string; host: string } {
    const options = this.connection.options as PostgresConnectionOptions;
    const database = options.database || 'unknown';
    const host = options.host || (options.url ? 'from URL' : 'unknown');
    return { database, host };
  }

  async onModuleInit() {
    try {
      // Test database connection
      await this.connection.query('SELECT 1');
      console.log('✅ Database connection established');
      const { database, host } = this.getConnectionInfo();
      console.log(`📊 Database: ${database}`);
      console.log(`🔌 Host: ${host}`);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Database connection failed:', errorMessage);
      throw error;
    }
  }

  /**
   * Get database connection status
   */
  async getConnectionStatus(): Promise<{
    status: string;
    database: string;
    isConnected: boolean;
  }> {
    try {
      await this.connection.query('SELECT 1');
      const { database } = this.getConnectionInfo();
      return {
        status: 'connected',
        database,
        isConnected: this.connection.isConnected,
      };
    } catch {
      const { database } = this.getConnectionInfo();
      return {
        status: 'disconnected',
        database,
        isConnected: false,
      };
    }
  }
}
