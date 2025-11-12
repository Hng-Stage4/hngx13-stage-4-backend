<?php

return [
    
    // AMQP connection for Laravel queues
    'host' => env('RABBITMQ_HOST', 'localhost'),
    'port' => env('RABBITMQ_PORT', 5672),
    'user' => env('RABBITMQ_USER', 'guest'),
    'password' => env('RABBITMQ_PASSWORD', 'guest'),
    'vhost' => env('RABBITMQ_VHOST', '/'),
    'exchange' => env('RABBITMQ_EXCHANGE', 'notifications.direct'),
    'queues' => [
        'push' => env('RABBITMQ_QUEUE_PUSH', 'push.queue'),
        'failed' => env('RABBITMQ_QUEUE_FAILED', 'failed.queue'),
    ],

    // Management API for MetricsService
    'management_host' => env('RABBITMQ_MANAGEMENT_HOST', '127.0.0.1'),
    'management_port' => env('RABBITMQ_MANAGEMENT_PORT', 15672),
    'management_user' => env('RABBITMQ_MANAGEMENT_USER', 'guest'),
    'management_password' => env('RABBITMQ_MANAGEMENT_PASSWORD', 'guest'),
];
