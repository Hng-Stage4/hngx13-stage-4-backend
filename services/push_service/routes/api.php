<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\HealthController;
use App\Http\Controllers\MetricsController;

Route::get('/', function () {
    return response()->json(['message' => 'Push Service API is running.']);
});

Route::get('/health', [HealthController::class, 'health']);
Route::get('/metrics', [MetricsController::class, 'index']);
