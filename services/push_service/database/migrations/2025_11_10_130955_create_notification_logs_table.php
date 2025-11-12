<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('notification_logs', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('notification_id')->unique()->index();
            $table->string('notification_type');
            $table->uuid('user_id')->index();
            $table->text('push_token')->nullable();
            $table->text('metadata')->nullable();
            $table->enum('status', ['pending', 'delivered', 'failed'])->default('pending');
            $table->text('error_message')->nullable();
            $table->integer('retry_count')->default(0);
            $table->timestamp('sent_at')->nullable();
            $table->timestamp('delivered_at')->nullable();
            $table->timestamps();
            
            $table->index(['status', 'created_at']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('notification_logs');
    }
};
