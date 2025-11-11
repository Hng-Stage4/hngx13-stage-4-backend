<?php

use Illuminate\Support\Str;
use App\Services\FirebaseService;
use App\Services\MetricsService;
use App\Services\PushNotificationService;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/fcm', function () {
    return view('fcm-generator');
});

Route::get('/test-push', function () {
    $pushService = new PushNotificationService(new FirebaseService(), new MetricsService());

    try {
        $result = $pushService->processNotification([
            'notification_id' => 'test-' . time(),
            'user_id' => (string) Str::uuid(),
            'push_token' => '<INSERT_VALID_FCM_TOKEN_HERE>',
            'title' => 'Welcome to HNG',
            'body' => 'Testing FCM integration',
            'image' => null,
            'link' => 'https://yourapp.com',
            'data' => ['type' => 'test'],
            'priority' => 1
        ]);

        return response()->json($result);

    } catch (Exception $e) {
        return response()->json([
            'success' => false,
            'error' => $e->getMessage()
        ], 500);
    }
});