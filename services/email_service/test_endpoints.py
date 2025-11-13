#!/usr/bin/env python3
"""
Email Service Endpoint Tests
Tests all API endpoints in the email service.
Since the full service may not be running, this script tests what it can.
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timezone

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_health_router():
    """Test health router functions directly"""
    print("🧪 Testing Health Router...")

    try:
        from app.routers.health import router

        # Check that router has the health endpoint
        routes = [route.path for route in router.routes]
        assert "/health" in routes, "Health endpoint not found"

        print("   ✅ Health router structure is correct")
        return True
    except Exception as e:
        print(f"   ❌ Health router test failed: {e}")
        return False

def test_metrics_router():
    """Test metrics router functions directly"""
    print("🧪 Testing Metrics Router...")

    try:
        from app.routers.metrics import router

        # Check that router has the metrics endpoint
        routes = [route.path for route in router.routes]
        assert "/metrics" in routes, "Metrics endpoint not found"

        print("   ✅ Metrics router structure is correct")
        return True
    except Exception as e:
        print(f"   ❌ Metrics router test failed: {e}")
        return False

def test_webhooks_router():
    """Test webhooks router functions directly"""
    print("🧪 Testing Webhooks Router...")

    try:
        from app.routers.webhooks import router

        # Check that router has the webhook endpoints
        routes = [route.path for route in router.routes]
        expected_routes = ["/sendgrid", "/mailgun", "/smtp/bounce"]
        for route in expected_routes:
            assert route in routes, f"Webhook endpoint {route} not found"

        print("   ✅ Webhooks router structure is correct")
        return True
    except Exception as e:
        print(f"   ❌ Webhooks router test failed: {e}")
        return False

def test_main_app():
    """Test main app structure"""
    print("🧪 Testing Main App...")

    try:
        from app.main import app

        # Check that app has the expected routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
            elif hasattr(route, 'paths'):
                routes.extend(route.paths)

        expected_routes = ["/", "/api/health", "/api/metrics", "/api/webhooks/sendgrid", "/api/webhooks/mailgun", "/api/webhooks/smtp/bounce"]

        for expected_route in expected_routes:
            assert expected_route in routes, f"Route {expected_route} not found in app"

        print("   ✅ Main app structure is correct")
        return True
    except Exception as e:
        print(f"   ❌ Main app test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("🧪 Testing Configuration Loading...")

    try:
        from app.config.settings import settings

        # Check that settings has expected attributes
        required_attrs = ['service_name', 'host', 'port']
        for attr in required_attrs:
            assert hasattr(settings, attr), f"Settings missing {attr}"

        print(f"   ✅ Configuration loaded: service={settings.service_name}, port={settings.port}")
        return True
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

async def test_http_endpoints():
    """Test HTTP endpoints if service is running"""
    print("🧪 Testing HTTP Endpoints...")

    try:
        import httpx

        BASE_URL = "http://localhost:8001"
        TIMEOUT = 5.0

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test root endpoint
            try:
                response = await client.get(f"{BASE_URL}/")
                if response.status_code == 200:
                    print("   ✅ Root endpoint accessible")
                    return True
                else:
                    print(f"   ⚠️  Root endpoint returned {response.status_code}")
                    return False
            except Exception as e:
                print(f"   ❌ HTTP endpoints not accessible: {e}")
                print("   ℹ️  Service may not be running - this is expected for unit testing")
                return False

    except ImportError:
        print("   ⚠️  httpx not available for HTTP testing")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Email Service Tests")
    print("=" * 60)

    tests = [
        ("Configuration Loading", test_config_loading),
        ("Health Router", test_health_router),
        ("Metrics Router", test_metrics_router),
        ("Webhooks Router", test_webhooks_router),
        ("Main App", test_main_app),
        ("HTTP Endpoints", lambda: asyncio.run(test_http_endpoints())),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append(result)
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")

    passed = sum(results)
    failed = len(results) - passed

    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Total: {len(results)}")

    if failed == 0:
        print("🎉 All available tests completed successfully!")
        print("\n📝 Note: HTTP endpoint tests may fail if the service is not running.")
        print("   To test HTTP endpoints, start the service with:")
        print("   cd services/email_service && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
