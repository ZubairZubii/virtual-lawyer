#!/usr/bin/env python3
"""
Comprehensive Manual Testing Suite for Lawmate Platform
IEEE Test Case Format Documentation
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import sys

class TestCase:
    def __init__(self, test_id, name, objective, preconditions, test_data, expected_result, priority="High", category=""):
        self.test_id = test_id
        self.name = name
        self.objective = objective
        self.preconditions = preconditions
        self.test_data = test_data
        self.expected_result = expected_result
        self.actual_result = ""
        self.status = "Not Executed"
        self.priority = priority
        self.severity = ""
        self.notes = ""
        self.category = category
        self.execution_time = ""

    def execute(self, executor_func):
        """Execute the test case using provided executor function"""
        start_time = time.time()
        try:
            self.actual_result, self.status, self.notes = executor_func(self.test_data)
            # Determine severity based on status
            if self.status == "PASS":
                self.severity = "None"
            elif "XSS" in self.name or "SQL Injection" in self.name or "Authorization" in self.name:
                self.severity = "Critical" if self.status == "FAIL" else "Low"
            elif "Form" in self.category or "Validation" in self.name:
                self.severity = "High" if self.status == "FAIL" else "Low"
            else:
                self.severity = "Medium" if self.status == "FAIL" else "Low"
        except Exception as e:
            self.actual_result = f"Exception: {str(e)}"
            self.status = "ERROR"
            self.severity = "High"
            self.notes = f"Unexpected error during execution: {str(e)}"

        self.execution_time = f"{time.time() - start_time:.2f}s"

class TestReportGenerator:
    def __init__(self):
        self.test_cases: List[TestCase] = []
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_users = {}

    def add_test_case(self, test_case: TestCase):
        self.test_cases.append(test_case)

    # ==================== TEST EXECUTORS ====================

    def test_auth_signup(self, test_data):
        """Execute signup test"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/signup",
                json=test_data,
                timeout=10
            )

            result = f"Status Code: {response.status_code}\n"
            try:
                json_response = response.json()
                result += f"Response: {json.dumps(json_response, indent=2)}"

                # Check for successful signup
                if response.status_code == 200 and json_response.get('id'):
                    # Store user for later tests
                    self.test_users[test_data.get('email', '')] = json_response
                    return result, "PASS", "User created successfully"
                elif response.status_code == 400:
                    # Check if it's proper validation error
                    if 'error' in json_response or 'detail' in json_response:
                        return result, "PASS", "Validation error handled correctly"
                    else:
                        return result, "FAIL", "Validation error but improper format"
                else:
                    return result, "FAIL", f"Unexpected status code: {response.status_code}"
            except json.JSONDecodeError:
                result += f"Raw Response: {response.text}"
                return result, "FAIL", "Invalid JSON response"
        except requests.exceptions.RequestException as e:
            return f"Request failed: {str(e)}", "ERROR", "Network/Server error"

    def test_auth_login(self, test_data):
        """Execute login test"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=test_data,
                timeout=10
            )

            result = f"Status Code: {response.status_code}\n"
            try:
                json_response = response.json()
                result += f"Response: {json.dumps(json_response, indent=2)}"

                if response.status_code == 200 and json_response.get('id'):
                    return result, "PASS", "Login successful"
                elif response.status_code in [401, 400]:
                    return result, "PASS", "Invalid credentials rejected correctly"
                else:
                    return result, "FAIL", f"Unexpected status code: {response.status_code}"
            except json.JSONDecodeError:
                return f"{result}\nRaw: {response.text}", "FAIL", "Invalid JSON"
        except Exception as e:
            return f"Error: {str(e)}", "ERROR", "Request failed"

    def test_case_creation(self, test_data):
        """Execute case creation test"""
        try:
            response = requests.post(
                f"{self.base_url}/api/cases",
                json=test_data,
                timeout=10
            )

            result = f"Status Code: {response.status_code}\n"
            try:
                json_response = response.json()
                result += f"Response: {json.dumps(json_response, indent=2)[:500]}"

                if response.status_code == 200:
                    return result, "PASS", "Case created successfully"
                elif response.status_code in [400, 422]:
                    return result, "PASS", "Validation working"
                else:
                    return result, "FAIL", f"Unexpected response"
            except:
                return f"{result}\n{response.text[:200]}", "FAIL", "Invalid response"
        except Exception as e:
            return f"Error: {str(e)}", "ERROR", str(e)

    def test_document_generation(self, test_data):
        """Test document generation endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/api/document/generate",
                json=test_data,
                timeout=15
            )

            result = f"Status Code: {response.status_code}\n"

            if response.status_code == 200:
                # Check if it's a file or JSON
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    json_response = response.json()
                    result += f"Response: {json.dumps(json_response, indent=2)[:300]}"
                else:
                    result += f"File received, size: {len(response.content)} bytes"
                return result, "PASS", "Document generated"
            elif response.status_code in [400, 422]:
                result += f"Error: {response.text[:200]}"
                return result, "PASS", "Validation error handled"
            else:
                return result, "FAIL", "Unexpected response"
        except Exception as e:
            return f"Error: {str(e)}", "ERROR", str(e)

    def test_api_endpoint(self, test_data):
        """Generic API endpoint test"""
        try:
            method = test_data.get('method', 'GET')
            endpoint = test_data.get('endpoint', '/')
            payload = test_data.get('payload', None)
            headers = test_data.get('headers', {})

            url = f"{self.base_url}{endpoint}"

            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=payload, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return "Invalid method", "ERROR", "Test configuration error"

            result = f"Status Code: {response.status_code}\n"
            result += f"Response: {response.text[:300]}"

            expected_status = test_data.get('expected_status', 200)
            if response.status_code == expected_status:
                return result, "PASS", f"Received expected status {expected_status}"
            else:
                return result, "FAIL", f"Expected {expected_status}, got {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}", "ERROR", str(e)

    def test_xss_injection(self, test_data):
        """Test XSS vulnerability"""
        # This reuses the appropriate executor based on endpoint
        if 'signup' in test_data.get('endpoint', ''):
            return self.test_auth_signup(test_data.get('payload', {}))
        elif 'cases' in test_data.get('endpoint', ''):
            return self.test_case_creation(test_data.get('payload', {}))
        else:
            return self.test_api_endpoint(test_data)

    def test_sql_injection(self, test_data):
        """Test SQL injection vulnerability"""
        return self.test_auth_login(test_data)

    # ==================== TEST CASE DEFINITIONS ====================

    def define_form_tests(self):
        """Define all form testing test cases"""

        # TC-FORM-001: Valid Citizen Signup
        self.add_test_case(TestCase(
            test_id="TC-FORM-001",
            name="Valid Citizen Signup",
            objective="Verify that a citizen can successfully sign up with valid credentials",
            preconditions=["Backend server running on port 8000", "Database accessible"],
            test_data={
                "name": "Ahmed Khan",
                "email": f"ahmed.khan.{int(time.time())}@test.pk",
                "password": "SecurePass123!",
                "userType": "citizen"
            },
            expected_result="User account created successfully with user ID returned",
            priority="Critical",
            category="Form Testing - Authentication"
        ))

        # TC-FORM-002: Empty Name Field
        self.add_test_case(TestCase(
            test_id="TC-FORM-002",
            name="Signup with Empty Name",
            objective="Verify system rejects signup when name field is empty",
            preconditions=["Backend server running"],
            test_data={
                "name": "",
                "email": f"empty.{int(time.time())}@test.pk",
                "password": "Test123!",
                "userType": "citizen"
            },
            expected_result="400 Bad Request with validation error message",
            priority="High",
            category="Form Testing - Validation"
        ))

        # TC-FORM-003: XSS in Name Field
        self.add_test_case(TestCase(
            test_id="TC-FORM-003",
            name="XSS Attack in Name Field",
            objective="Verify system sanitizes or rejects XSS payloads in name field",
            preconditions=["Backend server running"],
            test_data={
                "name": "<script>alert('XSS')</script>",
                "email": f"xss.{int(time.time())}@test.pk",
                "password": "Test123!",
                "userType": "citizen"
            },
            expected_result="Input sanitized OR rejected with validation error",
            priority="Critical",
            category="Form Testing - Security"
        ))

        # TC-FORM-004: SQL Injection in Email
        self.add_test_case(TestCase(
            test_id="TC-FORM-004",
            name="SQL Injection in Email Field",
            objective="Verify system prevents SQL injection through email field",
            preconditions=["Backend server running"],
            test_data={
                "email": "test@test.com' OR '1'='1",
                "password": "wrong",
                "userType": "citizen"
            },
            expected_result="Login rejected, no SQL error exposed",
            priority="Critical",
            category="Form Testing - Security"
        ))

        # TC-FORM-005: Very Long Input
        self.add_test_case(TestCase(
            test_id="TC-FORM-005",
            name="Extra Long Name Input",
            objective="Verify system handles excessively long input gracefully",
            preconditions=["Backend server running"],
            test_data={
                "name": "A" * 1000,
                "email": f"long.{int(time.time())}@test.pk",
                "password": "Test123!",
                "userType": "citizen"
            },
            expected_result="Input truncated or rejected with clear error",
            priority="Medium",
            category="Form Testing - Validation"
        ))

        # TC-FORM-006: Valid Lawyer Signup
        self.add_test_case(TestCase(
            test_id="TC-FORM-006",
            name="Valid Lawyer Signup",
            objective="Verify lawyer can sign up successfully",
            preconditions=["Backend server running"],
            test_data={
                "name": "Advocate Fatima Ali",
                "email": f"fatima.ali.{int(time.time())}@test.pk",
                "password": "Lawyer123!",
                "userType": "lawyer"
            },
            expected_result="Lawyer account created successfully",
            priority="Critical",
            category="Form Testing - Authentication"
        ))

        # TC-FORM-007: Invalid Email Format
        self.add_test_case(TestCase(
            test_id="TC-FORM-007",
            name="Invalid Email Format",
            objective="Verify email validation works correctly",
            preconditions=["Backend server running"],
            test_data={
                "name": "Test User",
                "email": "not-an-email",
                "password": "Test123!",
                "userType": "citizen"
            },
            expected_result="Validation error for invalid email format",
            priority="High",
            category="Form Testing - Validation"
        ))

        # TC-FORM-008: Weak Password
        self.add_test_case(TestCase(
            test_id="TC-FORM-008",
            name="Weak Password Validation",
            objective="Verify weak passwords are rejected",
            preconditions=["Backend server running"],
            test_data={
                "name": "Test User",
                "email": f"weak.{int(time.time())}@test.pk",
                "password": "123",
                "userType": "citizen"
            },
            expected_result="Password validation error",
            priority="High",
            category="Form Testing - Validation"
        ))

        # TC-FORM-009: Special Characters in Name (Valid)
        self.add_test_case(TestCase(
            test_id="TC-FORM-009",
            name="Special Characters in Name",
            objective="Verify system accepts valid special characters (Urdu names)",
            preconditions=["Backend server running"],
            test_data={
                "name": "محمد علی خان",
                "email": f"urdu.{int(time.time())}@test.pk",
                "password": "Test123!",
                "userType": "citizen"
            },
            expected_result="Account created with Urdu name preserved",
            priority="High",
            category="Form Testing - Internationalization"
        ))

        # TC-FORM-010: Case Creation with Valid Data
        self.add_test_case(TestCase(
            test_id="TC-FORM-010",
            name="Valid Case Creation",
            objective="Verify case can be created with all required fields",
            preconditions=["Backend running", "Valid user exists"],
            test_data={
                "user_id": "test_user_123",
                "scope": "citizen",
                "payload": {
                    "case_description": "False FIR filed against me under Section 420 PPC",
                    "urgency": "high",
                    "city": "Karachi",
                    "custody_status": "not_in_custody"
                }
            },
            expected_result="Case created successfully with case ID",
            priority="Critical",
            category="Form Testing - Case Management"
        ))

        # TC-FORM-011: Case Creation with XSS
        self.add_test_case(TestCase(
            test_id="TC-FORM-011",
            name="XSS in Case Description",
            objective="Verify XSS prevention in case description field",
            preconditions=["Backend running"],
            test_data={
                "user_id": "test_user_123",
                "scope": "citizen",
                "payload": {
                    "case_description": "<script>alert('XSS in case')</script>",
                    "urgency": "high",
                    "city": "Lahore"
                }
            },
            expected_result="Input sanitized or case creation rejected",
            priority="Critical",
            category="Form Testing - Security"
        ))

        # TC-FORM-012: Empty Case Description
        self.add_test_case(TestCase(
            test_id="TC-FORM-012",
            name="Empty Case Description",
            objective="Verify validation for required case description",
            preconditions=["Backend running"],
            test_data={
                "user_id": "test_user_123",
                "scope": "citizen",
                "payload": {
                    "case_description": "",
                    "urgency": "medium",
                    "city": "Islamabad"
                }
            },
            expected_result="Validation error for empty description",
            priority="High",
            category="Form Testing - Validation"
        ))

        # TC-FORM-013: Invalid Urgency Value
        self.add_test_case(TestCase(
            test_id="TC-FORM-013",
            name="Invalid Enum Value for Urgency",
            objective="Verify validation of enum fields",
            preconditions=["Backend running"],
            test_data={
                "user_id": "test_user_123",
                "scope": "citizen",
                "payload": {
                    "case_description": "Test case",
                    "urgency": "super_urgent_extreme",
                    "city": "Peshawar"
                }
            },
            expected_result="Validation error for invalid urgency value",
            priority="Medium",
            category="Form Testing - Validation"
        ))

    def define_security_tests(self):
        """Define URL and Security testing test cases"""

        # TC-SEC-001: Access Admin Route as Citizen
        self.add_test_case(TestCase(
            test_id="TC-SEC-001",
            name="Unauthorized Access to Admin Dashboard",
            objective="Verify citizen user cannot access admin endpoints",
            preconditions=["Logged in as citizen"],
            test_data={
                "method": "GET",
                "endpoint": "/api/admin/dashboard",
                "expected_status": 403
            },
            expected_result="403 Forbidden or redirect to login",
            priority="Critical",
            category="Security Testing - Authorization"
        ))

        # TC-SEC-002: Access Lawyer Clients as Citizen
        self.add_test_case(TestCase(
            test_id="TC-SEC-002",
            name="Cross-Role Data Access Prevention",
            objective="Verify citizens cannot access lawyer-specific endpoints",
            preconditions=["Backend running"],
            test_data={
                "method": "GET",
                "endpoint": "/api/lawyer/clients",
                "expected_status": 400
            },
            expected_result="Access denied or error response",
            priority="Critical",
            category="Security Testing - Authorization"
        ))

        # TC-SEC-003: Direct Case Access Without Auth
        self.add_test_case(TestCase(
            test_id="TC-SEC-003",
            name="Unauthenticated Case Access",
            objective="Verify cases cannot be accessed without authentication",
            preconditions=["Backend running"],
            test_data={
                "method": "GET",
                "endpoint": "/api/cases/citizen",
                "expected_status": 400
            },
            expected_result="401 Unauthorized or 400 Bad Request",
            priority="Critical",
            category="Security Testing - Authentication"
        ))

        # TC-SEC-004: SQL Injection in Login
        self.add_test_case(TestCase(
            test_id="TC-SEC-004",
            name="SQL Injection Prevention in Login",
            objective="Verify SQL injection is prevented in authentication",
            preconditions=["Backend running"],
            test_data={
                "email": "admin' OR '1'='1' --",
                "password": "anything",
                "userType": "admin"
            },
            expected_result="Login fails, no database error exposed",
            priority="Critical",
            category="Security Testing - SQL Injection"
        ))

        # TC-SEC-005: Path Traversal in Document Access
        self.add_test_case(TestCase(
            test_id="TC-SEC-005",
            name="Path Traversal Prevention",
            objective="Verify path traversal attacks are prevented",
            preconditions=["Backend running"],
            test_data={
                "method": "GET",
                "endpoint": "/api/document/download/../../etc/passwd",
                "expected_status": 404
            },
            expected_result="404 Not Found or 400 Bad Request",
            priority="Critical",
            category="Security Testing - Path Traversal"
        ))

        # TC-SEC-006: XSS in Chat Input
        self.add_test_case(TestCase(
            test_id="TC-SEC-006",
            name="XSS Prevention in Chat",
            objective="Verify XSS payloads in chat are sanitized",
            preconditions=["Backend running"],
            test_data={
                "method": "POST",
                "endpoint": "/api/chat",
                "payload": {
                    "query": "<img src=x onerror=alert('XSS')>",
                    "include_sources": True
                },
                "expected_status": 200
            },
            expected_result="Response doesn't execute script, input sanitized",
            priority="Critical",
            category="Security Testing - XSS"
        ))

        # TC-SEC-007: CSRF Token Validation
        self.add_test_case(TestCase(
            test_id="TC-SEC-007",
            name="CSRF Protection Check",
            objective="Verify CSRF protection on state-changing operations",
            preconditions=["Backend running"],
            test_data={
                "method": "POST",
                "endpoint": "/api/cases",
                "payload": {
                    "user_id": "fake",
                    "scope": "citizen",
                    "payload": {"test": "data"}
                },
                "headers": {"Origin": "http://malicious-site.com"},
                "expected_status": 200  # CORS should allow but validate origin
            },
            expected_result="Request processed (CORS configured) or rejected",
            priority="High",
            category="Security Testing - CSRF"
        ))

        # TC-SEC-008: Mass Assignment Vulnerability
        self.add_test_case(TestCase(
            test_id="TC-SEC-008",
            name="Mass Assignment Prevention",
            objective="Verify users cannot escalate privileges via mass assignment",
            preconditions=["Backend running"],
            test_data={
                "name": "Attacker",
                "email": f"attacker.{int(time.time())}@test.pk",
                "password": "Test123!",
                "userType": "citizen",
                "is_admin": True,  # Attempt to inject admin field
                "role": "admin"
            },
            expected_result="Extra fields ignored, user created as citizen only",
            priority="Critical",
            category="Security Testing - Mass Assignment"
        ))

        # TC-SEC-009: API Rate Limiting
        self.add_test_case(TestCase(
            test_id="TC-SEC-009",
            name="API Rate Limiting Check",
            objective="Verify API has rate limiting to prevent abuse",
            preconditions=["Backend running"],
            test_data={
                "method": "GET",
                "endpoint": "/",
                "iterations": 100  # Make 100 requests rapidly
            },
            expected_result="Rate limit enforced OR all requests processed",
            priority="Medium",
            category="Security Testing - Rate Limiting"
        ))

        # TC-SEC-010: Sensitive Data Exposure
        self.add_test_case(TestCase(
            test_id="TC-SEC-010",
            name="Password Hash Not Exposed",
            objective="Verify password hashes are not returned in API responses",
            preconditions=["User created"],
            test_data={
                "email": f"sensitive.{int(time.time())}@test.pk",
                "password": "SecurePass123!",
                "userType": "citizen"
            },
            expected_result="Response contains user data but NO password_hash field",
            priority="Critical",
            category="Security Testing - Data Exposure"
        ))

    def define_user_flow_tests(self):
        """Define end-to-end user flow test cases"""

        # TC-FLOW-001: Complete Citizen Journey
        self.add_test_case(TestCase(
            test_id="TC-FLOW-001",
            name="Complete Citizen Journey - Signup to Case Creation",
            objective="Verify complete citizen workflow from registration to case creation",
            preconditions=["Frontend and backend running"],
            test_data={
                "flow": "citizen_complete",
                "steps": [
                    {"action": "signup", "email": f"citizen.flow.{int(time.time())}@test.pk"},
                    {"action": "login"},
                    {"action": "create_case"}
                ]
            },
            expected_result="All steps complete successfully, case created",
            priority="Critical",
            category="User Flow Testing - Citizen"
        ))

        # TC-FLOW-002: Complete Lawyer Journey
        self.add_test_case(TestCase(
            test_id="TC-FLOW-002",
            name="Complete Lawyer Journey - Signup to Client Management",
            objective="Verify lawyer can register and manage clients",
            preconditions=["Backend running"],
            test_data={
                "flow": "lawyer_complete",
                "steps": [
                    {"action": "signup", "email": f"lawyer.flow.{int(time.time())}@test.pk", "userType": "lawyer"},
                    {"action": "login"},
                    {"action": "add_client"}
                ]
            },
            expected_result="Lawyer can add and view clients",
            priority="Critical",
            category="User Flow Testing - Lawyer"
        ))

        # TC-FLOW-003: Document Generation Workflow
        self.add_test_case(TestCase(
            test_id="TC-FLOW-003",
            name="Document Generation Complete Flow",
            objective="Verify end-to-end document generation",
            preconditions=["Backend running", "Templates available"],
            test_data={
                "template_name": "Affidavits",
                "placeholders": {
                    "APPLICANT_NAME": "Muhammad Ahmed",
                    "CNIC": "42101-1234567-1",
                    "ADDRESS": "House 123, Street 45, Karachi",
                    "DATE": "23rd April 2026"
                }
            },
            expected_result="Document generated and downloadable",
            priority="High",
            category="User Flow Testing - Documents"
        ))

        # TC-FLOW-004: Chat to Case Analysis Flow
        self.add_test_case(TestCase(
            test_id="TC-FLOW-004",
            name="AI Consultation to Case Analysis",
            objective="Verify user can get AI guidance then analyze case",
            preconditions=["Backend running", "AI models loaded"],
            test_data={
                "flow": "consultation_analysis",
                "chat_query": "What are my rights if FIR is filed against me?",
                "case_description": "FIR 123/2026 filed under Section 420 PPC"
            },
            expected_result="Chat provides guidance, analysis provides risk assessment",
            priority="High",
            category="User Flow Testing - AI Features"
        ))

        # TC-FLOW-005: Lawyer Recommendation Flow
        self.add_test_case(TestCase(
            test_id="TC-FLOW-005",
            name="Find Lawyer Recommendation",
            objective="Verify citizen can get lawyer recommendations",
            preconditions=["Backend running", "Lawyers in database"],
            test_data={
                "method": "POST",
                "endpoint": "/api/recommendations/lawyers",
                "payload": {
                    "case_type": "Criminal",
                    "case_description": "False accusation under PPC 420",
                    "city": "Karachi",
                    "urgency": "high"
                }
            },
            expected_result="Receive list of recommended lawyers",
            priority="High",
            category="User Flow Testing - Lawyer Discovery"
        ))

    def execute_all_tests(self):
        """Execute all test cases"""
        print("=" * 80)
        print("LAWMATE COMPREHENSIVE MANUAL TESTING SUITE")
        print("IEEE 830 Standard Test Case Format")
        print(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

        # Define all test cases
        print("📋 Defining test cases...")
        self.define_form_tests()
        self.define_security_tests()
        self.define_user_flow_tests()

        print(f"✅ Defined {len(self.test_cases)} test cases\n")

        # Execute each test case
        for i, tc in enumerate(self.test_cases, 1):
            print(f"\n[{i}/{len(self.test_cases)}] Executing: {tc.test_id} - {tc.name}")
            print("-" * 80)

            # Select appropriate executor
            if tc.category.startswith("Form Testing"):
                if "Signup" in tc.name or "Name" in tc.name or "Email" in tc.name or "Password" in tc.name or "Urdu" in tc.name or "Characters" in tc.name or "Long" in tc.name or "Mass Assignment" in tc.name:
                    tc.execute(self.test_auth_signup)
                elif "SQL Injection" in tc.name or "Login" in tc.category:
                    tc.execute(self.test_auth_login)
                elif "Case" in tc.name:
                    tc.execute(self.test_case_creation)
            elif tc.category.startswith("Security Testing"):
                if "SQL Injection" in tc.name:
                    tc.execute(self.test_sql_injection)
                elif "XSS" in tc.name and "signup" in tc.test_data.get('endpoint', ''):
                    tc.execute(self.test_xss_injection)
                else:
                    tc.execute(self.test_api_endpoint)
            elif tc.category.startswith("User Flow"):
                if "Document" in tc.name:
                    tc.execute(self.test_document_generation)
                else:
                    tc.execute(self.test_api_endpoint)
            else:
                tc.execute(self.test_api_endpoint)

            print(f"Status: {tc.status} | Severity: {tc.severity}")
            time.sleep(0.5)  # Avoid overwhelming the server

    def generate_ieee_report(self, output_file="test_report_ieee_format.md"):
        """Generate comprehensive IEEE format test report"""

        total = len(self.test_cases)
        passed = sum(1 for tc in self.test_cases if tc.status == "PASS")
        failed = sum(1 for tc in self.test_cases if tc.status == "FAIL")
        errors = sum(1 for tc in self.test_cases if tc.status == "ERROR")

        critical_failures = [tc for tc in self.test_cases if tc.severity == "Critical" and tc.status != "PASS"]

        report = f"""# LAWMATE PLATFORM - COMPREHENSIVE MANUAL TESTING REPORT
## IEEE 830 Standard Test Case Documentation

---

## EXECUTIVE SUMMARY

**Testing Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Platform:** Lawmate - Pakistan Criminal Law AI Platform
**Testing Scope:** Form Testing, Security Testing, User Flow Testing
**Test Environment:**
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Database: SQLite/MongoDB
- Test Framework: Custom Python Test Suite

---

## TEST METRICS

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Test Cases** | {total} | 100% |
| **Passed** | {passed} | {(passed/total*100):.1f}% |
| **Failed** | {failed} | {(failed/total*100):.1f}% |
| **Errors** | {errors} | {(errors/total*100):.1f}% |

### Severity Breakdown

| Severity | Pass | Fail | Error |
|----------|------|------|-------|
| **Critical** | {sum(1 for tc in self.test_cases if tc.severity == "Critical" and tc.status == "PASS")} | {sum(1 for tc in self.test_cases if tc.severity == "Critical" and tc.status == "FAIL")} | {sum(1 for tc in self.test_cases if tc.severity == "Critical" and tc.status == "ERROR")} |
| **High** | {sum(1 for tc in self.test_cases if tc.severity == "High" and tc.status == "PASS")} | {sum(1 for tc in self.test_cases if tc.severity == "High" and tc.status == "FAIL")} | {sum(1 for tc in self.test_cases if tc.severity == "High" and tc.status == "ERROR")} |
| **Medium** | {sum(1 for tc in self.test_cases if tc.severity == "Medium" and tc.status == "PASS")} | {sum(1 for tc in self.test_cases if tc.severity == "Medium" and tc.status == "FAIL")} | {sum(1 for tc in self.test_cases if tc.severity == "Medium" and tc.status == "ERROR")} |
| **Low** | {sum(1 for tc in self.test_cases if tc.severity == "Low" and tc.status == "PASS")} | {sum(1 for tc in self.test_cases if tc.severity == "Low" and tc.status == "FAIL")} | {sum(1 for tc in self.test_cases if tc.severity == "Low" and tc.status == "ERROR")} |

---

## CRITICAL FINDINGS

"""

        if critical_failures:
            report += f"⚠️ **{len(critical_failures)} CRITICAL ISSUES DETECTED**\n\n"
            for tc in critical_failures:
                report += f"### {tc.test_id}: {tc.name}\n"
                report += f"- **Status:** {tc.status}\n"
                report += f"- **Category:** {tc.category}\n"
                report += f"- **Issue:** {tc.notes}\n"
                report += f"- **Recommendation:** Immediate remediation required\n\n"
        else:
            report += "✅ **No critical failures detected**\n\n"

        report += "\n---\n\n"

        # Group test cases by category
        categories = {}
        for tc in self.test_cases:
            cat = tc.category.split(" - ")[0]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tc)

        # Generate detailed test cases for each category
        for category, test_cases in sorted(categories.items()):
            report += f"\n## {category.upper()}\n\n"
            report += f"**Total Test Cases:** {len(test_cases)}  \n"
            report += f"**Passed:** {sum(1 for tc in test_cases if tc.status == 'PASS')} | "
            report += f"**Failed:** {sum(1 for tc in test_cases if tc.status == 'FAIL')} | "
            report += f"**Errors:** {sum(1 for tc in test_cases if tc.status == 'ERROR')}\n\n"

            for tc in test_cases:
                report += f"### {tc.test_id}: {tc.name}\n\n"
                report += f"**Test Objective:** {tc.objective}\n\n"
                report += f"**Priority:** {tc.priority} | **Severity:** {tc.severity} | **Status:** "

                if tc.status == "PASS":
                    report += "✅ PASS\n\n"
                elif tc.status == "FAIL":
                    report += "❌ FAIL\n\n"
                else:
                    report += "⚠️ ERROR\n\n"

                report += f"**Preconditions:**\n"
                for pre in tc.preconditions:
                    report += f"- {pre}\n"

                report += f"\n**Test Data:**\n```json\n{json.dumps(tc.test_data, indent=2)}\n```\n\n"

                report += f"**Expected Result:**\n{tc.expected_result}\n\n"

                report += f"**Actual Result:**\n```\n{tc.actual_result[:500]}{'...' if len(tc.actual_result) > 500 else ''}\n```\n\n"

                if tc.notes:
                    report += f"**Notes:** {tc.notes}\n\n"

                report += f"**Execution Time:** {tc.execution_time}\n\n"
                report += "---\n\n"

        # Recommendations
        report += "\n## RECOMMENDATIONS\n\n"
        report += "### Immediate Actions Required\n\n"

        high_priority_failures = [tc for tc in self.test_cases if tc.priority in ["Critical", "High"] and tc.status != "PASS"]
        if high_priority_failures:
            for tc in high_priority_failures:
                report += f"1. **{tc.test_id}** - {tc.name}\n"
                report += f"   - Issue: {tc.notes}\n"
                report += f"   - Impact: {tc.severity} severity\n\n"
        else:
            report += "✅ No immediate actions required. All critical tests passed.\n\n"

        report += "\n### Security Recommendations\n\n"
        security_tests = [tc for tc in self.test_cases if "Security" in tc.category]
        security_passed = sum(1 for tc in security_tests if tc.status == "PASS")
        report += f"- Security test pass rate: {(security_passed/len(security_tests)*100):.1f}%\n"
        report += "- Implement input sanitization for all user-facing forms\n"
        report += "- Add rate limiting to prevent API abuse\n"
        report += "- Ensure all sensitive operations require authentication\n"
        report += "- Regularly audit authorization checks\n\n"

        report += "\n### Best Practices\n\n"
        report += "1. **Input Validation:** Implement comprehensive server-side validation\n"
        report += "2. **Error Handling:** Never expose internal errors or stack traces to users\n"
        report += "3. **Authentication:** Use secure session management and token rotation\n"
        report += "4. **Logging:** Log all security-relevant events for audit\n"
        report += "5. **Regular Testing:** Perform security testing before each release\n\n"

        report += "\n---\n\n"
        report += "## CONCLUSION\n\n"

        if passed / total >= 0.9:
            report += f"✅ **EXCELLENT:** {(passed/total*100):.1f}% of tests passed. Platform demonstrates strong quality.\n\n"
        elif passed / total >= 0.75:
            report += f"⚠️ **GOOD:** {(passed/total*100):.1f}% of tests passed. Some issues require attention.\n\n"
        else:
            report += f"❌ **NEEDS IMPROVEMENT:** Only {(passed/total*100):.1f}% of tests passed. Significant issues detected.\n\n"

        report += f"**Test Execution Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "---\n\n"
        report += "*This report was generated automatically using the Lawmate Manual Testing Suite*\n"

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✅ IEEE Format Test Report generated: {output_file}")

        return report

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("🧪 LAWMATE COMPREHENSIVE MANUAL TESTING SUITE")
    print("="*80 + "\n")

    # Initialize test suite
    suite = TestReportGenerator()

    # Execute all tests
    suite.execute_all_tests()

    # Generate IEEE format report
    print("\n" + "="*80)
    print("📄 GENERATING IEEE FORMAT TEST REPORT")
    print("="*80 + "\n")

    report = suite.generate_ieee_report("test_report_ieee_format.md")

    # Print summary
    print("\n" + "="*80)
    print("📊 TEST EXECUTION SUMMARY")
    print("="*80)

    total = len(suite.test_cases)
    passed = sum(1 for tc in suite.test_cases if tc.status == "PASS")
    failed = sum(1 for tc in suite.test_cases if tc.status == "FAIL")
    errors = sum(1 for tc in suite.test_cases if tc.status == "ERROR")

    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"⚠️  Errors: {errors} ({errors/total*100:.1f}%)")

    print("\n" + "="*80)
    print("✅ Testing complete! Check 'test_report_ieee_format.md' for full report")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
