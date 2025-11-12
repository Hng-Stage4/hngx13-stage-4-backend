<?php

namespace App\Http\Controllers;

use App\Services\MetricsService;
use App\Traits\JsonLogging;

/**
 * Metrics Controller
 * Exposes application metrics for monitoring.
 */
class MetricsController extends Controller
{
    use JsonLogging;

    private string $serviceName = 'push_metrics_service';

    /**
     * Display the metrics.
     *
     * @param MetricsService $metricsService
     * @return \Illuminate\Http\Response
     */
    public function index(MetricsService $metricsService)
    {
        try {
            $metrics = $metricsService->render();

            return response($metrics, 200)
                ->header('Content-Type', 'text/plain; version=0.0.4');

        } catch (\Throwable $e) {
            $this->logJson(
                'error',
                $this->serviceName,
                'metrics_render_failed',
                "Failed to render metrics: {$e->getMessage()}"
            );

            return response("Metrics rendering failed", 500);
        }
    }
}
