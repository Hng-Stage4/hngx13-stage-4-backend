#!/usr/bin/env python3
"""
Template Service Endpoint Tests
Tests all API endpoints in the template service.
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

def test_template_router():
    """Test template router functions directly"""
    print("🧪 Testing Template Router...")

    try:
        from app.routers.template import router

        # Check that router has the expected endpoints
        routes = [route.path for route in router.routes]
        expected_routes = ["/templates", "/templates/{template_id}", "/templates/{template_id}/render"]
        for route in expected_routes:
            assert route in routes, f"Template endpoint {route} not found"

        print("   ✅ Template router structure is correct")
        return True
    except Exception as e:
        print(f"   ❌ Template router test failed: {e}")
        return False

def test_version_router():
    """Test version router functions directly"""
    print("🧪 Testing Version Router...")

    try:
        from app.routers.version import router

        # Check that router has the expected endpoints
        routes = [route.path for route in router.routes]
        expected_routes = ["/templates/{template_id}/versions", "/versions/{version_id}"]
        for route in expected_routes:
            assert route in routes, f"Version endpoint {route} not found"

        print("   ✅ Version router structure is correct")
        return True
    except Exception as e:
        print(f"   ❌ Version router test failed: {e}")
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

        expected_routes = [
            "/",
            "/api/health",
            "/api/metrics",
            "/api/templates",
            "/api/templates/{template_id}",
            "/api/templates/{template_id}/render",
            "/api/templates/{template_id}/versions",
            "/api/versions/{version_id}"
        ]

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
        required_attrs = ['service_name', 'host', 'port', 'database_host', 'redis_host']
        for attr in required_attrs:
            assert hasattr(settings, attr), f"Settings missing {attr}"

        print(f"   ✅ Configuration loaded: service={settings.service_name}, port={settings.port}")
        return True
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_http_endpoints():
    """Test HTTP endpoints if service is running"""
    print("🧪 Testing HTTP Endpoints...")

    try:
        import httpx
        import asyncio

        async def run_tests():
            BASE_URL = "http://localhost:8003"
            TIMEOUT = 5.0

            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                # Test root endpoint
                try:
                    response = await client.get(f"{BASE_URL}/")
                    if response.status_code == 200:
                        print("   ✅ Root endpoint accessible")
                    else:
                        print(f"   ⚠️  Root endpoint returned {response.status_code}")
                        return False
                except Exception as e:
                    print(f"   ❌ Root endpoint not accessible: {e}")
                    print("   ℹ️  Service may not be running - this is expected for unit testing")
                    return False

                # Test health endpoint
                try:
                    response = await client.get(f"{BASE_URL}/api/health")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"   ✅ Health endpoint: {data.get('status', 'unknown')}")
                    else:
                        print(f"   ⚠️  Health endpoint returned {response.status_code}")
                        return False
                except Exception as e:
                    print(f"   ❌ Health endpoint failed: {e}")
                    return False

                # Test metrics endpoint
                try:
                    response = await client.get(f"{BASE_URL}/api/metrics")
                    if response.status_code == 200:
                        print("   ✅ Metrics endpoint accessible")
                    else:
                        print(f"   ⚠️  Metrics endpoint returned {response.status_code}")
                        return False
                except Exception as e:
                    print(f"   ❌ Metrics endpoint failed: {e}")
                    return False

                # Test templates endpoint (GET all - may be empty)
                try:
                    response = await client.get(f"{BASE_URL}/api/templates")
                    if response.status_code in [200, 404]:  # 404 if no templates
                        print("   ✅ Templates endpoint accessible")
                    else:
                        print(f"   ⚠️  Templates endpoint returned {response.status_code}")
                        return False
                except Exception as e:
                    print(f"   ❌ Templates endpoint failed: {e}")
                    return False

                print("   ✅ All HTTP endpoints tested successfully")
                return True

        return asyncio.run(run_tests())

    except ImportError:
        print("   ⚠️  httpx not available for HTTP testing")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Template Service Tests")
    print("=" * 60)

    tests = [
        ("Configuration Loading", test_config_loading),
        ("Health Router", test_health_router),
        ("Metrics Router", test_metrics_router),
        ("Template Router", test_template_router),
        ("Version Router", test_version_router),
        ("Main App", test_main_app),
        ("HTTP Endpoints", test_http_endpoints),
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
        print("   cd services/template_service && docker-compose up")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
