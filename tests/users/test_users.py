import time
import uuid

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.base_test import BaseTest, SkipTest


# ══════════════════════════════════════════════════════════════
#  Bilingual keyword sets
# ══════════════════════════════════════════════════════════════
KEYWORDS = {
    "users_heading": [
        "users", "المستخدمون", "المستخدمين",
    ],
    "add_user": [
        "add user", "create new user", "إضافة مستخدم", "مستخدم جديد",
    ],
    "name_label": [
        "name", "الاسم",
    ],
    "email_label": [
        "email", "البريد", "الإلكتروني",
    ],
    "password_label": [
        "password", "كلمة المرور",
    ],
    "role_label": [
        "user role", "role", "الدور", "الصلاحية",
    ],
    "approval_code_label": [
        "approval code", "كود الموافقة",
    ],
    "create_btn": [
        "create", "إنشاء",
    ],
    "cancel_btn": [
        "cancel", "إلغاء",
    ],
    "required_error": [
        "required", "this field is required", "مطلوب", "هذا الحقل مطلوب",
    ],
    "password_required": [
        "password field is required", "password is required",
        "حقل كلمة المرور مطلوب", "كلمة المرور مطلوبة",
    ],
    "invalid_format": [
        "invalid format", "invalid", "تنسيق غير صالح",
    ],
    "success": [
        "successfully", "created", "added", "success",
        "تم", "بنجاح", "تم الإنشاء", "تمت الإضافة",
    ],
    "edit": [
        "edit", "update", "تعديل", "تحديث",
    ],
    "delete": [
        "delete", "remove", "حذف",
    ],
    "reset_password": [
        "reset password", "change password", "إعادة تعيين كلمة المرور",
    ],
}

ERROR_SELECTORS = [
    (By.CSS_SELECTOR, ".alert-danger"),
    (By.CSS_SELECTOR, ".alert-error"),
    (By.CSS_SELECTOR, ".invalid-feedback"),
    (By.CSS_SELECTOR, ".text-danger"),
    (By.CSS_SELECTOR, ".error-message"),
    (By.CSS_SELECTOR, "[role='alert']"),
    (By.CSS_SELECTOR, "div.alert"),
    (By.CSS_SELECTOR, ".form-error"),
    (By.CSS_SELECTOR, ".error"),
    (By.CSS_SELECTOR, "label.error"),
]

SUCCESS_SELECTORS = [
    (By.CSS_SELECTOR, ".alert-success"),
    (By.CSS_SELECTOR, ".toast-success"),
    (By.CSS_SELECTOR, ".swal2-success"),
    (By.CSS_SELECTOR, ".flash-message"),
    (By.CSS_SELECTOR, "[role='alert'].alert-success"),
    (By.CSS_SELECTOR, ".notification-success"),
]


def contains_any(text, keywords):
    if not text:
        return False
    low = text.lower()
    return any(k.lower() in low for k in keywords)


# ══════════════════════════════════════════════════════════════
#  UsersMixin — locators + helpers
# ══════════════════════════════════════════════════════════════
class UsersMixin:
    feature = "users"

    # ── Page-level locators ───────────────────────────────
    PAGE_HEADING    = (By.CSS_SELECTOR, ".page-header-title h2")
    BREADCRUMB      = (By.CSS_SELECTOR, "ul.breadcrumb")
    ADD_USER_BTN    = (By.CSS_SELECTOR, "a[data-url*='/users/create']")
    USER_CARDS      = (By.CSS_SELECTOR, ".delivery-user-cards .card")
    CARD_NAMES      = (By.CSS_SELECTOR, ".delivery-user-cards h4.text-primary")
    CARD_EMAILS     = (By.CSS_SELECTOR, ".delivery-user-cards small")
    CARD_AVATARS    = (By.CSS_SELECTOR, ".delivery-user-cards .img-user")
    CARD_BADGES     = (By.CSS_SELECTOR, ".delivery-user-cards .badge")
    LIST_VIEW_BTN   = (By.CSS_SELECTOR, "a[href*='user-list']")
    CREATE_NEW_LINK = (By.CSS_SELECTOR, "a.btn-addnew-project")

    # ── Dropdown action locators (per-card) ───────────────
    DROPDOWN_TOGGLE = (By.CSS_SELECTOR, ".card-option .dropdown-toggle")
    EDIT_ACTION     = (By.CSS_SELECTOR, "a[data-url*='/users/'][data-url*='/edit']")
    RESET_PWD_ACTION= (By.CSS_SELECTOR, "a[data-url*='store-reset-password']")
    DELETE_ACTION   = (By.CSS_SELECTOR, "a.show_confirm")

    # ── Create-user modal form locators ───────────────────
    MODAL           = (By.CSS_SELECTOR, ".modal.show, .modal[style*='display: block']")
    FORM            = (By.CSS_SELECTOR, "form[action*='/users']")
    FORM_NAME       = (By.ID, "name")
    FORM_EMAIL      = (By.ID, "email")
    FORM_PASSWORD   = (By.ID, "password")
    FORM_APPROVAL   = (By.ID, "approval_code")
    FORM_ROLE       = (By.ID, "role")
    FORM_SUBMIT     = (By.CSS_SELECTOR, "input[type='submit'][value='Create']")
    FORM_CANCEL     = (By.CSS_SELECTOR, "input[type='button'][value='Cancel']")
    FORM_TOKEN      = (By.CSS_SELECTOR, "form[action*='/users'] input[name='_token']")

    # ── Cookie banner ─────────────────────────────────────
    COOKIE_ACCEPT   = (By.ID, "c-p-bn")

    # ══════════════════════════════════════════════════════
    #  Low-level helpers
    # ══════════════════════════════════════════════════════
    def slow(self, seconds=None):
        delay = seconds if seconds is not None else self.config.get("step_delay", 0.6)
        try:
            delay = float(delay)
        except (TypeError, ValueError):
            delay = 0.0
        if delay > 0:
            time.sleep(delay)

    def js(self, script, *args):
        return self.driver.execute_script(script, *args)

    def dismiss_cookies(self):
        try:
            accept = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable(self.COOKIE_ACCEPT)
            )
            accept.click()
            time.sleep(0.3)
        except Exception:
            pass
        try:
            self.js("""
                ['cm','c-inr','c-inr-i'].forEach(function(id){
                    var el = document.getElementById(id);
                    if (el && el.parentNode) el.parentNode.removeChild(el);
                });
            """)
        except Exception:
            pass

    def safe_click_locator(self, locator):
        el = self.wait.until(EC.presence_of_element_located(locator))
        self.js("arguments[0].scrollIntoView({block:'center'});", el)
        self.slow(0.3)
        try:
            self.wait.until(EC.element_to_be_clickable(locator)).click()
        except Exception:
            self.js("arguments[0].click();", el)
        self.slow()

    def safe_click_element(self, element):
        try:
            self.js("arguments[0].scrollIntoView({block:'center'});", element)
            element.click()
        except Exception:
            self.js("arguments[0].click();", element)
        self.slow()

    def read_text(self, element):
        return self.js(
            "return (arguments[0].textContent || arguments[0].innerText || '').trim();",
            element,
        )

    # ══════════════════════════════════════════════════════
    #  Auth: login to dashboard
    # ══════════════════════════════════════════════════════
    def login(self):
        creds = self.config["credentials"]["valid"]
        if not creds.get("email") or "REPLACE" in creds["email"].upper():
            raise SkipTest("credentials.valid not configured")

        old_delay = self.config.get("step_delay", 0.6)
        self.config["step_delay"] = 0.05
        try:
            self.driver.get(self.config["base_url"])
            self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            self.dismiss_cookies()

            email_el = self.driver.find_element(By.ID, "email")
            pwd_el   = self.driver.find_element(By.ID, "password")
            email_el.clear(); email_el.send_keys(creds["email"])
            pwd_el.clear();   pwd_el.send_keys(creds["password"])

            self.dismiss_cookies()
            btn = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.login-submit")
            ))
            btn.click()

            WebDriverWait(self.driver, 25).until(
                lambda d: "/login" not in d.current_url.rstrip("/")
            )
        finally:
            self.config["step_delay"] = old_delay
        self.slow(0.3)

    # ══════════════════════════════════════════════════════
    #  Navigate to /users (login first if needed)
    # ══════════════════════════════════════════════════════
    def open_users(self):
        users_url = self.config.get("users_url", "").strip()
        if not users_url:
            raise SkipTest("users_url not configured in config.json")

        url = self.driver.current_url or ""
        not_logged_in = (
            not url
            or url.startswith("data:")
            or "about:blank" in url
            or "/login" in url
        )
        if not_logged_in:
            self.login()

        self.driver.get(users_url)
        self.dismiss_cookies()
        self.slow(0.5)

        # Bounced to login? Log in and retry once
        if "/login" in self.driver.current_url:
            self.login()
            self.driver.get(users_url)
            self.dismiss_cookies()
            self.slow(0.5)

        # Wait for the page to contain user cards or the add-user button
        self.wait.until(
            EC.presence_of_element_located(self.ADD_USER_BTN)
        )

    # ══════════════════════════════════════════════════════
    #  Open the "Add User" modal
    # ══════════════════════════════════════════════════════
    def open_add_user_modal(self):
        """Click the + Add User button and wait for the modal form."""
        self.safe_click_locator(self.ADD_USER_BTN)
        # Wait for the form to appear inside the modal
        self.wait.until(EC.presence_of_element_located(self.FORM))
        self.slow(0.5)

    # ══════════════════════════════════════════════════════
    #  Fill the create-user form
    # ══════════════════════════════════════════════════════
    def fill_create_form(self, name=None, email=None, password=None,
                         approval_code=None, role_value=None):
        """
        Fill the Add User form. Pass None to leave a field empty.
        role_value should be the <option value="..."> string (e.g. '40').
        """
        if name is not None:
            el = self.wait.until(EC.presence_of_element_located(self.FORM_NAME))
            el.clear(); el.send_keys(name); self.slow(0.2)

        if email is not None:
            el = self.driver.find_element(*self.FORM_EMAIL)
            el.clear(); el.send_keys(email); self.slow(0.2)

        if password is not None:
            el = self.driver.find_element(*self.FORM_PASSWORD)
            el.clear(); el.send_keys(password); self.slow(0.2)

        if approval_code is not None:
            el = self.driver.find_element(*self.FORM_APPROVAL)
            el.clear(); el.send_keys(approval_code); self.slow(0.2)

        if role_value is not None:
            from selenium.webdriver.support.ui import Select
            sel_el = self.driver.find_element(*self.FORM_ROLE)
            Select(sel_el).select_by_value(role_value)
            self.slow(0.2)

    def unique_email(self):
        domain = self.config.get("register_user", {}).get("email_domain", "example.com")
        return f"usr_{uuid.uuid4().hex[:8]}@{domain}"

    # ══════════════════════════════════════════════════════
    #  Error / success text helpers
    # ══════════════════════════════════════════════════════
    def visible_error_text(self):
        chunks = []
        for sel in ERROR_SELECTORS:
            try:
                for el in self.driver.find_elements(*sel):
                    try:
                        if el.is_displayed():
                            t = self.read_text(el)
                            if t:
                                chunks.append(t)
                    except Exception:
                        continue
            except Exception:
                continue
        return " | ".join(chunks)

    def visible_success_text(self):
        chunks = []
        for sel in SUCCESS_SELECTORS:
            try:
                for el in self.driver.find_elements(*sel):
                    try:
                        if el.is_displayed():
                            t = self.read_text(el)
                            if t:
                                chunks.append(t)
                    except Exception:
                        continue
            except Exception:
                continue
        return " | ".join(chunks)

    def wait_for_error(self, timeout=10):
        deadline = time.time() + timeout
        while time.time() < deadline:
            txt = self.visible_error_text()
            if txt:
                return txt
            if contains_any(self.driver.page_source, KEYWORDS["required_error"]):
                return "required error (page source)"
            time.sleep(0.35)
        return ""

    def wait_for_success(self, timeout=15):
        deadline = time.time() + timeout
        while time.time() < deadline:
            txt = self.visible_success_text()
            if txt and contains_any(txt, KEYWORDS["success"]):
                return txt
            if contains_any(self.driver.page_source, KEYWORDS["success"]):
                return "success (page source)"
            time.sleep(0.35)
        return ""


# ══════════════════════════════════════════════════════════════
#  USERS_001 — Page loads with heading and breadcrumb
# ══════════════════════════════════════════════════════════════
class Users001(UsersMixin, BaseTest):
    key = "USERS_001"
    name = "Users page loads with heading and breadcrumb"
    description = "Navigate to /users; heading and breadcrumb are visible."
    category = "Smoke"

    def execute(self):
        self.open_users()
        heading = self.driver.find_element(*self.PAGE_HEADING)
        assert heading.is_displayed(), "Page heading not visible"
        txt = self.read_text(heading)
        assert contains_any(txt, KEYWORDS["users_heading"]), \
            f"Unexpected heading: '{txt}'"
        breadcrumb = self.driver.find_element(*self.BREADCRUMB)
        assert breadcrumb.is_displayed(), "Breadcrumb not visible"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_002 — User cards are rendered
# ══════════════════════════════════════════════════════════════
class Users002(UsersMixin, BaseTest):
    key = "USERS_002"
    name = "User cards are rendered on the page"
    description = "At least one user card with a name and email is visible."
    category = "Smoke"

    def execute(self):
        self.open_users()
        cards = self.driver.find_elements(*self.USER_CARDS)
        assert len(cards) >= 1, "No user cards found on the page"
        names = self.driver.find_elements(*self.CARD_NAMES)
        assert len(names) >= 1, "No user name elements found inside cards"
        emails = self.driver.find_elements(*self.CARD_EMAILS)
        assert len(emails) >= 1, "No user email elements found inside cards"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_003 — Add User button is present
# ══════════════════════════════════════════════════════════════
class Users003(UsersMixin, BaseTest):
    key = "USERS_003"
    name = "Add User button is present on the page"
    description = "The + Add User button/link is visible and clickable."
    category = "Smoke"

    def execute(self):
        self.open_users()
        btn = self.driver.find_element(*self.ADD_USER_BTN)
        assert btn.is_displayed(), "Add User button not visible"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_004 — List View button is present
# ══════════════════════════════════════════════════════════════
class Users004(UsersMixin, BaseTest):
    key = "USERS_004"
    name = "List View button is present"
    description = "The list-view icon link exists and points to /user-list."
    category = "UI"

    def execute(self):
        self.open_users()
        btn = self.driver.find_element(*self.LIST_VIEW_BTN)
        assert btn.is_displayed(), "List View button not visible"
        href = btn.get_attribute("href") or ""
        assert "user-list" in href, f"Unexpected href: '{href}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_005 — User cards have avatars
# ══════════════════════════════════════════════════════════════
class Users005(UsersMixin, BaseTest):
    key = "USERS_005"
    name = "User cards display avatar images"
    description = "Each user card has an <img> with a valid src."
    category = "UI"

    def execute(self):
        self.open_users()
        avatars = self.driver.find_elements(*self.CARD_AVATARS)
        assert len(avatars) >= 1, "No avatar images found"
        for img in avatars:
            src = img.get_attribute("src") or ""
            assert src.startswith("http") or src.startswith("data:image"), \
                f"Invalid avatar src: '{src}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_006 — User cards show role badges
# ══════════════════════════════════════════════════════════════
class Users006(UsersMixin, BaseTest):
    key = "USERS_006"
    name = "User cards display role badges"
    description = "Each user card has a visible role/badge label."
    category = "UI"

    def execute(self):
        self.open_users()
        badges = self.driver.find_elements(*self.CARD_BADGES)
        assert len(badges) >= 1, "No role badges found on user cards"
        for badge in badges:
            txt = self.read_text(badge)
            assert txt.strip(), "Empty badge text found"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_007 — Add User modal opens
# ══════════════════════════════════════════════════════════════
class Users007(UsersMixin, BaseTest):
    key = "USERS_007"
    name = "Clicking Add User opens the modal form"
    description = "After clicking +, the create-user form is displayed."
    category = "Functional"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()
        form = self.driver.find_element(*self.FORM)
        assert form.is_displayed(), "Create-user form not visible after clicking Add User"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_008 — Form has all required fields
# ══════════════════════════════════════════════════════════════
class Users008(UsersMixin, BaseTest):
    key = "USERS_008"
    name = "Create user form has all required fields"
    description = "Name, Email, Password, Approval Code, Role select all present."
    category = "Functional"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()
        for locator in (self.FORM_NAME, self.FORM_EMAIL, self.FORM_PASSWORD,
                        self.FORM_APPROVAL, self.FORM_ROLE):
            el = self.driver.find_element(*locator)
            assert el.is_displayed(), f"{locator} not visible in the form"
            self.slow(0.1)
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_009 — Form has CSRF token
# ══════════════════════════════════════════════════════════════
class Users009(UsersMixin, BaseTest):
    key = "USERS_009"
    name = "Create user form has CSRF token"
    description = "Hidden _token input exists with a value longer than 20 chars."
    category = "Security"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()
        token_el = self.driver.find_element(*self.FORM_TOKEN)
        token = token_el.get_attribute("value") or ""
        assert token and len(token) > 20, f"CSRF token missing or too short: '{token}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_010 — Form has Create and Cancel buttons
# ══════════════════════════════════════════════════════════════
class Users010(UsersMixin, BaseTest):
    key = "USERS_010"
    name = "Form has Create and Cancel buttons"
    description = "Both Submit (Create) and Cancel buttons are visible."
    category = "UI"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()
        submit = self.driver.find_element(*self.FORM_SUBMIT)
        cancel = self.driver.find_element(*self.FORM_CANCEL)
        assert submit.is_displayed(), "Create button not visible"
        assert cancel.is_displayed(), "Cancel button not visible"
        assert contains_any(
            submit.get_attribute("value") or "", KEYWORDS["create_btn"]
        ), f"Unexpected submit label: '{submit.get_attribute('value')}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_011 — Role select has options
# ══════════════════════════════════════════════════════════════
class Users011(UsersMixin, BaseTest):
    key = "USERS_011"
    name = "Role select dropdown has selectable options"
    description = "Role <select> has at least 2 options (placeholder + one real role)."
    category = "Functional"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()
        from selenium.webdriver.support.ui import Select
        sel = Select(self.driver.find_element(*self.FORM_ROLE))
        options = sel.options
        assert len(options) >= 2, f"Expected ≥2 options, got {len(options)}"
        # First option should be the placeholder "Select Role"
        first = options[0].text.strip()
        assert first, "First option is empty"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_012 — Empty form submission shows required errors
# ══════════════════════════════════════════════════════════════
class Users012(UsersMixin, BaseTest):
    key = "USERS_012"
    name = "Submitting empty form shows required field errors"
    description = "Click Create with blank fields → required-field errors appear."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        # Check HTML5 validity of required fields (name, email, role)
        name_el  = self.driver.find_element(*self.FORM_NAME)
        email_el = self.driver.find_element(*self.FORM_EMAIL)
        role_el  = self.driver.find_element(*self.FORM_ROLE)

        name_valid  = self.js("return arguments[0].checkValidity();", name_el)
        email_valid = self.js("return arguments[0].checkValidity();", email_el)
        role_valid  = self.js("return arguments[0].checkValidity();", role_el)

        assert name_valid is False,  "Empty name field considered valid"
        assert email_valid is False, "Empty email field considered valid"
        assert role_valid is False,  "Empty role field considered valid"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_013 — Invalid email format blocked by HTML5
# ══════════════════════════════════════════════════════════════
class Users013(UsersMixin, BaseTest):
    key = "USERS_013"
    name = "Invalid email format is blocked by HTML5 validation"
    description = "Enter 'abc' in email → checkValidity false, message contains '@'."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        email_el = self.driver.find_element(*self.FORM_EMAIL)
        email_el.clear(); email_el.send_keys("abc"); self.slow(0.2)

        valid = self.js("return arguments[0].checkValidity();", email_el)
        msg   = self.js("return arguments[0].validationMessage;", email_el)

        assert valid is False, "Invalid email 'abc' passed HTML5 validation"
        assert "@" in msg, f"Expected '@' in validation message, got: '{msg}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_014 — Approval code accepts only 5 digits
# ══════════════════════════════════════════════════════════════
class Users014(UsersMixin, BaseTest):
    key = "USERS_014"
    name = "Approval code field enforces 5-digit pattern"
    description = "maxlength=5, pattern=[0-9]{5}, inputmode=numeric are set."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        el = self.driver.find_element(*self.FORM_APPROVAL)
        assert el.get_attribute("maxlength") == "5", \
            f"maxlength not 5: '{el.get_attribute('maxlength')}'"
        pattern = el.get_attribute("pattern") or ""
        assert "9" in pattern and "5" in pattern, \
            f"Unexpected pattern: '{pattern}'"
        inputmode = el.get_attribute("inputmode") or ""
        assert inputmode == "numeric", \
            f"inputmode not numeric: '{inputmode}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_015 — Submitting without password shows server error
# ══════════════════════════════════════════════════════════════
class Users015(UsersMixin, BaseTest):
    key = "USERS_015"
    name = "Submitting without password shows 'password required' error"
    description = "Fill name, email, role but leave password blank → server error."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        self.fill_create_form(
            name="TestUser",
            email=self.unique_email(),
            password=None,       # intentionally blank
            role_value=None,
        )

        # Select a role manually to avoid role-required stopping us first
        from selenium.webdriver.support.ui import Select
        role_el = self.driver.find_element(*self.FORM_ROLE)
        options = Select(role_el).options
        # Pick the first non-placeholder option
        for opt in options:
            if opt.get_attribute("value"):
                Select(role_el).select_by_value(opt.get_attribute("value"))
                break
        self.slow(0.2)

        url_before = self.driver.current_url
        self.safe_click_locator(self.FORM_SUBMIT)

        # Wait for error or navigation
        deadline = time.time() + 15
        outcome = "timeout"
        while time.time() < deadline:
            if self.driver.current_url != url_before:
                outcome = "navigated"
                break
            err = self.visible_error_text()
            if err:
                outcome = "error"
                break
            if contains_any(self.driver.page_source, KEYWORDS["password_required"]):
                outcome = "error"
                break
            time.sleep(0.4)

        combined = (self.visible_error_text() + " " + self.driver.page_source).lower()
        assert outcome != "navigated" or contains_any(combined, KEYWORDS["success"]) is False, \
            "Form accepted blank password and navigated away"
        assert contains_any(combined, KEYWORDS["password_required"]) or outcome == "error", \
            f"Expected password-required error. outcome={outcome}, snippet={combined[:300]}"
        self.slow(0.5)


# ══════════════════════════════════════════════════════════════
#  USERS_016 — Name field accepts input
# ══════════════════════════════════════════════════════════════
class Users016(UsersMixin, BaseTest):
    key = "USERS_016"
    name = "Name field accepts typed input"
    description = "Type a name in the form and verify the DOM value."
    category = "Functional"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        el = self.wait.until(EC.presence_of_element_located(self.FORM_NAME))
        el.clear(); el.send_keys("John Doe"); self.slow(0.2)
        val = el.get_attribute("value") or ""
        assert val == "John Doe", f"Expected 'John Doe', got '{val}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_017 — Email field accepts input
# ══════════════════════════════════════════════════════════════
class Users017(UsersMixin, BaseTest):
    key = "USERS_017"
    name = "Email field accepts typed input"
    description = "Type a valid email and verify the DOM value."
    category = "Functional"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        test_email = "test@example.com"
        el = self.driver.find_element(*self.FORM_EMAIL)
        el.clear(); el.send_keys(test_email); self.slow(0.2)
        val = el.get_attribute("value") or ""
        assert val == test_email, f"Expected '{test_email}', got '{val}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_018 — Password field type is password
# ══════════════════════════════════════════════════════════════
class Users018(UsersMixin, BaseTest):
    key = "USERS_018"
    name = "Password field type is 'password' (input masked)"
    description = "The password input has type='password' for security."
    category = "Security"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        el = self.driver.find_element(*self.FORM_PASSWORD)
        input_type = el.get_attribute("type") or ""
        assert input_type == "password", \
            f"Expected type='password', got '{input_type}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_019 — User cards have Edit and Delete actions in dropdown
# ══════════════════════════════════════════════════════════════
class Users019(UsersMixin, BaseTest):
    key = "USERS_019"
    name = "User cards have Edit and Delete actions in dropdown"
    description = "Open first card's dropdown; Edit and Delete options are visible."
    category = "Functional"

    def execute(self):
        self.open_users()

        # Open the first card's dropdown toggle
        toggles = self.driver.find_elements(*self.DROPDOWN_TOGGLE)
        assert len(toggles) >= 1, "No dropdown toggles found on user cards"

        self.safe_click_element(toggles[0])
        self.slow(0.5)

        edit_items   = self.driver.find_elements(*self.EDIT_ACTION)
        delete_items = self.driver.find_elements(*self.DELETE_ACTION)

        assert len(edit_items) >= 1,   "Edit action not found in dropdown"
        assert len(delete_items) >= 1, "Delete action not found in dropdown"

        # Verify edit link points to /users/{id}/edit
        edit_url = edit_items[0].get_attribute("data-url") or ""
        assert "/users/" in edit_url and "/edit" in edit_url, \
            f"Unexpected edit data-url: '{edit_url}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_020 — /users redirects to login when unauthenticated
# ══════════════════════════════════════════════════════════════
class Users020(UsersMixin, BaseTest):
    key = "USERS_020"
    name = "/users page requires authentication"
    description = "Open /users without login → redirected to /login."
    category = "Auth"

    def execute(self):
        users_url = self.config.get("users_url", "").strip()
        if not users_url:
            raise SkipTest("users_url not configured in config.json")

        # Navigate directly without logging in first
        self.driver.get(users_url)
        self.slow(1.0)

        current = self.driver.current_url
        assert "/login" in current, \
            f"Expected redirect to /login, but landed on: '{current}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_021 — Create user with valid full data (E2E)
# ══════════════════════════════════════════════════════════════
class Users021(UsersMixin, BaseTest):
    key = "USERS_021"
    name = "Create user with valid full data succeeds"
    description = "Fill all fields correctly and submit → success, new user appears."
    category = "E2E"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        test_email = self.unique_email()
        self.fill_create_form(
            name="AutoTest User",
            email=test_email,
            password="Test@1234",
            approval_code="12345",
            role_value=self._first_role_value(),
        )

        url_before = self.driver.current_url
        self.safe_click_locator(self.FORM_SUBMIT)

        # Wait for success banner or page refresh with new user card
        msg = self.wait_for_success(timeout=15)
        self.slow(0.8)

        # Also accept: modal closed and URL didn't navigate to an error page
        modal_gone = self._modal_closed(timeout=8)

        assert msg or modal_gone, (
            f"No success signal after creating user. "
            f"URL: {self.driver.current_url}, "
            f"errors: '{self.visible_error_text()}'"
        )

    # ── helpers used by create tests ──────────────────────
    def _first_role_value(self):
        """Return the value of the first non-placeholder <option> in role select."""
        from selenium.webdriver.support.ui import Select
        sel = Select(self.driver.find_element(*self.FORM_ROLE))
        for opt in sel.options:
            val = opt.get_attribute("value")
            if val:
                return val
        raise SkipTest("No selectable role options found")

    def _modal_closed(self, timeout=8):
        """Return True if the create-user modal/form disappears within timeout."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                form = self.driver.find_element(*self.FORM)
                if not form.is_displayed():
                    return True
            except Exception:
                return True          # element gone from DOM = modal closed
            time.sleep(0.4)
        return False


# ══════════════════════════════════════════════════════════════
#  USERS_022 — Duplicate email is rejected
# ══════════════════════════════════════════════════════════════
class Users022(UsersMixin, BaseTest):
    key = "USERS_022"
    name = "Creating user with already-used email is rejected"
    description = "Submit form with an existing email → server error, no new user."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        # Use the known valid credential email which already exists
        existing_email = self.config["credentials"]["valid"]["email"]

        self.fill_create_form(
            name="Duplicate User",
            email=existing_email,
            password="Test@1234",
            approval_code="12345",
            role_value=self._pick_role(),
        )

        url_before = self.driver.current_url
        self.safe_click_locator(self.FORM_SUBMIT)

        deadline = time.time() + 15
        outcome = "timeout"
        while time.time() < deadline:
            err = self.visible_error_text()
            if err:
                outcome = "error"
                break
            if contains_any(self.driver.page_source,
                            ["already been taken", "already exists",
                             "البريد مستخدم", "مستخدم بالفعل", "unique"]):
                outcome = "error"
                break
            if self.driver.current_url != url_before:
                outcome = "navigated"
                break
            time.sleep(0.4)

        combined = (self.visible_error_text() + " " + self.driver.page_source).lower()
        assert outcome == "error" or contains_any(
            combined, ["taken", "exists", "unique", "مستخدم", "موجود"]
        ), (
            f"Server accepted duplicate email '{existing_email}'. "
            f"outcome={outcome}, snippet={combined[:300]}"
        )

    def _pick_role(self):
        from selenium.webdriver.support.ui import Select
        sel = Select(self.driver.find_element(*self.FORM_ROLE))
        for opt in sel.options:
            val = opt.get_attribute("value")
            if val:
                return val
        return None


# ══════════════════════════════════════════════════════════════
#  USERS_023 — Name field is required (HTML5)
# ══════════════════════════════════════════════════════════════
class Users023(UsersMixin, BaseTest):
    key = "USERS_023"
    name = "Name field is required — HTML5 blocks empty submit"
    description = "Leave name blank, fill rest → checkValidity false on name."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        # Fill everything except name
        email_el = self.driver.find_element(*self.FORM_EMAIL)
        email_el.clear(); email_el.send_keys(self.unique_email()); self.slow(0.2)

        pwd_el = self.driver.find_element(*self.FORM_PASSWORD)
        pwd_el.clear(); pwd_el.send_keys("Test@1234"); self.slow(0.2)

        name_el = self.driver.find_element(*self.FORM_NAME)
        # Ensure name is empty
        name_el.clear()
        self.slow(0.2)

        valid = self.js("return arguments[0].checkValidity();", name_el)
        assert valid is False, "Empty name field considered valid by HTML5"

        vm = self.js("return arguments[0].validationMessage;", name_el)
        assert vm, f"No HTML5 validation message on empty name field"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_024 — Email field is required (HTML5)
# ══════════════════════════════════════════════════════════════
class Users024(UsersMixin, BaseTest):
    key = "USERS_024"
    name = "Email field is required — HTML5 blocks empty submit"
    description = "Leave email blank, fill rest → checkValidity false on email."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        name_el = self.driver.find_element(*self.FORM_NAME)
        name_el.clear(); name_el.send_keys("Test Name"); self.slow(0.2)

        email_el = self.driver.find_element(*self.FORM_EMAIL)
        email_el.clear()
        self.slow(0.2)

        valid = self.js("return arguments[0].checkValidity();", email_el)
        assert valid is False, "Empty email field considered valid by HTML5"

        vm = self.js("return arguments[0].validationMessage;", email_el)
        assert vm, "No HTML5 validation message on empty email field"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_025 — Role field is required (HTML5)
# ══════════════════════════════════════════════════════════════
class Users025(UsersMixin, BaseTest):
    key = "USERS_025"
    name = "Role field is required — HTML5 blocks placeholder selection"
    description = "Leave role at placeholder → checkValidity false on role select."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        role_el = self.driver.find_element(*self.FORM_ROLE)
        # Make sure value is empty (placeholder selected)
        val = role_el.get_attribute("value") or ""
        assert val == "", f"Role unexpectedly pre-selected with value: '{val}'"

        valid = self.js("return arguments[0].checkValidity();", role_el)
        assert valid is False, "Empty role select considered valid by HTML5"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_026 — Invalid email format rejected by HTML5
# ══════════════════════════════════════════════════════════════
class Users026(UsersMixin, BaseTest):
    key = "USERS_026"
    name = "Invalid email format in create form rejected by HTML5"
    description = "Enter 'notanemail' → HTML5 invalid, message mentions '@'."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        email_el = self.driver.find_element(*self.FORM_EMAIL)
        email_el.clear(); email_el.send_keys("notanemail"); self.slow(0.2)

        valid = self.js("return arguments[0].checkValidity();", email_el)
        msg   = self.js("return arguments[0].validationMessage;", email_el)

        assert valid is False, "Invalid email 'notanemail' passed HTML5 validation"
        assert "@" in msg, f"Expected '@' in validation message, got: '{msg}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_027 — Approval code max-length enforced in DOM
# ══════════════════════════════════════════════════════════════
class Users027(UsersMixin, BaseTest):
    key = "USERS_027"
    name = "Approval code field truncates input beyond 5 digits"
    description = "Type 8 digits → field value is capped at 5 characters."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        el = self.driver.find_element(*self.FORM_APPROVAL)
        el.clear(); el.send_keys("12345678"); self.slow(0.2)

        val = el.get_attribute("value") or ""
        assert len(val) <= 5, \
            f"Expected max 5 chars, but got {len(val)} chars: '{val}'"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_028 — Approval code rejects non-numeric input
# ══════════════════════════════════════════════════════════════
class Users028(UsersMixin, BaseTest):
    key = "USERS_028"
    name = "Approval code field pattern rejects non-numeric input"
    description = "Enter 'abcde' → HTML5 pattern check returns invalid."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        el = self.driver.find_element(*self.FORM_APPROVAL)
        el.clear(); el.send_keys("abcde"); self.slow(0.2)

        valid = self.js("return arguments[0].checkValidity();", el)
        # The field has pattern="[0-9]{5}", so letters must be invalid
        # Some browsers silently drop non-numeric input due to inputmode — accept either
        val = el.get_attribute("value") or ""
        letters_blocked = (val == "" or not any(c.isalpha() for c in val))

        assert valid is False or letters_blocked, (
            f"Non-numeric input 'abcde' was accepted. "
            f"checkValidity={valid}, actual value='{val}'"
        )
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_029 — Cancel button closes the modal
# ══════════════════════════════════════════════════════════════
class Users029(UsersMixin, BaseTest):
    key = "USERS_029"
    name = "Cancel button closes the Add User modal"
    description = "Open modal, fill name, click Cancel → form disappears."
    category = "Functional"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        # Type something so we know the form was open and interactive
        name_el = self.wait.until(EC.presence_of_element_located(self.FORM_NAME))
        name_el.send_keys("ShouldNotBeSaved"); self.slow(0.2)

        # Click Cancel
        self.safe_click_locator(self.FORM_CANCEL)
        self.slow(0.8)

        # Form should be gone or hidden
        closed = False
        try:
            form = self.driver.find_element(*self.FORM)
            closed = not form.is_displayed()
        except Exception:
            closed = True   # element removed from DOM

        assert closed, "Modal/form still visible after clicking Cancel"
        self.slow()


# ══════════════════════════════════════════════════════════════
#  USERS_030 — Missing password server-side error message
# ══════════════════════════════════════════════════════════════
class Users030(UsersMixin, BaseTest):
    key = "USERS_030"
    name = "Server returns 'password required' error when password is blank"
    description = "Fill name+email+role, leave password blank → server-side error."
    category = "Validation"

    def execute(self):
        self.open_users()
        self.open_add_user_modal()

        # Pick first available role
        from selenium.webdriver.support.ui import Select
        role_el = self.driver.find_element(*self.FORM_ROLE)
        first_role = None
        for opt in Select(role_el).options:
            if opt.get_attribute("value"):
                first_role = opt.get_attribute("value")
                break
        if not first_role:
            raise SkipTest("No selectable role options available")

        self.fill_create_form(
            name="NoPasswordUser",
            email=self.unique_email(),
            password=None,          # intentionally blank
            role_value=first_role,
        )

        url_before = self.driver.current_url
        self.safe_click_locator(self.FORM_SUBMIT)

        # Poll for outcome
        deadline = time.time() + 15
        outcome = "timeout"
        while time.time() < deadline:
            if self.driver.current_url != url_before:
                outcome = "navigated"
                break
            err = self.visible_error_text()
            if err:
                outcome = "error"
                break
            src = self.driver.page_source.lower()
            if contains_any(src, KEYWORDS["password_required"]):
                outcome = "error_in_source"
                break
            time.sleep(0.4)

        combined = (self.visible_error_text() + " " + self.driver.page_source).lower()

        assert outcome != "navigated", \
            "Server accepted blank password and navigated away"
        assert contains_any(combined, KEYWORDS["password_required"]) or outcome in ("error", "error_in_source"), \
            (
                f"Expected 'password required' error. "
                f"outcome={outcome}, visible_error='{self.visible_error_text()}', "
                f"snippet={combined[:300]}"
            )
        self.slow(0.5)
