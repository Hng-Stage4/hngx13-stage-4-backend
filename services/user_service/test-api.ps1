# Simple API Test Script for User Service
# Run this script to test your endpoints

$baseUrl = "http://localhost:3000"

Write-Host "🧪 Testing User Service API" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Root endpoint
Write-Host "1. Testing GET /" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl" -UseBasicParsing
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   📄 Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: Health endpoint (when implemented)
Write-Host "2. Testing GET /health" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -UseBasicParsing
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   📄 Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  Endpoint not implemented yet (expected)" -ForegroundColor Yellow
}

Write-Host ""

# Test 3: Check if service is running
Write-Host "3. Service Status Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Service is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Service is not responding" -ForegroundColor Red
    Write-Host "   Make sure the service is running with: pnpm run start:dev" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Test completed!" -ForegroundColor Cyan

