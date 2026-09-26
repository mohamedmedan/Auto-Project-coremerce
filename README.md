<div align="center">

# 🧪 Coremerce Selenium Test Suite

**A professional, framework-free end-to-end test automation suite for the [Coremerce](https://coremerce.ai) web platform.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-green?logo=selenium)](https://selenium.dev)
[![Browser](https://img.shields.io/badge/Browser-Chrome%20%7C%20Firefox%20%7C%20Edge-orange)](#)
[![Tests](https://img.shields.io/badge/Tests-110%20cases-brightgreen)](#test-coverage)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](#)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Project Structure](#-project-structure)
- [Features & Test Coverage](#-features--test-coverage)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running Tests](#-running-tests)
- [Reports](#-reports)
- [Test Design Patterns](#-test-design-patterns)

---

## 🔍 Overview

This suite automates **110 end-to-end test cases** across **4 features** of the Coremerce dashboard using pure Python + Selenium — no pytest, no external test framework. It ships its own runner, HTML reporter, and WebDriver factory, keeping dependencies minimal.

Key highlights:
- ✅ **Bilingual** — all text assertions support both **English and Arabic**
- ✅ **Multi-browser** — Chrome, Firefox, and Edge via `webdriver-manager`
- ✅ **Headless mode** — run silently in CI/CD pipelines
- ✅ **Auto screenshots** on failure
- ✅ **Self-contained HTML reports** with dark theme, filters, and per-test details
- ✅ **Interactive CLI** — pick feature, filter by key, choose browser on the fly

---

## 📁 Project Structure

```
auto-test/
│
├── 📄 run_tests.py               # Entry point — interactive + CLI runner
├── 📄 requirements.txt           # Python dependencies (3 packages)
│
├── 📂 config/
│   └── config.json               # All runtime settings (URLs, credentials, timeouts)
│
├── 📂 utils/
│   ├── driver_factory.py         # Creates WebDriver for Chrome / Firefox / Edge
│   ├── reporter.py               # Generates self-contained dark-theme HTML reports
│   └── __init__.py
│
├── 📂 tests/
│   ├── base_test.py              # Abstract BaseTest class + SkipTest exception
│   ├── registry.py               # Central test registry (FEATURES dict)
│   ├── __init__.py
│   │
│   ├── 📂 login/
│   │   ├── test_login.py         # LOGIN_001 – LOGIN_020
│   │   └── __init__.py
│   │
│   ├── 📂 register/
│   │   ├── test_register.py      # REGISTER_001 – REGISTER_020
│   │   └── __init__.py
│   │
│   ├── 📂 profile/
│   │   ├── test_profile.py       # PROFILE_001 – PROFILE_020
│   │   ├── av.png                # Test fixture — avatar image for upload tests
│   │   └── __init__.py
│   │
│   └── 📂 users/
│       ├── test_users.py         # USERS_001 – USERS_030
│       └── __init__.py
│
└── 📂 reports/
    ├── *.html                    # Generated HTML reports (one per run)
    └── screenshots/              # Failure screenshots — {KEY}_{timestamp}.png
```

---

## 🎯 Features & Test Coverage

### Total: **110 test cases** across 4 features

---

### 🔐 Login — `LOGIN_001–020` (20 tests)

Tests the `/login` page end-to-end.

| Key | Category | Description |
|-----|----------|-------------|
| LOGIN_001 | Smoke | Page loads with logo, heading, inputs, submit, forgot & register links |
| LOGIN_002 | Functional | Email field accepts and holds typed value |
| LOGIN_003 | Functional | Password field accepts and holds typed value |
| LOGIN_004 | UI | Password toggle flips input type between `password` ↔ `text` |
| LOGIN_005 | UI | Remember-me checkbox toggles state correctly |
| LOGIN_006 | Validation | Empty form fails HTML5 `checkValidity()` |
| LOGIN_007 | Validation | Invalid email `"tager"` shows HTML5 `@` error |
| LOGIN_008 | Validation | Email-only filled; password still invalid via HTML5 |
| LOGIN_009 | Auth | Wrong credentials produce a bilingual error banner |
| LOGIN_010 | Auth | Valid credentials redirect away from `/login` |
| LOGIN_011 | Navigation | Forgot-password link href contains `/forgot-password` |
| LOGIN_012 | Navigation | Register link href contains `/register` |
| LOGIN_013 | UI | Exactly 2 social buttons (Google + Apple) present |
| LOGIN_014 | UI | Legal section has Terms and Privacy links |
| LOGIN_015 | UX | Pressing Enter in password field submits or shows error |
| LOGIN_016 | UX | Email input is auto-focused on page load |
| LOGIN_017 | Security | Form method is POST; `_token` (CSRF) is present and >20 chars |
| LOGIN_018 | UI | Email and password placeholders mention the field (bilingual) |
| LOGIN_019 | UI | Submit button text contains "Sign In" (bilingual) |
| LOGIN_020 | Content | H1 heading visible with "Welcome back" text (bilingual) |

---

### 📝 Register — `REGISTER_001–020` (20 tests)

Tests the `/register` page including OTP verification flow.

| Key | Category | Description |
|-----|----------|-------------|
| REGISTER_001 | Smoke | Page loads with logo, heading, form, submit |
| REGISTER_002 | Functional | All 5 required fields present |
| REGISTER_003 | Validation | Empty form fails HTML5 `checkValidity()` |
| REGISTER_004 | Validation | Invalid email format triggers `@` validation message |
| REGISTER_005 | Validation | Short password (`Ab@1`) rejected server-side |
| REGISTER_006 | Validation | Password without symbol (`abcdefgh`) rejected server-side |
| REGISTER_007 | Validation | Unchecked terms checkbox blocks HTML5 form validity |
| REGISTER_008 | UX | `#first_name` is auto-focused on load |
| REGISTER_009 | UI | Password toggle works |
| REGISTER_010 | UI | Country code `<select>` has `+20` and ≥3 options |
| REGISTER_011 | Navigation | Login link href contains `/login` |
| REGISTER_012 | UI | Google + Apple social buttons present |
| REGISTER_013 | UI | Stepper is displayed with first step label |
| REGISTER_014 | UI | All inputs have non-empty placeholders |
| REGISTER_015 | UI | Legal section has Terms + Privacy links (bilingual) |
| REGISTER_016 | Security | Form is POST with CSRF `_token` |
| REGISTER_017 | E2E | Valid form → redirects to `/onboarding/verify-phone` with OTP inputs |
| REGISTER_018 | E2E | OTP page shows debug code (6 digits) |
| REGISTER_019 | E2E | Full flow: register → read OTP → fill → verify → navigate away |
| REGISTER_020 | Navigation | Login page has a link pointing to `/register` |

---

### 👤 Profile — `PROFILE_001–020` (20 tests)

Tests the `/profile` page (requires authentication).

| Key | Category | Description |
|-----|----------|-------------|
| PROFILE_001 | Smoke | Form, avatar, name, email, mobile inputs visible |
| PROFILE_002 | Security | Form is POST + `multipart/form-data` + CSRF token |
| PROFILE_003 | Functional | Name is pre-filled on load |
| PROFILE_004 | Functional | Email is pre-filled and contains `@` |
| PROFILE_005 | Functional | Mobile is pre-filled |
| PROFILE_006 | UI | Avatar `#blah` has a valid `src` |
| PROFILE_007 | Functional | Name field accepts input (fills, verifies, restores) |
| PROFILE_008 | Functional | Email field accepts input |
| PROFILE_009 | Functional | Mobile field accepts input |
| PROFILE_010 | UI | Submit button value contains "Save Changes" (bilingual) |
| PROFILE_011 | Validation | Clearing name + saving shows required-field error |
| PROFILE_012 | Functional | Saving unchanged data produces a success banner |
| PROFILE_013 | E2E | Change name, save → success, then restore original |
| PROFILE_014 | Validation | Invalid email `"abc"` rejected; original email unchanged after reload |
| PROFILE_015 | UI | `#file-1` input has `type=file` and `name=profile_image` |
| PROFILE_016 | UI | Selecting `av.png` changes avatar `#blah` src to blob URL |
| PROFILE_017 | E2E | Upload avatar → save → success banner |
| PROFILE_018 | Functional | Save → reload → name still persists |
| PROFILE_019 | UI | Personal Info card header visible (bilingual XPATH) |
| PROFILE_020 | Auth | Login then navigate to `/profile` without bounce |

---

### 👥 Users — `USERS_001–030` (30 tests)

Tests the `/users` dashboard page and the Create User modal form.

#### Page & UI (USERS_001–020)

| Key | Category | Description |
|-----|----------|-------------|
| USERS_001 | Smoke | Page loads with correct heading and breadcrumb |
| USERS_002 | Smoke | User cards rendered with names and emails |
| USERS_003 | Smoke | Add User button is present and visible |
| USERS_004 | UI | List View button present, href points to `/user-list` |
| USERS_005 | UI | Each user card has a valid avatar image |
| USERS_006 | UI | Each user card shows a role badge |
| USERS_007 | Functional | Clicking + opens the Add User modal |
| USERS_008 | Functional | Form has all required fields (name, email, password, approval code, role) |
| USERS_009 | Security | Form contains a valid CSRF `_token` (>20 chars) |
| USERS_010 | UI | Both Create and Cancel buttons are visible |
| USERS_011 | Functional | Role select has ≥2 options including placeholder |
| USERS_012 | Validation | Empty form fails HTML5 `checkValidity()` on name, email, role |
| USERS_013 | Validation | Invalid email format `"abc"` blocked by HTML5 with `@` message |
| USERS_014 | Validation | Approval code field has `maxlength=5`, `pattern=[0-9]{5}`, `inputmode=numeric` |
| USERS_015 | Validation | Submitting without password triggers server-side error |
| USERS_016 | Functional | Name field accepts and holds typed value |
| USERS_017 | Functional | Email field accepts and holds typed value |
| USERS_018 | Security | Password field type is `password` (masked) |
| USERS_019 | Functional | Card dropdown shows Edit and Delete with correct URLs |
| USERS_020 | Auth | `/users` redirects to `/login` when unauthenticated |

#### Create User — Full Validation (USERS_021–030)

| Key | Category | Description |
|-----|----------|-------------|
| USERS_021 | E2E | **Full create flow** — fill all fields correctly → success, user appears |
| USERS_022 | Validation | Duplicate email rejected by server |
| USERS_023 | Validation | Empty name blocked by HTML5 |
| USERS_024 | Validation | Empty email blocked by HTML5 |
| USERS_025 | Validation | Role placeholder selection blocked by HTML5 |
| USERS_026 | Validation | Invalid email format `"notanemail"` rejected by HTML5 |
| USERS_027 | Validation | Approval code input truncated at 5 characters by `maxlength` |
| USERS_028 | Validation | Non-numeric approval code rejected by `pattern` attribute |
| USERS_029 | Functional | Cancel button closes the modal without saving |
| USERS_030 | Validation | Blank password triggers server-side `"password required"` error |

---

## 🏗️ Architecture

### Test Lifecycle (per test)

```
run_tests.py  →  create_driver()  →  cls(driver, config, wait)
                                          │
                                     setup()        ← no-op by default
                                     execute()      ← test logic lives here
                                     teardown()     ← no-op by default
                                          │
                              PASSED / FAILED / ERROR / SKIPPED
                                          │
                              FAILED/ERROR → save screenshot
                              driver.quit()
```

### Dual Inheritance Pattern

Every test uses **Mixin + BaseTest** double inheritance:

```python
class Users021(UsersMixin, BaseTest):
    key         = "USERS_021"
    name        = "Create user with valid full data succeeds"
    description = "Fill all fields correctly and submit → success."
    category    = "E2E"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()
        self.fill_create_form(...)
        ...
```

- **`*Mixin`** — holds all CSS/ID locators, helper methods (`slow()`, `js()`, `dismiss_cookies()`, `safe_click_locator()`, etc.)
- **`BaseTest`** — provides `__init__(driver, config, wait)`, abstract `execute()`, and `SkipTest` exception

### Bilingual Support

All text assertions check both Arabic and English simultaneously:

```python
KEYWORDS = {
    "success": [
        "successfully", "created", "success",
        "تم", "بنجاح", "تم الإنشاء",
    ],
}
assert contains_any(page_text, KEYWORDS["success"])
```

---

## ⚙️ Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| Google Chrome / Firefox / Edge | Latest |
| pip | Any recent |

> `webdriver-manager` automatically downloads the correct browser driver binary — no manual ChromeDriver setup needed.

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/mohamedmedan/Auto-Project-coremerce.git
cd Auto-Project-coremerce

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

**Dependencies (`requirements.txt`):**
```
selenium>=4.20.0
webdriver-manager>=4.0.1
colorama>=0.4.6
```

---

## 🔧 Configuration

All settings live in `config/config.json`:

```json
{
  "report_title"    : "Coremerce Test Suite",
  "base_url"        : "https://coremerce.ai/login",
  "register_url"    : "https://coremerce.ai/register",
  "profile_url"     : "https://coremerce.ai/profile",
  "users_url"       : "https://coremerce.ai/users",
  "browser"         : "chrome",
  "headless"        : false,
  "timeout"         : 20,
  "implicit_wait"   : 5,
  "step_delay"      : 0.8,
  "report_dir"      : "reports",
  "screenshots_dir" : "reports/screenshots",
  "credentials": {
    "valid"  : { "email": "your@email.com", "password": "yourpassword" },
    "invalid": { "email": "wrong@email.com", "password": "WrongPass" }
  },
  "register_user": {
    "first_name"  : "Test",
    "last_name"   : "User",
    "email_domain": "gmail.com",
    "country_code": "+20",
    "mobile"      : "1009876543",
    "password"    : "Test@1234"
  },
  "profile": {
    "default_name"  : "tager",
    "default_mobile": "01050050050"
  }
}
```

| Key | Description |
|-----|-------------|
| `base_url` | The login page URL |
| `browser` | `chrome`, `firefox`, or `edge` |
| `headless` | `true` to run without opening a browser window |
| `timeout` | Seconds for `WebDriverWait` |
| `implicit_wait` | Selenium implicit wait in seconds |
| `step_delay` | Pause between UI actions (seconds) — reduce for faster runs |
| `credentials.valid` | Account used by login, profile, and users tests |

---

## ▶️ Running Tests

### Interactive Mode (recommended)

```bash
python run_tests.py
```

Launches a menu where you can pick a feature, filter by keys, and choose a browser.

```
+===========================================================+
|        Coremerce Selenium Test Suite Runner               |
+===========================================================+
Main Menu:

  1) Login    (20)
  2) Register (20)
  3) Profile  (20)
  4) Users    (30)
  5) All Features
  6) Custom Keys
  7) List Tests
  0) Exit
```

### CLI Mode

```bash
# Run a single feature
python run_tests.py --feature login
python run_tests.py --feature register
python run_tests.py --feature profile
python run_tests.py --feature users

# Run all features
python run_tests.py --feature all

# Run specific test keys
python run_tests.py --keys LOGIN_001,LOGIN_009,LOGIN_010

# Run specific keys within a feature
python run_tests.py --feature users --keys USERS_021,USERS_022

# Run in headless mode
python run_tests.py --feature users --headless

# Use a different browser
python run_tests.py --feature login --browser firefox

# List all tests without running
python run_tests.py --list
python run_tests.py --feature users --list
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All tests passed |
| `1` | One or more tests failed or errored |
| `2` | Bad arguments or no tests found |

---

## 📊 Reports

After each run, a self-contained HTML report is saved to `reports/`:

```
reports/report_users_20260926_143000.html
reports/screenshots/USERS_021_20260926_143005.png
```

Report features:
- **Summary cards** — Total, Passed, Failed, Errors, Skipped, Duration, Pass Rate
- **Feature cards** — per-feature pass/fail breakdown
- **Filter buttons** — show/hide rows by status (All / Passed / Failed / Errors / Skipped)
- **Per-test rows** — key, feature tag, name, description, error message, screenshot link
- **Dark theme** — fully self-contained (no external CSS/JS)

---

## 🧩 Test Design Patterns

### `SkipTest` Exception

Raised when a test can't run due to missing config or environment:

```python
if not creds.get("email"):
    raise SkipTest("credentials.valid not configured")
```

Results in `SKIPPED` status (not a failure).

### `slow()` — Configurable Step Delay

```python
def slow(self, seconds=None):
    delay = seconds if seconds is not None else self.config.get("step_delay", 0.6)
    time.sleep(delay)
```

Called between every UI interaction. Adjustable via `step_delay` in config.

### `safe_click_locator()` — Resilient Clicks

```python
def safe_click_locator(self, locator):
    el = self.wait.until(EC.presence_of_element_located(locator))
    self.js("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        self.wait.until(EC.element_to_be_clickable(locator)).click()
    except Exception:
        self.js("arguments[0].click();", el)   # JS fallback
```

### `fill_field()` — Framework-safe Input (Profile)

Handles React/Vue-managed inputs by dispatching DOM events as a fallback:

```python
# Attempt 1: native send_keys
el.clear(); el.send_keys(value)

# Attempt 2: JavaScript with event dispatch
el.value = val;
el.dispatchEvent(new Event('input', {bubbles:true}));
el.dispatchEvent(new Event('change', {bubbles:true}));
```

### Cookie Dismissal

Applied at the start of every page interaction:

```python
def dismiss_cookies(self):
    # Try clicking the accept button
    accept = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(COOKIE_ACCEPT))
    accept.click()
    # Fallback: remove banner from DOM via JavaScript
    self.js("document.getElementById('cm').remove()")
```

---

<div align="center">

Built with ❤️ for the **Coremerce** platform · Powered by **Selenium 4** · Python 3.8+

</div>
