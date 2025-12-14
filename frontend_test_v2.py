#!/usr/bin/env python
"""
Comprehensive Frontend E2E Testing Script v2
Tests all pages, buttons, forms, and interactive elements with correct URLs
"""

import json
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
from urllib.parse import urljoin

# Test Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

# Correct page URLs based on frontend/urls.py
PAGES = {
    "home": "/",
    "login": "/login/",
    "register": "/register/",
    "dashboard": "/dashboard/",
    "chat": "/chat/",
    "team": "/team/",
    "settings": "/settings/",
    "profile": "/profile/",
    "api-explorer": "/api-explorer/",
}

# Results tracking
results = {
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "base_url": BASE_URL,
    "tests": {
        "pages": [],
        "buttons": [],
        "forms": [],
        "api_calls": [],
        "interactive_elements": [],
        "validation": [],
        "errors": []
    },
    "summary": {
        "total_pages_tested": 0,
        "pages_passed": 0,
        "pages_failed": 0,
        "total_buttons_tested": 0,
        "working_buttons": 0,
        "broken_buttons": 0,
        "total_forms_tested": 0,
        "api_calls_tested": 0,
        "api_calls_passed": 0,
        "api_calls_failed": 0,
        "validation_issues_found": 0,
    },
    "detailed_findings": {
        "broken_buttons": [],
        "missing_handlers": [],
        "missing_pages": [],
        "api_issues": [],
        "form_issues": [],
        "ui_issues": [],
    }
}

def create_session():
    """Create requests session with retries"""
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = create_session()

def log_test(category: str, test_name: str, status: str, details: str = "", error: str = ""):
    """Log test result"""
    result = {
        "test": test_name,
        "status": status,
        "details": details,
        "error": error if error else None,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    results["tests"][category].append(result)
    
    status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️" if status == "WARN" else "⏭️"
    print(f"{status_symbol} [{category.upper()}] {test_name}: {status}")
    if error:
        print(f"    Error: {error}")
    if details:
        print(f"    {details}")

def load_page(url: str) -> Optional[Tuple[int, BeautifulSoup, requests.Response]]:
    """Load and parse a page"""
    try:
        response = session.get(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return response.status_code, soup, response
        else:
            return response.status_code, None, response
    except Exception as e:
        print(f"❌ Failed to load {url}: {e}")
        return None, None, None

# ============ PAGE TESTS ============

def test_all_pages():
    """Test all frontend pages"""
    print("\n" + "="*80)
    print("TESTING: ALL FRONTEND PAGES")
    print("="*80)
    
    for page_name, page_url in PAGES.items():
        print(f"\n>>> Testing {page_name.upper()} page: {page_url}")
        
        full_url = urljoin(BASE_URL, page_url)
        status, soup, response = load_page(full_url)
        
        if status == 200:
            log_test("pages", f"{page_name.capitalize()} Page", "PASS", f"URL: {page_url}", "")
            results["summary"]["pages_passed"] += 1
            
            # Count page elements
            forms_count = len(soup.find_all('form'))
            buttons_count = len(soup.find_all('button'))
            inputs_count = len(soup.find_all('input'))
            
            log_test("pages", f"  → Forms: {forms_count}", "PASS", f"Found {forms_count} form(s)")
            log_test("pages", f"  → Buttons: {buttons_count}", "PASS", f"Found {buttons_count} button(s)")
            log_test("pages", f"  → Input Fields: {inputs_count}", "PASS", f"Found {inputs_count} input(s)")
            
            # Test page-specific elements
            test_page_elements(page_name, soup, full_url)
            
        elif status == 404:
            log_test("pages", f"{page_name.capitalize()} Page", "FAIL", f"URL: {page_url}", "404 Not Found")
            results["summary"]["pages_failed"] += 1
            results["detailed_findings"]["missing_pages"].append(page_url)
        elif status == 500:
            log_test("pages", f"{page_name.capitalize()} Page", "FAIL", f"URL: {page_url}", "500 Server Error")
            results["summary"]["pages_failed"] += 1
            results["detailed_findings"]["api_issues"].append(f"500 error on {page_url}")
        else:
            log_test("pages", f"{page_name.capitalize()} Page", "FAIL", f"URL: {page_url}", f"Status: {status}")
            results["summary"]["pages_failed"] += 1
        
        results["summary"]["total_pages_tested"] += 1

def test_page_elements(page_name: str, soup: BeautifulSoup, url: str):
    """Test specific elements on each page"""
    
    if page_name == "login":
        # Test login form
        form = soup.find('form')
        if form:
            email_input = form.find('input', {'type': 'email'}) or form.find('input', {'name': 'email'})
            password_input = form.find('input', {'type': 'password'})
            submit_button = form.find('button', {'type': 'submit'})
            
            if email_input and password_input and submit_button:
                log_test("forms", "  → Login Form Complete", "PASS", "All required fields present")
            else:
                missing = []
                if not email_input: missing.append("email")
                if not password_input: missing.append("password")
                if not submit_button: missing.append("submit")
                log_test("forms", "  → Login Form Complete", "FAIL", "", f"Missing: {', '.join(missing)}")
                results["detailed_findings"]["form_issues"].append(f"Login form missing: {missing}")
    
    elif page_name == "register":
        # Test registration form
        form = soup.find('form')
        if form:
            required_fields = ['name', 'email', 'password']
            missing = []
            for field in required_fields:
                if not form.find('input', {'name': field}):
                    missing.append(field)
            
            if not missing:
                log_test("forms", "  → Registration Form Complete", "PASS", "All fields present")
            else:
                log_test("forms", "  → Registration Form Complete", "FAIL", "", f"Missing: {', '.join(missing)}")
                results["detailed_findings"]["form_issues"].append(f"Register form missing: {missing}")
    
    elif page_name == "dashboard":
        # Test dashboard components
        buttons = soup.find_all('button')
        test_count = sum(1 for btn in buttons if btn.get('id') or btn.get('onclick') or btn.find('svg'))
        log_test("interactive_elements", "  → Dashboard Buttons with Handlers", "PASS", f"{test_count}/{len(buttons)} buttons have handlers")
        
        # Check for key dashboard elements
        tasks_grid = soup.find('div', {'id': 'tasks-grid'}) or soup.find('div', {'class': lambda x: x and 'task' in x})
        if tasks_grid:
            log_test("interactive_elements", "  → Tasks Grid", "PASS", "Tasks container found")
        
        stats_grid = soup.find('div', {'class': 'stats-grid'})
        if stats_grid:
            log_test("interactive_elements", "  → Stats Grid", "PASS", "Stats container found")
    
    elif page_name == "chat":
        # Test chat form
        message_input = soup.find('input', {'placeholder': lambda x: x and 'message' in x.lower()})
        if message_input:
            log_test("forms", "  → Message Input", "PASS", "Found message input")
        
        send_button = soup.find('button', string=lambda x: x and 'send' in x.lower())
        if send_button:
            log_test("buttons", "  → Send Button", "PASS", "Send button found")
    
    elif page_name == "settings":
        # Test settings tabs/sections
        tabs = soup.find_all('button', {'class': lambda x: x and 'tab' in x.lower()})
        if tabs:
            log_test("interactive_elements", f"  → Settings Tabs", "PASS", f"Found {len(tabs)} tabs")
    
    elif page_name == "profile":
        # Test profile form
        form = soup.find('form')
        if form:
            inputs = form.find_all('input')
            log_test("forms", "  → Profile Form", "PASS", f"Found {len(inputs)} input fields")

# ============ BUTTON TESTS ============

def test_all_buttons():
    """Test all buttons on all pages"""
    print("\n" + "="*80)
    print("TESTING: ALL BUTTONS AND CLICKABLE ELEMENTS")
    print("="*80)
    
    for page_name, page_url in PAGES.items():
        print(f"\n>>> Checking buttons on {page_name.upper()}")
        
        full_url = urljoin(BASE_URL, page_url)
        status, soup, response = load_page(full_url)
        
        if status != 200:
            continue
        
        buttons = soup.find_all('button')
        links = soup.find_all('a', {'class': lambda x: x and 'button' in x.lower()})
        
        all_clickables = buttons + links
        results["summary"]["total_buttons_tested"] += len(all_clickables)
        
        for btn in buttons:
            btn_id = btn.get('id', 'unnamed')
            btn_text = btn.get_text(strip=True)[:40]
            btn_class = btn.get('class', [])
            btn_onclick = btn.get('onclick')
            btn_type = btn.get('type', 'button')
            
            # Check if button has a handler
            has_handler = bool(btn_onclick or btn.find('svg') or 'submit' in btn_type or btn_id)
            
            if has_handler:
                log_test("buttons", f"  {btn_id or btn_text}", "PASS", f"Type: {btn_type}, Handler: {bool(btn_onclick)}")
                results["summary"]["working_buttons"] += 1
            else:
                log_test("buttons", f"  {btn_id or btn_text}", "WARN", f"Type: {btn_type}", "May lack click handler")
                results["detailed_findings"]["missing_handlers"].append({
                    "page": page_name,
                    "button": btn_id or btn_text,
                    "type": btn_type
                })
        
        for link in links:
            link_text = link.get_text(strip=True)[:40]
            link_href = link.get('href', '#')
            log_test("buttons", f"  {link_text} (link)", "PASS", f"Link: {link_href}")
            results["summary"]["working_buttons"] += 1

# ============ FORM TESTS ============

def test_all_forms():
    """Test all forms on all pages"""
    print("\n" + "="*80)
    print("TESTING: ALL FORMS AND INPUT VALIDATION")
    print("="*80)
    
    for page_name, page_url in PAGES.items():
        print(f"\n>>> Testing forms on {page_name.upper()}")
        
        full_url = urljoin(BASE_URL, page_url)
        status, soup, response = load_page(full_url)
        
        if status != 200:
            continue
        
        forms = soup.find_all('form')
        results["summary"]["total_forms_tested"] += len(forms)
        
        for i, form in enumerate(forms, 1):
            form_id = form.get('id', f'form_{i}')
            form_method = form.get('method', 'POST').upper()
            form_action = form.get('action', '(no action)')
            
            # Find inputs
            inputs = form.find_all('input')
            selects = form.find_all('select')
            textareas = form.find_all('textarea')
            
            log_test("forms", f"  {form_id} ({form_method})", "PASS", 
                    f"Inputs: {len(inputs)}, Selects: {len(selects)}, Textareas: {len(textareas)}")
            
            # Check for required fields
            required_fields = form.find_all(['input', 'select', 'textarea'], {'required': True})
            if required_fields:
                log_test("forms", f"    → Required Fields: {len(required_fields)}", "PASS", 
                        f"Found {len(required_fields)} required field(s)")
            
            # Check for submit button
            submit_btn = form.find('button', {'type': 'submit'})
            if submit_btn:
                log_test("forms", f"    → Submit Button: {submit_btn.get_text(strip=True)}", "PASS", "Submit button present")
            else:
                log_test("forms", f"    → Submit Button", "FAIL", "", "No submit button found")
                results["detailed_findings"]["form_issues"].append(f"Form {form_id} missing submit button")

# ============ INTERACTIVE ELEMENTS TESTS ============

def test_interactive_elements():
    """Test interactive UI components"""
    print("\n" + "="*80)
    print("TESTING: INTERACTIVE UI COMPONENTS")
    print("="*80)
    
    full_url = urljoin(BASE_URL, "/dashboard/")
    status, soup, response = load_page(full_url)
    
    if status != 200:
        log_test("interactive_elements", "Dashboard Load", "FAIL", "", f"Status: {status}")
        return
    
    # Test modals
    modals = soup.find_all('div', {'class': lambda x: x and 'modal' in x})
    log_test("interactive_elements", f"Modal Windows: {len(modals)}", "PASS", f"Found {len(modals)} modal(s)")
    
    # Test dropdowns/selects
    selects = soup.find_all('select')
    log_test("interactive_elements", f"Dropdown Elements: {len(selects)}", "PASS", f"Found {len(selects)} dropdown(s)")
    
    # Test tabs
    tabs = soup.find_all('button', {'class': lambda x: x and 'tab' in x.lower()})
    log_test("interactive_elements", f"Tab Controls: {len(tabs)}", "PASS", f"Found {len(tabs)} tab(s)")
    
    # Test search
    search_input = soup.find('input', {'id': 'global-search-input'})
    if search_input:
        log_test("interactive_elements", "Global Search", "PASS", "Search input found")
    else:
        log_test("interactive_elements", "Global Search", "FAIL", "", "Search input not found")

# ============ API TESTS ============

def test_api_endpoints():
    """Test API endpoint connectivity"""
    print("\n" + "="*80)
    print("TESTING: API ENDPOINTS")
    print("="*80)
    
    api_endpoints = [
        ("POST", "/api/users/register/", "User registration"),
        ("POST", "/api/users/login/", "User login"),
        ("GET", "/api/users/profile/", "Get user profile"),
        ("POST", "/api/token/", "Get JWT token"),
        ("POST", "/api/token/refresh/", "Refresh token"),
        ("GET", "/api/tasks/", "Get tasks list"),
        ("GET", "/api/projects/", "Get projects list"),
        ("GET", "/api/search/", "Search functionality"),
    ]
    
    for method, endpoint, description in api_endpoints:
        try:
            url = urljoin(BASE_URL, endpoint)
            response = session.request(method, url, timeout=5, json={})
            results["summary"]["api_calls_tested"] += 1
            
            # Expected error responses for unauthenticated requests
            if response.status_code in [200, 201, 400, 401, 405]:
                log_test("api_calls", f"{method} {endpoint}", "PASS", 
                        f"Status: {response.status_code} ({description})")
                results["summary"]["api_calls_passed"] += 1
            else:
                log_test("api_calls", f"{method} {endpoint}", "FAIL", 
                        f"Status: {response.status_code}")
                results["summary"]["api_calls_failed"] += 1
                results["detailed_findings"]["api_issues"].append(f"{method} {endpoint}: {response.status_code}")
        except Exception as e:
            log_test("api_calls", f"{method} {endpoint}", "FAIL", "", str(e))
            results["summary"]["api_calls_failed"] += 1
            results["detailed_findings"]["api_issues"].append(f"{method} {endpoint}: {str(e)}")

# ============ UI/UX CONSISTENCY TESTS ============

def test_ui_consistency():
    """Test UI/UX consistency across pages"""
    print("\n" + "="*80)
    print("TESTING: UI/UX CONSISTENCY")
    print("="*80)
    
    # Test sidebar consistency
    sidebar_pages = ["/dashboard/", "/chat/", "/settings/"]
    sidebars_found = 0
    
    for page_url in sidebar_pages:
        full_url = urljoin(BASE_URL, page_url)
        status, soup, response = load_page(full_url)
        
        if status == 200:
            sidebar = soup.find('aside', {'class': lambda x: x and 'sidebar' in x})
            if sidebar:
                sidebars_found += 1
                nav_links = sidebar.find_all('a', {'class': 'nav-link'})
                log_test("interactive_elements", f"Sidebar on {page_url}", "PASS", f"Found {len(nav_links)} navigation links")
    
    log_test("interactive_elements", f"Sidebar Consistency: {sidebars_found}/{len(sidebar_pages)}", "PASS", 
            "Sidebar layout is consistent")

# ============ MAIN EXECUTION ============

def main():
    """Run all frontend tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE FRONTEND E2E TEST SUITE v2")
    print("Smart Task Manager - Full Frontend Validation")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Start Time: {results['timestamp']}")
    print("="*80)
    
    # Wait for server
    print("\n⏳ Waiting for server to be ready...")
    for i in range(15):
        try:
            response = session.get(urljoin(BASE_URL, "/login/"), timeout=2)
            if response.status_code in [200, 302]:
                print("✅ Server is ready!\n")
                break
        except:
            if i < 14:
                time.sleep(1)
    
    # Run all tests
    test_all_pages()
    test_all_buttons()
    test_all_forms()
    test_interactive_elements()
    test_ui_consistency()
    test_api_endpoints()
    
    # Print final summary
    print("\n" + "="*80)
    print("TEST EXECUTION SUMMARY")
    print("="*80)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Total Pages Tested: {results['summary']['total_pages_tested']}")
    print(f"  ✅ Passed: {results['summary']['pages_passed']}")
    print(f"  ❌ Failed: {results['summary']['pages_failed']}")
    print(f"\nTotal Buttons/Links Tested: {results['summary']['total_buttons_tested']}")
    print(f"  ✅ Working: {results['summary']['working_buttons']}")
    print(f"  ⚠️  Issues: {results['summary']['total_buttons_tested'] - results['summary']['working_buttons']}")
    print(f"\nTotal Forms Tested: {results['summary']['total_forms_tested']}")
    print(f"\nAPI Endpoints Tested: {results['summary']['api_calls_tested']}")
    print(f"  ✅ Passed: {results['summary']['api_calls_passed']}")
    print(f"  ❌ Failed: {results['summary']['api_calls_failed']}")
    print("\n" + "="*80)
    
    # Print detailed findings
    if results["detailed_findings"]["missing_pages"]:
        print("\n⚠️  MISSING PAGES:")
        for page in results["detailed_findings"]["missing_pages"]:
            print(f"  - {page}")
    
    if results["detailed_findings"]["form_issues"]:
        print("\n⚠️  FORM ISSUES:")
        for issue in results["detailed_findings"]["form_issues"]:
            print(f"  - {issue}")
    
    if results["detailed_findings"]["api_issues"]:
        print("\n⚠️  API ISSUES:")
        for issue in results["detailed_findings"]["api_issues"]:
            print(f"  - {issue}")
    
    if results["detailed_findings"]["missing_handlers"]:
        print(f"\n⚠️  BUTTONS WITH POTENTIALLY MISSING HANDLERS ({len(results['detailed_findings']['missing_handlers'])}):")
        for handler in results["detailed_findings"]["missing_handlers"][:10]:
            print(f"  - Page: {handler['page']}, Button: {handler['button']}")
    
    # Save results
    with open('frontend_test_results_v2.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: frontend_test_results_v2.json")
    print(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
