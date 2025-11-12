<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;

class NotificationLog extends Model
{
    use HasUuids;

    protected $fillable = [
        'notification_id',
        'notification_type',
        'user_id',
        'push_token',
        'status',
        'error_message',
        'retry_count',
        'sent_at',
        'delivered_at',
        'metadata',
    ];

    protected $casts = [
        'push_token' => 'encrypted',
        'metadata' => 'encrypted',
        'sent_at' => 'datetime',
        'delivered_at' => 'datetime',
    ];
}
