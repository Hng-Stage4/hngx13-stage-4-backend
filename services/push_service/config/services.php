<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Mailgun, Postmark, AWS and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate the various service credentials.
    |
    */

    'postmark' => [
        'key' => env('POSTMARK_API_KEY'),
    ],

    'resend' => [
        'key' => env('RESEND_API_KEY'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],
    
    'api_gateway' => [
        'url' => env('API_GATEWAY_URL', 'http://localhost:8080'),
    ],
    
    'circuit_breaker' => [
        'failure_threshold' => env('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5),
        'timeout' => env('CIRCUIT_BREAKER_TIMEOUT', 60),
        'retry_timeout' => env('CIRCUIT_BREAKER_RETRY_TIMEOUT', 30),
    ],
    
    'max_retry_attempts' => env('MAX_RETRY_ATTEMPTS', 3),
    'retry_delay_seconds' => env('RETRY_DELAY_SECONDS', 5),

];
