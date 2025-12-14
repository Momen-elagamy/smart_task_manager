# FRONTEND TESTING CHECKLIST & ROADMAP

## Pre-Testing Setup
- [ ] Django development server running (`python manage.py runserver`)
- [ ] All database migrations applied
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Test database populated with sample data (optional)
- [ ] Browser developer tools console clear of errors
- [ ] Network tab ready to monitor API calls

---

## PAGE TESTING CHECKLIST

### ✅ Home Page (`/`)
- [ ] Page loads without errors
- [ ] All navigation links visible
- [ ] Logo clickable
- [ ] Mobile responsive layout
- [ ] No console errors
- [ ] Page title correct
- [ ] Meta tags present

### ✅ Login Page (`/login/`)
- [ ] Form renders correctly
- [ ] Email field present and focused
- [ ] Password field present
- [ ] "Sign In" button visible
- [ ] "Don't have account?" → `/register/` works
- [ ] "Forgot password?" link functional
- [ ] Google OAuth button visible
- [ ] GitHub OAuth button visible
- [ ] Form styling consistent
- [ ] Mobile responsive

### ✅ Registration Page (`/register/`)
- [ ] Form renders correctly
- [ ] All input fields present (name, email, password, password confirm)
- [ ] Email validation active
- [ ] Password strength indicator (if exists)
- [ ] Terms & conditions checkbox
- [ ] "Create Account" button functional
- [ ] "Already have account?" → `/login/` works
- [ ] OAuth buttons visible
- [ ] Form data cleared after submission
- [ ] Mobile responsive

### ✅ Dashboard Page (`/dashboard/`)
- [ ] Page loads after login
- [ ] "My Tasks" header visible
- [ ] Stats grid displays correctly
- [ ] Task list loads
- [ ] Filter buttons functional (All, Pending, In Progress, Completed, High Priority)
- [ ] Search input responsive
- [ ] Sort dropdown works
- [ ] "New Task" button functional
- [ ] Refresh button works
- [ ] Filter button opens modal
- [ ] All modals can be closed
- [ ] Pagination works (if applicable)
- [ ] No broken images/icons
- [ ] Mobile responsive layout

### 🟡 Chat Page (`/chat/`)
- [ ] **CURRENTLY BROKEN - 500 SERVER ERROR**
- [ ] Page loads without error
- [ ] Chat sidebar displays
- [ ] Conversation list populated
- [ ] Message input field present
- [ ] Send button functional
- [ ] Message history displays
- [ ] User avatars show
- [ ] Timestamps correct
- [ ] Real-time updates work (if WebSocket implemented)

### 🟡 Team Page (`/team/`)
- [ ] **CURRENTLY BROKEN - 404 (NEEDS AUTH)**
- [ ] Requires login
- [ ] Displays list of team members
- [ ] User cards display correctly
- [ ] Edit/manage options work
- [ ] Add member button functional
- [ ] Remove member confirmation
- [ ] Search team members works
- [ ] Pagination works

### 🟡 Settings Page (`/settings/`)
- [ ] **CURRENTLY BROKEN - 404 (NEEDS AUTH)**
- [ ] Requires login
- [ ] Settings tabs visible
- [ ] Save button functional
- [ ] Changes persist
- [ ] Confirmation messages appear
- [ ] Validation errors display
- [ ] Theme toggle works (if exists)
- [ ] Notification settings work
- [ ] Password change works

### 🟡 Profile Page (`/profile/`)
- [ ] **CURRENTLY BROKEN - 404 (NEEDS AUTH)**
- [ ] Requires login
- [ ] User profile form displays
- [ ] Email field present
- [ ] Name field present
- [ ] Phone field present
- [ ] Profile picture upload works
- [ ] Save button functional
- [ ] Changes persist
- [ ] Edit button toggles edit mode

### ✅ API Explorer Page (`/api-explorer/`)
- [ ] Page loads correctly
- [ ] All buttons present
- [ ] API endpoint list displays
- [ ] Request builder functional
- [ ] Response displays correctly
- [ ] Clear button works
- [ ] No console errors

---

## BUTTON TESTING CHECKLIST

### Login Page Buttons
- [ ] **Submit Button ("Sign In")**
  - [ ] Clickable
  - [ ] Shows loading state
  - [ ] Submits form on Enter key
  - [ ] Validates inputs before submit
  - [ ] Error message on fail
  - [ ] Success redirect on success

- [ ] **Google OAuth Button**
  - [ ] Clickable
  - [ ] Opens OAuth dialog
  - [ ] Redirects to Google login
  - [ ] Closes dialog after auth

- [ ] **GitHub OAuth Button**
  - [ ] Clickable
  - [ ] Opens OAuth dialog
  - [ ] Redirects to GitHub
  - [ ] Closes dialog after auth

- [ ] **Sign Up Link**
  - [ ] Clickable
  - [ ] Navigates to `/register/`
  - [ ] Preserves previous data (if applicable)

### Dashboard Buttons
- [ ] **Filter Button**
  - [ ] Opens filter modal
  - [ ] All filters working
  - [ ] Can clear filters
  - [ ] Filters persist on reload

- [ ] **Refresh Button**
  - [ ] Reloads task list
  - [ ] Shows loading state
  - [ ] Updates timestamps
  - [ ] Maintains scroll position

- [ ] **New Task Button**
  - [ ] Opens create task modal
  - [ ] Form clears on open
  - [ ] Modal closes on cancel
  - [ ] Task creates on submit

- [ ] **Tab Buttons (All/Pending/In Progress/Completed/High)**
  - [ ] Each tab switches view
  - [ ] Selected tab highlights
  - [ ] Task count updates
  - [ ] Preserves scroll position

- [ ] **Close Modal Buttons (X)**
  - [ ] Closes modal
  - [ ] Discards unsaved changes (with warning)
  - [ ] Restores focus to trigger button

---

## FORM TESTING CHECKLIST

### Login Form
- [ ] **Email Field**
  - [ ] Accepts text input
  - [ ] Shows error on invalid email
  - [ ] Trims whitespace
  - [ ] Accepts valid email formats
  - [ ] Not required until submit

- [ ] **Password Field**
  - [ ] Masks password (dots/asterisks)
  - [ ] Toggle visibility button works
  - [ ] Accepts special characters
  - [ ] Minimum length enforced
  - [ ] Copy/paste works

- [ ] **Submit Button**
  - [ ] Disabled until valid
  - [ ] Shows loading spinner
  - [ ] API call made on submit
  - [ ] Error handling works
  - [ ] Success redirect works

- [ ] **Form Validation**
  - [ ] Empty email rejected
  - [ ] Invalid email rejected
  - [ ] Empty password rejected
  - [ ] Short password rejected
  - [ ] Error messages clear
  - [ ] Multiple errors show all

### Registration Form
- [ ] **Name Field**
  - [ ] Accepts text input
  - [ ] Trimmed on blur
  - [ ] Special characters allowed
  - [ ] Minimum 2 characters
  - [ ] Maximum 50 characters

- [ ] **Email Field**
  - [ ] Valid format required
  - [ ] Duplicate check (if backend enabled)
  - [ ] Trimmed whitespace
  - [ ] Not case-sensitive for storage

- [ ] **Password Fields**
  - [ ] Both visible toggle work
  - [ ] Match validation works
  - [ ] Strength indicator present (if exists)
  - [ ] Special chars required (if policy)
  - [ ] Minimum 8 characters

- [ ] **Terms Checkbox**
  - [ ] Must be checked to submit
  - [ ] Link to terms opens modal
  - [ ] Validated on submit

### Task Creation Form
- [ ] **Title Field**
  - [ ] Required
  - [ ] Accepts max 200 chars
  - [ ] Trimmed on save

- [ ] **Description Field**
  - [ ] Optional
  - [ ] Rich text editor (if exists)
  - [ ] Markdown support (if exists)
  - [ ] Auto-saves draft (if exists)

- [ ] **Priority Dropdown**
  - [ ] Required
  - [ ] All options visible
  - [ ] Default selected
  - [ ] Selected option preserves

- [ ] **Status Dropdown**
  - [ ] Required
  - [ ] Default: "Pending"
  - [ ] All statuses available
  - [ ] Selection persists

- [ ] **Project Dropdown**
  - [ ] Optional
  - [ ] All projects listed
  - [ ] Search works (if many projects)
  - [ ] Selection persists

---

## INPUT VALIDATION TESTING

### Email Validation
- [ ] Valid: `user@example.com` ✅
- [ ] Valid: `user+tag@example.co.uk` ✅
- [ ] Invalid: `user@` ❌
- [ ] Invalid: `@example.com` ❌
- [ ] Invalid: `userexample.com` ❌
- [ ] Invalid: `user@.com` ❌
- [ ] Invalid: `user @example.com` (space) ❌

### Password Validation
- [ ] Length: Min 8 characters ✅
- [ ] Length: Max 128 characters ✅
- [ ] Special chars: Allowed ✅
- [ ] Numbers: Allowed ✅
- [ ] Uppercase: Allowed ✅
- [ ] Lowercase: Allowed ✅
- [ ] Whitespace only: Rejected ❌
- [ ] Common passwords: Rejected (if configured) ❌

### Text Field Validation
- [ ] Empty string: Rejected for required ❌
- [ ] Whitespace only: Treated as empty ❌
- [ ] Leading/trailing spaces: Trimmed ✅
- [ ] Special characters: Allowed ✅
- [ ] Emoji: Allowed/rejected (depends on field) ✅/❌
- [ ] HTML tags: Escaped ✅
- [ ] SQL injection: Sanitized ✅

---

## API TESTING CHECKLIST

### POST /api/users/register/
- [ ] Accepts valid JSON
- [ ] Validates email format
- [ ] Validates password match
- [ ] Rejects duplicate email
- [ ] Returns 201 Created on success
- [ ] Returns 400 on validation error
- [ ] Returns 500 on server error
- [ ] Response includes user data
- [ ] Password not included in response

### POST /api/users/login/
- [ ] Accepts email & password
- [ ] Returns tokens on success
- [ ] Returns 401 on invalid creds
- [ ] Rate limiting (if configured)
- [ ] Response includes access_token
- [ ] Response includes refresh_token
- [ ] Token expiry included

### GET /api/users/profile/
- [ ] Requires authentication
- [ ] Returns 401 if not logged in
- [ ] Returns user profile data
- [ ] Includes email, name, phone
- [ ] Includes profile picture URL
- [ ] Includes role/permissions
- [ ] No sensitive data exposed

### GET /api/tasks/
- [ ] Requires authentication
- [ ] Returns task list
- [ ] Pagination works (if enabled)
- [ ] Filtering by status works
- [ ] Search works
- [ ] Sorting works
- [ ] Returns 200 on success

### GET /api/projects/
- [ ] **CURRENTLY RETURNS 404**
- [ ] Should return projects list
- [ ] Should support pagination
- [ ] Should support filtering
- [ ] Should return 200 on success

### GET /api/search/
- [ ] **CURRENTLY WORKING (200)**
- [ ] Accepts search query
- [ ] Returns results
- [ ] Can search tasks
- [ ] Can search projects
- [ ] Can search people (if applicable)

### POST /api/token/
- [ ] Accepts credentials
- [ ] Returns access_token
- [ ] Returns refresh_token
- [ ] Token format valid (JWT)
- [ ] Token expiry set correctly

---

## ERROR HANDLING CHECKLIST

### Network Errors
- [ ] 404 Not Found
  - [ ] Friendly error message
  - [ ] Suggested actions
  - [ ] Back button available

- [ ] 500 Server Error
  - [ ] Error message shows
  - [ ] Retry button available
  - [ ] Error logged

- [ ] Network Timeout
  - [ ] Graceful degradation
  - [ ] Retry option
  - [ ] User notification

### Validation Errors
- [ ] Errors appear near field
- [ ] Error text is clear
- [ ] Error color is distinct (red/pink)
- [ ] Multiple errors show all
- [ ] Error disappears on fix

### API Errors
- [ ] Authentication errors handled
- [ ] Authorization errors handled
- [ ] Rate limit errors handled
- [ ] Server errors handled
- [ ] Network errors handled

---

## ACCESSIBILITY CHECKLIST

### Keyboard Navigation
- [ ] Tab order logical
- [ ] Skip links present (if needed)
- [ ] Focus visible
- [ ] Enter key submits forms
- [ ] Escape closes modals
- [ ] Arrow keys in dropdowns

### Screen Readers
- [ ] Page title announced
- [ ] Form labels associated
- [ ] Error messages announced
- [ ] Button purposes clear
- [ ] Images have alt text
- [ ] Landmarks present (nav, main, etc.)

### Visual Accessibility
- [ ] Sufficient color contrast
- [ ] Not color-only information
- [ ] Text resizable
- [ ] No text smaller than 12px
- [ ] Spacing adequate
- [ ] No animated GIFs (or pausable)

---

## PERFORMANCE CHECKLIST

### Load Time
- [ ] Homepage < 2 seconds
- [ ] Login page < 1.5 seconds
- [ ] Dashboard < 2.5 seconds
- [ ] Smooth scrolling
- [ ] No jank/stutter

### Network
- [ ] CSS minified
- [ ] JavaScript minified
- [ ] Images optimized
- [ ] Lazy loading implemented
- [ ] Caching headers set

### Resources
- [ ] No memory leaks
- [ ] Console clean
- [ ] No unused CSS
- [ ] No unused JavaScript
- [ ] Compression enabled

---

## MOBILE/RESPONSIVE TESTING

### iPhone/Small Screens (375px)
- [ ] Layout adapts
- [ ] Touch targets ≥ 44px
- [ ] No horizontal scroll
- [ ] Text readable
- [ ] Forms work

### Tablet/Medium Screens (768px)
- [ ] Layout optimized
- [ ] Touch areas adequate
- [ ] Multi-column layout used
- [ ] No overflow

### Desktop/Large Screens (1920px+)
- [ ] Max-width container used
- [ ] Horizontal scroll avoided
- [ ] Layout doesn't feel stretched
- [ ] Whitespace appropriate

---

## SECURITY CHECKLIST

### Input Security
- [ ] No XSS vulnerabilities
- [ ] HTML entities escaped
- [ ] SQL injection prevented
- [ ] CSRF protection active
- [ ] File uploads validated

### Authentication
- [ ] Passwords hashed (never stored plaintext)
- [ ] Tokens signed (JWT)
- [ ] Sessions secure
- [ ] Logout clears data
- [ ] Session timeout works

### Data Protection
- [ ] HTTPS enforced (if production)
- [ ] Sensitive data not in logs
- [ ] Sensitive data not in local storage unencrypted
- [ ] API keys not in frontend code
- [ ] CORS properly configured

---

## BROWSER COMPATIBILITY

### Chromium-based (Chrome, Edge, Opera)
- [ ] Latest version
- [ ] Previous version
- [ ] Version -2

### Firefox
- [ ] Latest version
- [ ] Previous version

### Safari
- [ ] Latest version
- [ ] Previous version

### Mobile Browsers
- [ ] Chrome Mobile
- [ ] Safari Mobile
- [ ] Samsung Internet

---

## BUG TRACKING TEMPLATE

When bugs are found, document as follows:

```
BUG REPORT TEMPLATE
==================

Bug ID: [AUTO-GENERATED]
Date Found: [DATE]
Tested By: [NAME]
Severity: [CRITICAL|HIGH|MEDIUM|LOW]

TITLE: [BRIEF DESCRIPTION]

DESCRIPTION:
[Detailed description of the issue]

STEPS TO REPRODUCE:
1. [Step 1]
2. [Step 2]
3. [Step 3]

EXPECTED RESULT:
[What should happen]

ACTUAL RESULT:
[What actually happened]

SCREENSHOT/VIDEO:
[Attach if possible]

ENVIRONMENT:
- Browser: [Chrome 120]
- OS: [Windows 11]
- Device: [Desktop]
- Screen Resolution: [1920x1080]

ROOT CAUSE:
[If known]

PROPOSED FIX:
[If known]

STATUS: [NEW|IN PROGRESS|FIXED|VERIFIED|CLOSED]
ASSIGNED TO: [DEVELOPER NAME]
```

---

## REGRESSION TEST CHECKLIST

After each bug fix, re-test:

- [ ] The specific bug is fixed
- [ ] Related features still work
- [ ] No new errors in console
- [ ] Performance not degraded
- [ ] Mobile still responsive
- [ ] Accessibility still works

---

## SIGN-OFF CHECKLIST

When testing complete, verify:

- [ ] All critical bugs fixed
- [ ] All high priority bugs addressed
- [ ] Test results documented
- [ ] Screenshots/videos captured
- [ ] Report generated
- [ ] Team notified
- [ ] Stakeholders updated
- [ ] Ready for QA/production

---

## TESTING RESOURCES

### Test Data
- **Test User 1:** `testuser1@example.com` / `Password123!`
- **Test User 2:** `testuser2@example.com` / `Password456!`
- **Sample Task Data:** Located in `fixtures/sample_tasks.json`
- **Sample Project Data:** Located in `fixtures/sample_projects.json`

### Tools
- Django Development Server: `python manage.py runserver`
- Database GUI: `python manage.py dbshell`
- Shell: `python manage.py shell`
- Testing Script: `python frontend_test_v2.py`
- Results: `frontend_test_results_v2.json`

### Documentation
- Frontend Report: `FRONTEND_TEST_REPORT.md`
- Executive Summary: `FRONTEND_TEST_EXECUTIVE_SUMMARY.md`
- This Checklist: `FRONTEND_TESTING_CHECKLIST.md`

---

**Last Updated:** November 23, 2025  
**Status:** Ready for QA Testing  
**Next Review:** After fixes implemented

