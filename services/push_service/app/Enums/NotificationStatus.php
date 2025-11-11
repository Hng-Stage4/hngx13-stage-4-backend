<?php

namespace App\Enums;

enum NotificationStatus: string
{
    case DELIVERED = 'delivered';
    case PENDING = 'pending';
    case FAILED = 'failed';
}