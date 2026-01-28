"""
Test script for User Service
Tests all endpoints based on actual routes in main.py
"""

import requests
import json
from typing import Optional, Dict
import random
import string

# Configuration
BASE_URL = "http://localhost:8080"  # Adjust port as needed


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'


def generate_random_email():
    """Generate a random email for testing"""
    random_string = ''.join(random.choices(
        string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@example.com"


def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{title}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")


def print_test(test_name: str, passed: bool, details: Optional[str] = None):
    """Print test result with color"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {test_name}")
    if details:
        print(f"  {Colors.YELLOW}{details}{Colors.END}")


# Global variable to store authentication token
auth_token: Optional[str] = None
test_user_email: Optional[str] = None
test_user_id: Optional[str] = None


def test_root_endpoint():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        passed = response.status_code == 200
        data = response.json()
        details = f"Status: {response.status_code}, Service: {data.get('service', 'N/A')}"
        print_test("GET /", passed, details)
        return passed
    except Exception as e:
        print_test("GET /", False, f"Error: {str(e)}")
        return False


def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        passed = response.status_code == 200
        data = response.json()
        details = f"Status: {response.status_code}, Response: {data}"
        print_test("GET /health", passed, details)
        return passed
    except Exception as e:
        print_test("GET /health", False, f"Error: {str(e)}")
        return False


def test_healthz():
    """Test liveness probe"""
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        passed = response.status_code == 200
        data = response.json()
        details = f"Status: {response.status_code}, Service: {data.get('service', 'N/A')}"
        print_test("GET /healthz", passed, details)
        return passed
    except Exception as e:
        print_test("GET /healthz", False, f"Error: {str(e)}")
        return False


def test_ready():
    """Test readiness probe"""
    try:
        response = requests.get(f"{BASE_URL}/ready")
        passed = response.status_code == 200
        data = response.json()
        deps = data.get('dependencies', {})
        details = f"Status: {response.status_code}, DB: {deps.get('database', False)}, Cache: {deps.get('cache', False)}"
        print_test("GET /ready", passed, details)
        return passed
    except Exception as e:
        print_test("GET /ready", False, f"Error: {str(e)}")
        return False


def test_metrics():
    """Test Prometheus metrics endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        passed = response.status_code == 200
        content_length = len(response.text)
        details = f"Status: {response.status_code}, Content length: {content_length} bytes"
        print_test("GET /metrics", passed, details)
        return passed
    except Exception as e:
        print_test("GET /metrics", False, f"Error: {str(e)}")
        return False


def test_register_user():
    """Test user registration"""
    global test_user_email, test_user_id

    try:
        test_user_email = generate_random_email()
        new_user = {
            "email": test_user_email,
            "password": "Test@1234",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890"
        }

        response = requests.post(
            f"{BASE_URL}/api/users/register",
            json=new_user,
            headers={"Content-Type": "application/json"}
        )

        passed = response.status_code == 201
        if passed:
            data = response.json()
            test_user_id = data.get('id')
            details = f"Status: {response.status_code}, User ID: {test_user_id}, Email: {test_user_email}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"

        print_test("POST /api/users/register", passed, details)
        return passed, test_user_id, test_user_email
    except Exception as e:
        print_test("POST /api/users/register", False, f"Error: {str(e)}")
        return False, None, None


def test_register_duplicate_user():
    """Test registering duplicate user (should fail)"""
    try:
        duplicate_user = {
            "email": test_user_email,  # Use same email as before
            "password": "Test@1234",
            "first_name": "Duplicate",
            "last_name": "User",
            "phone": "+1234567890"
        }

        response = requests.post(
            f"{BASE_URL}/api/users/register",
            json=duplicate_user,
            headers={"Content-Type": "application/json"}
        )

        # Should fail with 409 Conflict
        passed = response.status_code == 409
        details = f"Status: {response.status_code} (Expected: 409 Conflict)"
        print_test("POST /api/users/register (duplicate)", passed, details)
        return passed
    except Exception as e:
        print_test("POST /api/users/register (duplicate)",
                   False, f"Error: {str(e)}")
        return False


def test_login(email: str, password: str = "Test@1234"):
    """Test user login"""
    global auth_token

    try:
        login_data = {
            "email": email,
            "password": password
        }

        response = requests.post(
            f"{BASE_URL}/api/users/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )

        passed = response.status_code == 200
        if passed:
            data = response.json()
            auth_token = data.get('access_token')
            details = f"Status: {response.status_code}, Token: {'✓ Received' if auth_token else '✗ Missing'}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"

        print_test("POST /api/users/login", passed, details)
        return passed, auth_token
    except Exception as e:
        print_test("POST /api/users/login", False, f"Error: {str(e)}")
        return False, None


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    try:
        login_data = {
            "email": test_user_email,
            "password": "WrongPassword123"
        }

        response = requests.post(
            f"{BASE_URL}/api/users/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )

        # Should fail with 401 Unauthorized
        passed = response.status_code == 401
        details = f"Status: {response.status_code} (Expected: 401 Unauthorized)"
        print_test("POST /api/users/login (invalid credentials)",
                   passed, details)
        return passed
    except Exception as e:
        print_test("POST /api/users/login (invalid credentials)",
                   False, f"Error: {str(e)}")
        return False


def test_get_profile():
    """Test getting current user profile"""
    try:
        if not auth_token:
            print_test("GET /api/users/profile", False,
                       "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/users/profile", headers=headers)

        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"Status: {response.status_code}, Email: {data.get('email', 'N/A')}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"

        print_test("GET /api/users/profile", passed, details)
        return passed
    except Exception as e:
        print_test("GET /api/users/profile", False, f"Error: {str(e)}")
        return False


def test_update_profile():
    """Test updating current user profile"""
    try:
        if not auth_token:
            print_test("PUT /api/users/profile", False,
                       "No auth token available")
            return False

        update_data = {
            "first_name": "Updated",
            "last_name": "TestUser",
            "phone": "+9876543210"
        }

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        response = requests.put(
            f"{BASE_URL}/api/users/profile",
            json=update_data,
            headers=headers
        )

        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"Status: {response.status_code}, Name: {data.get('first_name')} {data.get('last_name')}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"

        print_test("PUT /api/users/profile", passed, details)
        return passed
    except Exception as e:
        print_test("PUT /api/users/profile", False, f"Error: {str(e)}")
        return False


def test_change_password():
    """Test changing user password"""
    try:
        if not auth_token:
            print_test("PUT /api/users/password",
                       False, "No auth token available")
            return False

        password_data = {
            "old_password": "Test@1234",
            "new_password": "NewTest@5678"
        }

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        response = requests.put(
            f"{BASE_URL}/api/users/password",
            json=password_data,
            headers=headers
        )

        passed = response.status_code == 200
        details = f"Status: {response.status_code}"
        print_test("PUT /api/users/password", passed, details)
        return passed
    except Exception as e:
        print_test("PUT /api/users/password", False, f"Error: {str(e)}")
        return False


def test_get_all_users():
    """Test getting all users"""
    try:
        if not auth_token:
            print_test("GET /api/users", False, "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/users?limit=10&offset=0",
            headers=headers
        )

        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"Status: {response.status_code}, Users count: {len(data)}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"

        print_test("GET /api/users", passed, details)
        return passed
    except Exception as e:
        print_test("GET /api/users", False, f"Error: {str(e)}")
        return False


def test_get_user_by_id():
    """Test getting user by ID"""
    try:
        if not auth_token or not test_user_id:
            print_test("GET /api/users/{user_id}", False,
                       "No auth token or user ID available")
            return False

        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/users/{test_user_id}",
            headers=headers
        )

        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"Status: {response.status_code}, Email: {data.get('email', 'N/A')}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"

        print_test(f"GET /api/users/{test_user_id}", passed, details)
        return passed
    except Exception as e:
        print_test("GET /api/users/{user_id}", False, f"Error: {str(e)}")
        return False


def test_logout():
    """Test user logout"""
    try:
        if not auth_token:
            print_test("POST /api/users/logout", False,
                       "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/users/logout",
            headers=headers
        )

        passed = response.status_code == 204
        details = f"Status: {response.status_code} (Expected: 204 No Content)"
        print_test("POST /api/users/logout", passed, details)
        return passed
    except Exception as e:
        print_test("POST /api/users/logout", False, f"Error: {str(e)}")
        return False


def test_cache_stats():
    """Test cache statistics endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/debug/cache-stats")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"Status: {response.status_code}, Stats available: {len(data) > 0}"
        else:
            details = f"Status: {response.status_code}"

        print_test("GET /debug/cache-stats", passed, details)
        return passed
    except Exception as e:
        print_test("GET /debug/cache-stats", False, f"Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}User Service Test Suite{Colors.END}")
    print(f"{Colors.BLUE}Testing: {BASE_URL}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    # Track results
    total_tests = 0
    passed_tests = 0

    # Section 1: Basic Health Checks
    print_section("Section 1: Health & System Endpoints")

    tests = [
        test_root_endpoint,
        test_health_check,
        test_healthz,
        test_ready,
        test_metrics,
        test_cache_stats
    ]

    for test in tests:
        total_tests += 1
        if test():
            passed_tests += 1

    # Section 2: Authentication Flow
    print_section("Section 2: User Registration & Authentication")

    # Test registration
    total_tests += 1
    success, user_id, email = test_register_user()
    if success:
        passed_tests += 1

    # Test duplicate registration
    if email:
        total_tests += 1
        if test_register_duplicate_user():
            passed_tests += 1

    # Test invalid login
    if email:
        total_tests += 1
        if test_login_invalid_credentials():
            passed_tests += 1

    # Test valid login
    if email:
        total_tests += 1
        success, token = test_login(email)
        if success:
            passed_tests += 1

    # Section 3: Authenticated Endpoints
    if auth_token:
        print_section("Section 3: Profile & User Management")

        authenticated_tests = [
            test_get_profile,
            test_update_profile,
            test_change_password,
            test_get_all_users,
            test_get_user_by_id,
        ]

        for test in authenticated_tests:
            total_tests += 1
            if test():
                passed_tests += 1

        # Section 4: Logout
        print_section("Section 4: Logout")

        total_tests += 1
        if test_logout():
            passed_tests += 1

    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Total Tests: {total_tests}")
    print(f"{Colors.GREEN}Passed: {passed_tests}{Colors.END}")
    print(f"{Colors.RED}Failed: {total_tests - passed_tests}{Colors.END}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

    return passed_tests == total_tests


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
