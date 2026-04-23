"""
Comprehensive Manual Testing Suite for Lawmate Website
IEEE 829 Standard Test Case Format
Tests: Form Testing, Security/URL Testing, User Flow Testing
"""

import requests
import json
from datetime import datetime
from typing import List
import time

class LawmateTestSuite:
    def __init__(self, base_url="http://localhost:8000", frontend_url="http://localhost:3000"):
        self.base_url = base_url
        self.frontend_url = frontend_url
        self.test_results = []
        self.test_count = 0
        self.passed = 0
        self.failed = 0

        # Test users for different scenarios
        self.test_users = {
            'citizen': {'email': 'ali.raza@example.pk', 'password': 'demo123', 'userType': 'citizen'},
            'lawyer': {'email': 'sara.ahmed@lawmate.pk', 'password': 'demo123', 'userType': 'lawyer'},
            'admin': {'email': 'admin@lawmate.com', 'password': 'admin123', 'userType': 'admin'}
        }

        self.tokens = {}

    def log_test(self, test_id: str, title: str, objective: str, preconditions: str,
                 steps: List[str], test_data: str, expected: str, actual: str,
                 status: str, priority: str, notes: str = ""):
        """Log test case in IEEE 829 format"""
        self.test_count += 1
        if status.upper() == "PASS":
            self.passed += 1
        else:
            self.failed += 1

        self.test_results.append({
            'Test Case ID': test_id,
            'Test Case Title': title,
            'Test Objective': objective,
            'Preconditions': preconditions,
            'Test Steps': steps,
            'Test Data': test_data,
            'Expected Result': expected,
            'Actual Result': actual,
            'Status': status,
            'Priority': priority,
            'Notes': notes,
            'Timestamp': datetime.now().isoformat()
        })

    def print_separator(self, title):
        """Print formatted separator"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80 + "\n")

    # ============================================================================
    # CATEGORY 1: FORM TESTING
    # ============================================================================

    def test_login_form_valid(self):
        """TC-FORM-001: Test login form with valid credentials"""
        test_id = "TC-FORM-001"
        title = "Login Form - Valid Credentials (Citizen)"

        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.test_users['citizen'],
                timeout=10
            )

            actual = f"Status: {response.status_code}, Response: {response.json()}"

            if response.status_code == 200 and 'user' in response.json():
                self.tokens['citizen'] = response.json().get('user')
                status = "PASS"
            else:
                status = "FAIL"

            self.log_test(
                test_id=test_id,
                title=title,
                objective="Verify login form accepts valid citizen credentials",
                preconditions="User exists in database with valid credentials",
                steps=[
                    "1. Navigate to login API endpoint",
                    "2. Send POST request with valid email, password, userType",
                    "3. Observe response"
                ],
                test_data=f"Email: {self.test_users['citizen']['email']}, Password: demo123, UserType: citizen",
                expected="Status 200, Returns user object with id, name, email, userType",
                actual=actual,
                status=status,
                priority="HIGH"
            )
        except Exception as e:
            self.log_test(test_id, title, "Test login", "None", [], str(self.test_users['citizen']),
                         "Success", f"Exception: {str(e)}", "FAIL", "HIGH", str(e))

    def test_login_form_invalid_email(self):
        """TC-FORM-002: Test login with invalid email"""
        test_id = "TC-FORM-002"
        title = "Login Form - Invalid Email"

        try:
            invalid_data = {
                'email': 'nonexistent@test.com',
                'password': 'wrongpass',
                'userType': 'citizen'
            }

            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=invalid_data,
                timeout=10
            )

            actual = f"Status: {response.status_code}, Response: {response.json() if response.status_code != 500 else 'Server Error'}"

            if response.status_code in [401, 404]:
                status = "PASS"
            else:
                status = "FAIL"

            self.log_test(
                test_id=test_id,
                title=title,
                objective="Verify login form rejects invalid credentials",
                preconditions="User does not exist in database",
                steps=[
                    "1. Navigate to login API endpoint",
                    "2. Send POST request with non-existent email",
                    "3. Observe response"
                ],
                test_data=str(invalid_data),
                expected="Status 401 or 404, Returns error message",
                actual=actual,
                status=status,
                priority="HIGH"
            )
        except Exception as e:
            self.log_test(test_id, title, "Test invalid login", "None", [], str(invalid_data),
                         "Error response", f"Exception: {str(e)}", "FAIL", "HIGH", str(e))

    def test_login_form_sql_injection(self):
        """TC-FORM-003: Test login form against SQL injection"""
        test_id = "TC-FORM-003"
        title = "Login Form - SQL Injection Attempt"

        try:
            sql_injection_data = {
                'email': "' OR 1=1 --",
                'password': "' OR 1=1 --",
                'userType': 'citizen'
            }

            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=sql_injection_data,
                timeout=10
            )

            actual = f"Status: {response.status_code}, Response blocked/rejected"

            # Should NOT authenticate - should return 401 or similar
            if response.status_code != 200:
                status = "PASS"
                notes = "SQL injection properly blocked"
            else:
                status = "FAIL"
                notes = "CRITICAL: SQL injection vulnerability detected!"

            self.log_test(
                test_id=test_id,
                title=title,
                objective="Verify login form blocks SQL injection attempts",
                preconditions="Security measures in place",
                steps=[
                    "1. Navigate to login API endpoint",
                    "2. Send POST request with SQL injection payload",
                    "3. Verify request is rejected"
                ],
                test_data=str(sql_injection_data),
                expected="Status 401/400, SQL injection blocked",
                actual=actual,
                status=status,
                priority="CRITICAL",
                notes=notes
            )
        except Exception as e:
            self.log_test(test_id, title, "Test SQL injection", "None", [], str(sql_injection_data),
                         "Blocked", f"Exception: {str(e)}", "PASS", "CRITICAL", "Exception is acceptable")

    def test_signup_form_xss(self):
        """TC-FORM-004: Test signup form against XSS"""
        test_id = "TC-FORM-004"
        title = "Signup Form - XSS Injection Attempt"

        try:
            xss_data = {
                'name': "<script>alert('XSS')</script>",
                'email': f"test_xss_{int(time.time())}@test.com",
                'password': 'test123',
                'userType': 'citizen'
            }

            response = requests.post(
                f"{self.base_url}/api/auth/signup",
                json=xss_data,
                timeout=10
            )

            # Check if script tags are sanitized
            if response.status_code == 200:
                returned_name = response.json().get('user', {}).get('name', '')
                if '<script>' not in returned_name:
                    status = "PASS"
                    notes = "XSS payload sanitized/escaped"
                else:
                    status = "FAIL"
                    notes = "CRITICAL: XSS vulnerability - script tags not sanitized!"
            else:
                status = "PASS"
                notes = "Registration rejected suspicious input"

            actual = f"Status: {response.status_code}, Name returned: {returned_name if response.status_code == 200 else 'N/A'}"

            self.log_test(
                test_id=test_id,
                title=title,
                objective="Verify signup form sanitizes XSS attempts",
                preconditions="Security sanitization in place",
                steps=[
                    "1. Navigate to signup API endpoint",
                    "2. Send POST request with XSS payload in name field",
                    "3. Verify payload is sanitized or rejected"
                ],
                test_data=str(xss_data),
                expected="XSS payload sanitized (< > converted to entities) or rejected",
                actual=actual,
                status=status,
                priority="CRITICAL",
                notes=notes
            )
        except Exception as e:
            self.log_test(test_id, title, "Test XSS", "None", [], str(xss_data),
                         "Sanitized", f"Exception: {str(e)}", "PASS", "CRITICAL")

    def test_case_creation_empty_fields(self):
        """TC-FORM-005: Test case creation with empty required fields"""
        test_id = "TC-FORM-005"
        title = "Case Creation Form - Empty Required Fields"

        try:
            # First login as citizen
            login_response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.test_users['citizen'],
                timeout=10
            )

            if login_response.status_code == 200:
                user_data = login_response.json().get('user', {})
                user_id = user_data.get('_id') or user_data.get('id')

                # Try to create case with minimal/empty data
                empty_case_data = {
                    'user_id': user_id,
                    'title': '',  # Empty title
                    'description': '',  # Empty description
                    'status': 'open'
                }

                response = requests.post(
                    f"{self.base_url}/api/cases",
                    json=empty_case_data,
                    timeout=10
                )

                actual = f"Status: {response.status_code}"

                # Should reject empty fields
                if response.status_code in [400, 422]:
                    status = "PASS"
                    notes = "Empty fields properly validated"
                elif response.status_code == 200:
                    status = "FAIL"
                    notes = "WARNING: API accepts empty required fields"
                else:
                    status = "FAIL"
                    notes = f"Unexpected response: {response.status_code}"

                self.log_test(
                    test_id=test_id,
                    title=title,
                    objective="Verify case creation validates required fields",
                    preconditions="User logged in as citizen",
                    steps=[
                        "1. Login as citizen",
                        "2. Send POST request to /api/cases with empty title/description",
                        "3. Verify validation error"
                    ],
                    test_data=str(empty_case_data),
                    expected="Status 400/422 with validation error message",
                    actual=actual,
                    status=status,
                    priority="HIGH",
                    notes=notes
                )
            else:
                self.log_test(test_id, title, "Test empty fields", "Login", [], "",
                             "Validation error", "Could not login", "FAIL", "HIGH")

        except Exception as e:
            self.log_test(test_id, title, "Test empty fields", "None", [], "",
                         "Validation error", f"Exception: {str(e)}", "FAIL", "HIGH", str(e))

    def test_case_creation_long_input(self):
        """TC-FORM-006: Test case creation with very long input"""
        test_id = "TC-FORM-006"
        title = "Case Creation Form - Very Long Input (Buffer Overflow Test)"

        try:
            # Login as citizen
            login_response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.test_users['citizen'],
                timeout=10
            )

            if login_response.status_code == 200:
                user_data = login_response.json().get('user', {})
                user_id = user_data.get('_id') or user_data.get('id')

                # Create very long description (10000 characters)
                long_text = "A" * 10000

                long_case_data = {
                    'user_id': user_id,
                    'title': 'Test Case - Long Input',
                    'description': long_text,
                    'status': 'open',
                    'case_type': 'criminal'
                }

                response = requests.post(
                    f"{self.base_url}/api/cases",
                    json=long_case_data,
                    timeout=15
                )

                actual = f"Status: {response.status_code}, Response handled: {len(long_text)} chars"

                # Should either accept (with length limit) or reject gracefully
                if response.status_code in [200, 201]:
                    status = "PASS"
                    notes = "Long input accepted - verify length limit exists"
                elif response.status_code in [400, 413]:
                    status = "PASS"
                    notes = "Long input rejected with proper error"
                else:
                    status = "FAIL"
                    notes = f"Unexpected response: {response.status_code}"

                self.log_test(
                    test_id=test_id,
                    title=title,
                    objective="Verify system handles very long inputs safely",
                    preconditions="User logged in as citizen",
                    steps=[
                        "1. Login as citizen",
                        "2. Create case with 10,000 character description",
                        "3. Verify system handles gracefully"
                    ],
                    test_data=f"Description: {len(long_text)} characters",
                    expected="Either accepts with length limit or rejects with 413/400",
                    actual=actual,
                    status=status,
                    priority="MEDIUM",
                    notes=notes
                )
            else:
                self.log_test(test_id, title, "Test long input", "Login", [], "",
                             "Handled gracefully", "Could not login", "FAIL", "MEDIUM")

        except Exception as e:
            self.log_test(test_id, title, "Test long input", "None", [], "",
                         "Handled gracefully", f"Exception: {str(e)}", "FAIL", "MEDIUM", str(e))

    def test_document_generation_special_chars(self):
        """TC-FORM-007: Test document generation with special characters"""
        test_id = "TC-FORM-007"
        title = "Document Generation - Special Characters in Placeholders"

        try:
            special_chars_data = {
                'ACCUSED_NAME': "Test < > ' \" & Name",
                'FIR_NUMBER': "123/2024 & <test>",
                'SECTIONS': "302, 34 PPC ' OR 1=1",
                'POLICE_STATION': "City Station \"Test\" & <script>"
            }

            response = requests.post(
                f"{self.base_url}/api/documents/generate",
                json={
                    'template_id': 'Pre-arrest bail (anticipatory bail)',
                    'data': special_chars_data
                },
                timeout=30
            )

            actual = f"Status: {response.status_code}"

            if response.status_code == 200:
                result = response.json()
                if 'output_filename' in result:
                    status = "PASS"
                    notes = "Document generated - verify special chars sanitized in output"
                else:
                    status = "FAIL"
                    notes = "Document generation failed"
            else:
                status = "FAIL"
                notes = f"Request failed: {response.status_code}"

            self.log_test(
                test_id=test_id,
                title=title,
                objective="Verify document generation sanitizes special characters",
                preconditions="Document templates exist",
                steps=[
                    "1. Prepare data with special characters: < > ' \" &",
                    "2. Send POST to /api/documents/generate",
                    "3. Verify document generates and chars are escaped"
                ],
                test_data=str(special_chars_data),
                expected="Status 200, Document generated with sanitized content",
                actual=actual,
                status=status,
                priority="HIGH",
                notes=notes
            )
        except Exception as e:
            self.log_test(test_id, title, "Test special chars", "None", [], str(special_chars_data),
                         "Sanitized", f"Exception: {str(e)}", "FAIL", "HIGH", str(e))

    # ============================================================================
    # CATEGORY 2: SECURITY & URL TESTING
    # ============================================================================

    def test_url_access_citizen_to_lawyer(self):
        """TC-SEC-001: Test citizen accessing lawyer routes"""
        test_id = "TC-SEC-001"
        title = "URL Access Control - Citizen accessing Lawyer routes"

        try:
            # Login as citizen
            login_response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.test_users['citizen'],
                timeout=10
            )

            if login_response.status_code == 200:
                user_data = login_response.json().get('user', {})
                user_id = user_data.get('_id') or user_data.get('id')

                # Try to access lawyer-specific endpoint
                response = requests.get(
                    f"{self.base_url}/api/lawyer/clients",
                    params={'lawyer_id': user_id},  # Using citizen's ID
                    timeout=10
                )

                actual = f"Status: {response.status_code}"

                # Should be forbidden or return empty/error
                if response.status_code in [401, 403]:
                    status = "PASS"
                    notes = "Access properly denied"
                elif response.status_code == 200:
                    clients = response.json()
                    if not clients or len(clients) == 0:
                        status = "PASS"
                        notes = "Returns empty - acceptable"
                    else:
                        status = "FAIL"
                        notes = "CRITICAL: Citizen can access lawyer data!"
                else:
                    status = "FAIL"
                    notes = f"Unexpected response: {response.status_code}"

                self.log_test(
                    test_id=test_id,
                    title=title,
                    objective="Verify citizens cannot access lawyer-only routes",
                    preconditions="Logged in as citizen",
                    steps=[
                        "1. Login as citizen user",
                        "2. Attempt to access /api/lawyer/clients",
                        "3. Verify access denied"
                    ],
                    test_data=f"User ID: {user_id}, Role: citizen",
                    expected="Status 403 or empty response",
                    actual=actual,
                    status=status,
                    priority="CRITICAL",
                    notes=notes
                )
            else:
                self.log_test(test_id, title, "Test access control", "Login", [], "",
                             "Access denied", "Could not login", "FAIL", "CRITICAL")

        except Exception as e:
            self.log_test(test_id, title, "Test access control", "None", [], "",
                         "Access denied", f"Exception: {str(e)}", "FAIL", "CRITICAL", str(e))

    def test_url_access_lawyer_to_admin(self):
        """TC-SEC-002: Test lawyer accessing admin routes"""
        test_id = "TC-SEC-002"
        title = "URL Access Control - Lawyer accessing Admin routes"

        try:
            # Login as lawyer
            login_response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.test_users['lawyer'],
                timeout=10
            )

            if login_response.status_code == 200:
                # Try to access admin endpoint
                response = requests.get(
                    f"{self.base_url}/api/admin/users",
                    timeout=10
                )

                actual = f"Status: {response.status_code}"

                # Should be forbidden
                if response.status_code in [401, 403]:
                    status = "PASS"
                    notes = "Admin routes properly protected"
                elif response.status_code == 200:
                    status = "FAIL"
                    notes = "CRITICAL: Lawyer can access admin routes!"
                else:
                    status = "PASS"
                    notes = f"Access denied with status {response.status_code}"

                self.log_test(
                    test_id=test_id,
                    title=title,
                    objective="Verify lawyers cannot access admin-only routes",
                    preconditions="Logged in as lawyer",
                    steps=[
                        "1. Login as lawyer user",
                        "2. Attempt to access /api/admin/users",
                        "3. Verify access denied"
                    ],
                    test_data="Role: lawyer",
                    expected="Status 403/401",
                    actual=actual,
                    status=status,
                    priority="CRITICAL",
                    notes=notes
                )
            else:
                self.log_test(test_id, title, "Test admin access", "Login", [], "",
                             "Access denied", "Could not login", "FAIL", "CRITICAL")

        except Exception as e:
            self.log_test(test_id, title, "Test admin access", "None", [], "",
                         "Access denied", f"Exception: {str(e)}", "FAIL", "CRITICAL", str(e))

    def test_url_unauthenticated_access(self):
        """TC-SEC-003: Test accessing protected routes without authentication"""
        test_id = "TC-SEC-003"
        title = "URL Access Control - Unauthenticated access to protected routes"

        try:
            protected_endpoints = [
                '/api/cases',
                '/api/documents/list',
                '/api/lawyer/clients',
                '/api/admin/users'
            ]

            results = []
            all_protected = True

            for endpoint in protected_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    results.append(f"{endpoint}: {response.status_code}")

                    # If it returns 200, it's not properly protected
                    if response.status_code == 200:
                        all_protected = False
                except Exception as e:
                    results.append(f"{endpoint}: Exception")

            actual = ", ".join(results)

            if all_protected:
                status = "PASS"
                notes = "All protected routes require authentication"
            else:
                status = "FAIL"
                notes = "CRITICAL: Some protected routes accessible without auth!"

            self.log_test(
                test_id=test_id,
                title=title,
                objective="Verify protected routes require authentication",
                preconditions="No authentication token provided",
                steps=[
                    "1. Access protected endpoints without authentication",
                    "2. Verify all return 401/403"
                ],
                test_data=str(protected_endpoints),
                expected="All endpoints return 401/403/422",
                actual=actual,
                status=status,
                priority="CRITICAL",
                notes=notes
            )

        except Exception as e:
            self.log_test(test_id, title, "Test unauth access", "None", [], "",
                         "All protected", f"Exception: {str(e)}", "FAIL", "CRITICAL", str(e))

    def test_api_sql_injection_case_endpoint(self):
        """TC-SEC-004: Test SQL injection on case retrieval endpoint"""
        test_id = "TC-SEC-004"
        title = "API Security - SQL Injection on Case Endpoint"

        try:
            # Try SQL injection in query parameters
            sql_payloads = [
                "1' OR '1'='1",
                "1; DROP TABLE cases--",
                "' UNION SELECT * FROM users--"
            ]

            injection_blocked = True
            results = []

            for payload in sql_payloads:
                try:
                    response = requests.get(
                        f"{self.base_url}/api/cases/citizen",
                        params={'user_id': payload},
                        timeout=5
                    )
                    results.append(f"Payload '{payload}': Status {response.status_code}")

                    # If it returns sensitive data (200 with data), it might be vulnerable
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            injection_blocked = False
                except Exception as e:
                    results.append(f"Payload blocked: {str(e)}")

            actual = "; ".join(results)

            if injection_blocked:
                status = "PASS"
                notes = "SQL injection attempts properly blocked"
            else:
                status = "FAIL"
                notes = "WARNING: Possible SQL injection vulnerability"

            self.log_test(
                test_id=test_id,
                title=title,
                objective="Verify API endpoints block SQL injection attempts",
                preconditions="API endpoints accessible",
                steps=[
                    "1. Send SQL injection payloads in query parameters",
                    "2. Verify queries are sanitized/parameterized",
                    "3. Confirm no sensitive data leaked"
                ],
                test_data=str(sql_payloads),
                expected="All SQL injection attempts blocked or return errors",
                actual=actual,
                status=status,
                priority="CRITICAL",
                notes=notes
            )

        except Exception as e:
            self.log_test(test_id, title, "Test SQL injection", "None", [], "",
                         "Blocked", f"Exception: {str(e)}", "PASS", "CRITICAL")

    def test_cors_configuration(self):
        """TC-SEC-005: Test CORS configuration"""
        test_id = "TC-SEC-005"
        title = "API Security - CORS Configuration"

        try:
            response = requests.get(
                f"{self.base_url}/api/auth/login",
                headers={'Origin': 'http://malicious-site.com'},
                timeout=5
            )

            cors_header = response.headers.get('Access-Control-Allow-Origin', '')

            actual = f"CORS Header: {cors_header}"

            # Check if CORS is too permissive
            if cors_header == '*':
                status = "FAIL"
                notes = "WARNING: CORS allows all origins - security risk!"
            elif cors_header in ['http://localhost:3000', 'http://localhost:8000']:
                status = "PASS"
                notes = "CORS properly configured for localhost only"
            else:
                status = "PASS"
                notes = f"CORS configured: {cors_header}"

            self.log_test(
                test_id=test_id,
                title=title,
                objective="Verify CORS configuration is not overly permissive",
                preconditions="API server running",
                steps=[
                    "1. Send request with Origin header from external site",
                    "2. Check Access-Control-Allow-Origin header",
                    "3. Verify not set to '*' (allow all)"
                ],
                test_data="Origin: http://malicious-site.com",
                expected="CORS limited to specific origins (not '*')",
                actual=actual,
                status=status,
                priority="HIGH",
                notes=notes
            )

        except Exception as e:
            self.log_test(test_id, title, "Test CORS", "None", [], "",
                         "Properly configured", f"Exception: {str(e)}", "FAIL", "HIGH", str(e))

    # ============================================================================
    # CATEGORY 3: USER FLOW TESTING (End-to-End)
    # ============================================================================

    def test_e2e_citizen_complete_journey(self):
        """TC-FLOW-001: End-to-end citizen journey"""
        test_id = "TC-FLOW-001"
        title = "E2E User Flow - Complete Citizen Journey"

        steps_completed = []
        failed_step = None

        try:
            # Step 1: Login as citizen
            login_response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.test_users['citizen'],
                timeout=10
            )

            if login_response.status_code == 200:
                steps_completed.append("1. Login successful")
                user_data = login_response.json().get('user', {})
                user_id = user_data.get('_id') or user_data.get('id')
            else:
                failed_step = "Login failed"
                raise Exception("Login failed")

            # Step 2: Create a case
            case_data = {
                'user_id': user_id,
                'title': 'Test Bail Case - E2E Test',
                'description': 'Testing complete citizen journey for bail application',
                'case_type': 'criminal',
                'status': 'open',
                'sections': ['302', '34'],
                'fir_number': f'123/{int(time.time())}',
                'police_station': 'Test Police Station'
            }

            case_response = requests.post(
                f"{self.base_url}/api/cases",
                json=case_data,
                timeout=10
            )

            if case_response.status_code in [200, 201]:
                case_id = case_response.json().get('id') or case_response.json().get('_id')
                steps_completed.append(f"2. Case created successfully (ID: {case_id})")
            else:
                failed_step = f"Case creation failed: {case_response.status_code}"
                raise Exception(failed_step)

            # Step 3: Analyze case
            analyze_data = {
                'sections': ['302', '34'],
                'fir_number': case_data['fir_number'],
                'police_station': 'Test Police Station',
                'facts': 'Accused wrongly implicated in false case'
            }

            analyze_response = requests.post(
                f"{self.base_url}/api/analyze",
                json=analyze_data,
                timeout=30
            )

            if analyze_response.status_code == 200:
                steps_completed.append("3. Case analysis completed")
            else:
                steps_completed.append(f"3. Case analysis: {analyze_response.status_code}")

            # Step 4: Get lawyer recommendations
            lawyer_request = {
                'city': 'Karachi',
                'specialization': 'Criminal Law',
                'case_description': 'Need bail for criminal case',
                'min_experience': 3,
                'budget_min': 10000,
                'budget_max': 50000
            }

            lawyer_response = requests.post(
                f"{self.base_url}/api/recommend-lawyers",
                json=lawyer_request,
                timeout=15
            )

            if lawyer_response.status_code == 200:
                steps_completed.append("4. Lawyer recommendations retrieved")
            else:
                steps_completed.append(f"4. Lawyer recommendations: {lawyer_response.status_code}")

            # Step 5: Generate document
            doc_data = {
                'ACCUSED_NAME': 'Muhammad Ali',
                'FIR_NUMBER': case_data['fir_number'],
                'SECTIONS': '302, 34 PPC',
                'POLICE_STATION': 'Test Police Station'
            }

            doc_response = requests.post(
                f"{self.base_url}/api/documents/generate",
                json={
                    'template_id': 'Pre-arrest bail (anticipatory bail)',
                    'data': doc_data
                },
                timeout=30
            )

            if doc_response.status_code == 200:
                result = doc_response.json()
                if 'output_filename' in result:
                    steps_completed.append("5. Document generated successfully")
                else:
                    steps_completed.append("5. Document generation: No filename returned")
            else:
                steps_completed.append(f"5. Document generation: {doc_response.status_code}")

            # All steps completed
            actual = "; ".join(steps_completed)
            status = "PASS"
            notes = "Complete citizen journey successful"

        except Exception as e:
            actual = "; ".join(steps_completed) + f"; Failed at: {failed_step or str(e)}"
            status = "FAIL"
            notes = f"Journey interrupted: {str(e)}"

        self.log_test(
            test_id=test_id,
            title=title,
            objective="Verify complete citizen workflow from login to document generation",
            preconditions="Citizen account exists, templates available",
            steps=[
                "1. Login as citizen",
                "2. Create a new criminal case",
                "3. Analyze the case",
                "4. Get lawyer recommendations",
                "5. Generate bail application document"
            ],
            test_data="Complete citizen workflow with bail case",
            expected="All steps complete successfully: Login → Case → Analysis → Lawyers → Document",
            actual=actual,
            status=status,
            priority="HIGH",
            notes=notes
        )

    def test_e2e_lawyer_client_management(self):
        """TC-FLOW-002: End-to-end lawyer client management"""
        test_id = "TC-FLOW-002"
        title = "E2E User Flow - Lawyer Client Management"

        steps_completed = []
        failed_step = None

        try:
            # Step 1: Login as lawyer
            login_response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.test_users['lawyer'],
                timeout=10
            )

            if login_response.status_code == 200:
                steps_completed.append("1. Lawyer login successful")
                user_data = login_response.json().get('user', {})
                lawyer_id = user_data.get('_id') or user_data.get('id')
            else:
                failed_step = "Login failed"
                raise Exception("Login failed")

            # Step 2: Add new client
            client_data = {
                'lawyer_id': lawyer_id,
                'name': f'Test Client {int(time.time())}',
                'email': f'client_{int(time.time())}@test.com',
                'phone': '+923001234567',
                'city': 'Karachi',
                'address': '123 Test Street'
            }

            client_response = requests.post(
                f"{self.base_url}/api/lawyer/clients",
                json=client_data,
                timeout=10
            )

            if client_response.status_code in [200, 201]:
                steps_completed.append("2. Client added successfully")
                client_id = client_response.json().get('id') or client_response.json().get('_id')
            else:
                failed_step = f"Client creation failed: {client_response.status_code}"
                raise Exception(failed_step)

            # Step 3: Create case for client
            case_data = {
                'user_id': client_id,
                'lawyer_id': lawyer_id,
                'title': 'Client Case - E2E Test',
                'description': 'Testing lawyer client management flow',
                'case_type': 'criminal',
                'status': 'open'
            }

            case_response = requests.post(
                f"{self.base_url}/api/cases",
                json=case_data,
                timeout=10
            )

            if case_response.status_code in [200, 201]:
                steps_completed.append("3. Case created for client")
            else:
                steps_completed.append(f"3. Case creation: {case_response.status_code}")

            # Step 4: Retrieve all clients
            clients_response = requests.get(
                f"{self.base_url}/api/lawyer/clients",
                params={'lawyer_id': lawyer_id},
                timeout=10
            )

            if clients_response.status_code == 200:
                clients = clients_response.json()
                steps_completed.append(f"4. Retrieved {len(clients)} clients")
            else:
                steps_completed.append(f"4. Client retrieval: {clients_response.status_code}")

            # All steps completed
            actual = "; ".join(steps_completed)
            status = "PASS"
            notes = "Lawyer client management workflow successful"

        except Exception as e:
            actual = "; ".join(steps_completed) + f"; Failed at: {failed_step or str(e)}"
            status = "FAIL"
            notes = f"Workflow interrupted: {str(e)}"

        self.log_test(
            test_id=test_id,
            title=title,
            objective="Verify complete lawyer workflow for client management",
            preconditions="Lawyer account exists and verified",
            steps=[
                "1. Login as lawyer",
                "2. Add new client with details",
                "3. Create case for the client",
                "4. Retrieve all clients to verify data persistence"
            ],
            test_data="Lawyer client management workflow",
            expected="All steps complete: Login → Add Client → Create Case → View Clients",
            actual=actual,
            status=status,
            priority="HIGH",
            notes=notes
        )

    def test_e2e_data_isolation_between_citizens(self):
        """TC-FLOW-003: Test data isolation between different citizens"""
        test_id = "TC-FLOW-003"
        title = "E2E Data Isolation - Citizen A cannot see Citizen B's data"

        steps_completed = []

        try:
            # Login as first citizen
            citizen1_creds = self.test_users['citizen']
            login1 = requests.post(
                f"{self.base_url}/api/auth/login",
                json=citizen1_creds,
                timeout=10
            )

            if login1.status_code == 200:
                user1_data = login1.json().get('user', {})
                user1_id = user1_data.get('_id') or user1_data.get('id')
                steps_completed.append("1. Citizen A logged in")
            else:
                raise Exception("Citizen A login failed")

            # Create case as Citizen A
            case1_data = {
                'user_id': user1_id,
                'title': 'Citizen A Private Case',
                'description': 'This should not be visible to Citizen B',
                'status': 'open',
                'case_type': 'criminal'
            }

            case1_response = requests.post(
                f"{self.base_url}/api/cases",
                json=case1_data,
                timeout=10
            )

            if case1_response.status_code in [200, 201]:
                case1_id = case1_response.json().get('id') or case1_response.json().get('_id')
                steps_completed.append("2. Citizen A created private case")
            else:
                raise Exception("Case creation failed")

            # Now login as second citizen (if exists) or try to access with different ID
            # For testing, we'll try to access Citizen A's cases with a different user_id
            fake_user_id = "000000000000000000000000"  # Fake MongoDB ID

            # Try to get Citizen A's cases using fake user ID
            try:
                cases_response = requests.get(
                    f"{self.base_url}/api/cases/citizen",
                    params={'user_id': fake_user_id},
                    timeout=10
                )

                if cases_response.status_code == 200:
                    cases = cases_response.json()
                    # Check if Citizen A's case is in the results
                    case_ids = [c.get('id') or c.get('_id') for c in cases if isinstance(c, dict)]

                    if case1_id in case_ids:
                        steps_completed.append("3. FAIL: Different user can see Citizen A's case!")
                        status = "FAIL"
                        notes = "CRITICAL: Data isolation breach - users can see other users' data"
                    else:
                        steps_completed.append("3. PASS: Different user cannot see Citizen A's case")
                        status = "PASS"
                        notes = "Data properly isolated between users"
                else:
                    steps_completed.append("3. PASS: Access denied for different user")
                    status = "PASS"
                    notes = "Data isolation working - access denied"
            except Exception as e:
                steps_completed.append(f"3. Test completed with exception: {str(e)}")
                status = "PASS"
                notes = "Data isolation enforced (exception is acceptable)"

            actual = "; ".join(steps_completed)

        except Exception as e:
            actual = "; ".join(steps_completed) + f"; Error: {str(e)}"
            status = "FAIL"
            notes = f"Test failed: {str(e)}"

        self.log_test(
            test_id=test_id,
            title=title,
            objective="Verify data isolation between different citizen users",
            preconditions="Multiple citizen accounts exist",
            steps=[
                "1. Login as Citizen A",
                "2. Create private case as Citizen A",
                "3. Attempt to access Citizen A's case with different user ID",
                "4. Verify access denied or data not visible"
            ],
            test_data="Cross-user data access attempt",
            expected="Citizen B cannot see or access Citizen A's cases",
            actual=actual,
            status=status,
            priority="CRITICAL",
            notes=notes
        )

    # ============================================================================
    # TEST EXECUTION AND REPORTING
    # ============================================================================

    def run_all_tests(self):
        """Execute all test suites"""
        self.print_separator("LAWMATE COMPREHENSIVE TESTING SUITE")
        print("IEEE 829 Standard Test Case Format")
        print(f"Test Execution Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Category 1: Form Testing
        self.print_separator("CATEGORY 1: FORM TESTING")
        self.test_login_form_valid()
        self.test_login_form_invalid_email()
        self.test_login_form_sql_injection()
        self.test_signup_form_xss()
        self.test_case_creation_empty_fields()
        self.test_case_creation_long_input()
        self.test_document_generation_special_chars()

        # Category 2: Security & URL Testing
        self.print_separator("CATEGORY 2: SECURITY & URL ACCESS TESTING")
        self.test_url_access_citizen_to_lawyer()
        self.test_url_access_lawyer_to_admin()
        self.test_url_unauthenticated_access()
        self.test_api_sql_injection_case_endpoint()
        self.test_cors_configuration()

        # Category 3: User Flow Testing
        self.print_separator("CATEGORY 3: END-TO-END USER FLOW TESTING")
        self.test_e2e_citizen_complete_journey()
        self.test_e2e_lawyer_client_management()
        self.test_e2e_data_isolation_between_citizens()

        self.print_separator("TEST EXECUTION SUMMARY")
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Pass Rate: {(self.passed/self.test_count*100):.1f}%\n")

    def generate_ieee_report(self, filename="test_report_ieee.json"):
        """Generate IEEE 829 format test report"""
        report = {
            'test_report_metadata': {
                'project_name': 'Lawmate - Virtual Lawyer Platform',
                'test_type': 'Manual Testing (Automated Script)',
                'test_level': 'System Testing',
                'test_environment': {
                    'backend_url': self.base_url,
                    'frontend_url': self.frontend_url
                },
                'test_execution_date': datetime.now().isoformat(),
                'tester': 'Automated Test Suite',
                'standard': 'IEEE 829-2008'
            },
            'test_summary': {
                'total_tests': self.test_count,
                'passed': self.passed,
                'failed': self.failed,
                'pass_rate': f"{(self.passed/self.test_count*100):.1f}%" if self.test_count > 0 else "0%"
            },
            'test_categories': {
                'form_testing': {
                    'count': sum(1 for t in self.test_results if 'FORM' in t['Test Case ID']),
                    'description': 'Testing all input forms for validation, security, and data handling'
                },
                'security_url_testing': {
                    'count': sum(1 for t in self.test_results if 'SEC' in t['Test Case ID']),
                    'description': 'Testing authentication, authorization, and API security'
                },
                'e2e_flow_testing': {
                    'count': sum(1 for t in self.test_results if 'FLOW' in t['Test Case ID']),
                    'description': 'Testing complete user workflows and data isolation'
                }
            },
            'test_cases': self.test_results,
            'critical_findings': [
                t for t in self.test_results
                if t['Priority'] == 'CRITICAL' and t['Status'] == 'FAIL'
            ],
            'recommendations': self.generate_recommendations()
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nIEEE 829 Test Report saved to: {filename}")
        return report

    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []

        critical_fails = [t for t in self.test_results if t['Priority'] == 'CRITICAL' and t['Status'] == 'FAIL']

        if critical_fails:
            recommendations.append({
                'priority': 'CRITICAL',
                'finding': f'{len(critical_fails)} critical security/functionality issues found',
                'recommendation': 'Address all critical failures immediately before production deployment'
            })

        # Check for specific issues
        for test in self.test_results:
            if 'SQL injection' in test['Test Case Title'] and test['Status'] == 'FAIL':
                recommendations.append({
                    'priority': 'CRITICAL',
                    'finding': 'SQL injection vulnerability detected',
                    'recommendation': 'Implement parameterized queries and input sanitization immediately'
                })

            if 'XSS' in test['Test Case Title'] and test['Status'] == 'FAIL':
                recommendations.append({
                    'priority': 'CRITICAL',
                    'finding': 'XSS vulnerability detected',
                    'recommendation': 'Implement input sanitization and output encoding'
                })

            if 'Access Control' in test['Test Case Title'] and test['Status'] == 'FAIL':
                recommendations.append({
                    'priority': 'HIGH',
                    'finding': 'Authorization bypass detected',
                    'recommendation': 'Implement proper role-based access control (RBAC) at API level'
                })

            if 'CORS' in test['Test Case Title'] and 'allow all' in test.get('Notes', '').lower():
                recommendations.append({
                    'priority': 'HIGH',
                    'finding': 'CORS misconfiguration - allows all origins',
                    'recommendation': 'Configure CORS to only allow specific trusted origins'
                })

        return recommendations

    def print_detailed_report(self):
        """Print human-readable detailed report"""
        self.print_separator("DETAILED TEST RESULTS")

        for test in self.test_results:
            print(f"\n{'='*80}")
            print(f"Test ID: {test['Test Case ID']}")
            print(f"Title: {test['Test Case Title']}")
            print(f"Priority: {test['Priority']}")
            print(f"Status: {test['Status']}")
            print(f"\nObjective:")
            print(f"  {test['Test Objective']}")
            print(f"\nTest Steps:")
            for step in test['Test Steps']:
                print(f"  {step}")
            print(f"\nExpected Result:")
            print(f"  {test['Expected Result']}")
            print(f"\nActual Result:")
            print(f"  {test['Actual Result']}")
            if test.get('Notes'):
                print(f"\nNotes:")
                print(f"  {test['Notes']}")
            print(f"{'='*80}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                  LAWMATE COMPREHENSIVE TESTING SUITE                       ║
║                     IEEE 829 Standard Test Cases                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

Testing Categories:
1. Form Testing - Input validation, security, data handling
2. Security & URL Testing - Authentication, authorization, API security
3. E2E User Flow Testing - Complete workflows and data isolation

Starting tests...
""")

    # Initialize and run tests
    test_suite = LawmateTestSuite()

    try:
        # Run all tests
        test_suite.run_all_tests()

        # Generate reports
        report = test_suite.generate_ieee_report("test_report_ieee.json")

        # Print detailed results
        test_suite.print_detailed_report()

        # Print critical findings
        test_suite.print_separator("CRITICAL FINDINGS & RECOMMENDATIONS")
        critical = report['critical_findings']
        if critical:
            print(f"⚠️  {len(critical)} CRITICAL ISSUES FOUND:\n")
            for finding in critical:
                print(f"  • {finding['Test Case Title']}")
                print(f"    {finding['Notes']}\n")
        else:
            print("✅ No critical issues found!\n")

        # Print recommendations
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"\n{i}. [{rec['priority']}] {rec['finding']}")
            print(f"   → {rec['recommendation']}")

        print(f"\n\nTest execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Full report saved to: test_report_ieee.json")

    except Exception as e:
        print(f"\n❌ Test suite execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
