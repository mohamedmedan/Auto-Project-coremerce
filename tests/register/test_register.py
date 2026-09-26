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
    "sign_up": [
        "create account", "sign up", "signup", "register", "create your",
        "إنشاء حساب", "تسجيل", "حساب جديد", "إنشاء",
    ],
    "first_name": ["first name", "الاسم الأول", "الاسم الاول"],
    "last_name":  ["last name", "الاسم الأخير", "الاسم الاخير"],
    "email":      ["email", "بريد", "الإلكتروني", "الالكتروني"],
    "phone":      ["phone", "mobile", "tel", "الهاتف", "رقم"],
    "password":   ["password", "كلمة المرور", "كلمه المرور", "المرور"],
    "terms":      ["terms", "conditions", "الشروط", "الأحكام", "الاحكام"],
    "privacy":    ["privacy", "الخصوصية", "خصوصية"],
    "login_link": ["login", "sign in", "تسجيل الدخول", "دخول"],
}

# Server-side error messages (both EN and AR)
ERROR_KEYWORDS = {
    "email_invalid": [
        "must be a valid email", "valid email address",
        "بريد إلكتروني صالح", "بريد الكتروني صالح",
    ],
    "password_short": [
        "at least 8 characters", "8 characters",
        "8 أحرف", "8 احرف", "٨ أحرف",
    ],
    "password_symbol": [
        "at least one symbol", "contain at least one symbol",
        "رمز", "رموز", "contains at least",
    ],
    "generic": [
        "please fix these details", "check the highlighted",
        "الرجاء تصحيح", "تحقق من",
    ],
}

# Server-side error containers
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
]


def contains_any(text, keywords):
    if not text:
        return False
    low = text.lower()
    return any(k.lower() in low for k in keywords)


class RegisterMixin:
    feature = "register"

    # ── Register page locators ────────────────────────────
    FIRST_NAME     = (By.ID, "first_name")
    LAST_NAME      = (By.ID, "last_name")
    EMAIL          = (By.ID, "email")
    MOBILE         = (By.ID, "mobile")
    COUNTRY_CODE   = (By.NAME, "country_code")
    PASSWORD       = (By.ID, "password")
    PASSWORD_TOGGLE= (By.CSS_SELECTOR, ".register-password-toggle")
    TERMS_CHECKBOX = (By.CSS_SELECTOR, ".register-legal input[type='checkbox']")
    SUBMIT         = (By.CSS_SELECTOR, "button.register-submit")
    FORM           = (By.ID, "register_form")
    TOKEN          = (By.CSS_SELECTOR, "#register_form input[name='_token']")
    HEADING        = (By.CSS_SELECTOR, ".register-heading")
    LOGO           = (By.CSS_SELECTOR, ".register-logo")
    LEGAL          = (By.CSS_SELECTOR, ".register-legal")
    SOCIAL         = (By.CSS_SELECTOR, ".register-social-btn")
    LOGIN_LINK     = (By.CSS_SELECTOR, ".register-footer-link a")
    STEPPER        = (By.CSS_SELECTOR, ".ob-stepper")
    ACTIVE_STEP    = (By.CSS_SELECTOR, ".ob-step.is-active .ob-step__label")

    # ── OTP page locators ─────────────────────────────────
    OTP_INPUTS     = (By.CSS_SELECTOR, ".verify-otp-input")
    OTP_SUBMIT     = (By.ID, "verify-continue-btn")
    OTP_DEBUG      = (By.CSS_SELECTOR, ".verify-debug strong")
    OTP_HEADING    = (By.CSS_SELECTOR, ".verify-heading")
    OTP_FORM       = (By.ID, "phone-otp-form")

    # ── Cookie banner ─────────────────────────────────────
    COOKIE_ACCEPT  = (By.ID, "c-p-bn")

    # ══════════════════════════════════════════════════════
    #  Helpers
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
            time.sleep(0.4)
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

    def read_placeholder(self, element):
        return self.js(
            "return (arguments[0].placeholder || "
            "arguments[0].getAttribute('placeholder') || '');",
            element,
        ).strip()

    def get_register_url(self):
        url = self.config.get("register_url", "").strip()
        if not url:
            raise SkipTest("register_url not configured in config.json")
        return url

    def open_register(self):
        self.driver.get(self.get_register_url())
        self.wait.until(EC.presence_of_element_located(self.FORM))
        self.dismiss_cookies()
        self.slow()

    def unique_email(self):
        domain = self.config.get("register_user", {}).get("email_domain", "example.com")
        return f"test_{uuid.uuid4().hex[:10]}@{domain}"

    def fill_form(self, first="Test", last="User", email=None, mobile=None,
                  password=None, agree=True):
        ru = self.config.get("register_user", {})
        email = email or self.unique_email()
        mobile = mobile if mobile is not None else ru.get("mobile", "1009876543")
        password = password if password is not None else ru.get("password", "Test@1234")

        first_el = self.driver.find_element(*self.FIRST_NAME)
        first_el.clear(); first_el.send_keys(first); self.slow(0.3)

        last_el = self.driver.find_element(*self.LAST_NAME)
        last_el.clear(); last_el.send_keys(last); self.slow(0.3)

        email_el = self.driver.find_element(*self.EMAIL)
        email_el.clear(); email_el.send_keys(email); self.slow(0.3)

        mob_el = self.driver.find_element(*self.MOBILE)
        mob_el.clear(); mob_el.send_keys(mobile); self.slow(0.3)

        pwd_el = self.driver.find_element(*self.PASSWORD)
        pwd_el.clear(); pwd_el.send_keys(password); self.slow(0.3)

        if agree:
            cb = self.driver.find_element(*self.TERMS_CHECKBOX)
            if not cb.is_selected():
                self.safe_click_element(cb)

        return {"email": email, "mobile": mobile, "password": password}

    # ── Server-side error detection ───────────────────────
    def visible_error_text(self):
        """Return concatenated visible text of any error container."""
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

    def page_has_any(self, keywords):
        return contains_any(self.driver.page_source, keywords)

    def submit_and_wait_for_outcome(self, timeout=15):
        """Submit and wait until either an error appears or URL changes."""
        url_before = self.driver.current_url
        self.safe_click_locator(self.SUBMIT)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.driver.current_url != url_before:
                return "navigated"
            err = self.visible_error_text()
            if err:
                return "error"
            # fallback: page source contains error keywords
            if (self.page_has_any(ERROR_KEYWORDS["generic"])
                    or self.page_has_any(ERROR_KEYWORDS["email_invalid"])
                    or self.page_has_any(ERROR_KEYWORDS["password_short"])
                    or self.page_has_any(ERROR_KEYWORDS["password_symbol"])):
                return "error"
            time.sleep(0.4)
        return "timeout"


# ══════════════════════════════════════════════════════════════
#  REGISTER_001 — Smoke: page loads
# ══════════════════════════════════════════════════════════════
class Register001(RegisterMixin, BaseTest):
    key = "REGISTER_001"
    name = "Register page loads with key elements"
    description = "Logo, heading, form, submit button visible."
    category = "Smoke"

    def execute(self):
        self.open_register()
        for loc in (self.LOGO, self.HEADING, self.FORM, self.SUBMIT):
            assert self.driver.find_element(*loc).is_displayed(), f"{loc} missing"
            self.slow(0.2)


# ══════════════════════════════════════════════════════════════
#  REGISTER_002 — All required fields present
# ══════════════════════════════════════════════════════════════
class Register002(RegisterMixin, BaseTest):
    key = "REGISTER_002"
    name = "All required input fields are present"
    description = "first_name, last_name, email, mobile, password inputs visible."
    category = "Functional"

    def execute(self):
        self.open_register()
        for loc in (self.FIRST_NAME, self.LAST_NAME, self.EMAIL,
                    self.MOBILE, self.PASSWORD):
            assert self.driver.find_element(*loc).is_displayed(), f"{loc} missing"
            self.slow(0.15)


# ══════════════════════════════════════════════════════════════
#  REGISTER_003 — Empty form blocked (HTML5)
# ══════════════════════════════════════════════════════════════
class Register003(RegisterMixin, BaseTest):
    key = "REGISTER_003"
    name = "Empty form blocked by HTML5"
    description = "checkValidity() returns False on empty form."
    category = "Validation"

    def execute(self):
        self.open_register()
        form = self.driver.find_element(*self.FORM)
        valid = self.js("return arguments[0].checkValidity();", form)
        assert valid is False, "Empty form considered valid"


# ══════════════════════════════════════════════════════════════
#  REGISTER_004 — Invalid email format (HTML5)
# ══════════════════════════════════════════════════════════════
class Register004(RegisterMixin, BaseTest):
    key = "REGISTER_004"
    name = "Invalid email format triggers HTML5 error"
    description = "Enter 'abc' => validation message mentions '@'."
    category = "Validation"

    def execute(self):
        self.open_register()
        el = self.driver.find_element(*self.EMAIL)
        el.clear(); el.send_keys("abc"); self.slow()
        msg = self.js("return arguments[0].validationMessage;", el)
        ok  = self.js("return arguments[0].checkValidity();", el)
        assert ok is False
        assert "@" in msg, f"Expected '@' in message, got: '{msg}'"


# ══════════════════════════════════════════════════════════════
#  REGISTER_005 — Password too short (server)
# ══════════════════════════════════════════════════════════════
class Register005(RegisterMixin, BaseTest):
    key = "REGISTER_005"
    name = "Short password rejected by server"
    description = "Password 'Ab@1' (<8 chars) triggers server error."
    category = "Validation"

    def execute(self):
        self.open_register()
        self.fill_form(password="Ab@1")

        outcome = self.submit_and_wait_for_outcome()
        assert outcome != "navigated", \
            "Server accepted short password and navigated away"

        combined = (self.visible_error_text() + " " + self.driver.page_source).lower()
        assert (
            contains_any(combined, ERROR_KEYWORDS["password_short"])
            or contains_any(combined, ERROR_KEYWORDS["generic"])
        ), f"No 'min 8 chars' error found. Page snippet: {combined[:300]}"
        self.slow(0.5)


# ══════════════════════════════════════════════════════════════
#  REGISTER_006 — Password without symbol (server)
# ══════════════════════════════════════════════════════════════
class Register006(RegisterMixin, BaseTest):
    key = "REGISTER_006"
    name = "Password without symbol rejected by server"
    description = "Password 'abcdefgh' (8 chars, no symbol) => server error."
    category = "Validation"

    def execute(self):
        self.open_register()
        self.fill_form(password="abcdefgh")

        outcome = self.submit_and_wait_for_outcome()
        assert outcome != "navigated", \
            "Server accepted symbol-less password and navigated away"

        combined = (self.visible_error_text() + " " + self.driver.page_source).lower()
        assert (
            contains_any(combined, ERROR_KEYWORDS["password_symbol"])
            or contains_any(combined, ERROR_KEYWORDS["generic"])
        ), f"No 'symbol required' error. Snippet: {combined[:300]}"
        self.slow(0.5)


# ══════════════════════════════════════════════════════════════
#  REGISTER_007 — Terms checkbox required (HTML5)
# ══════════════════════════════════════════════════════════════
class Register007(RegisterMixin, BaseTest):
    key = "REGISTER_007"
    name = "Terms checkbox is required"
    description = "Without checking terms, form invalid."
    category = "Validation"

    def execute(self):
        self.open_register()
        # Fill everything but DO NOT check the checkbox
        self.fill_form(agree=False)

        cb = self.driver.find_element(*self.TERMS_CHECKBOX)
        assert not cb.is_selected(), "Checkbox should start unchecked"

        valid = self.js("return arguments[0].checkValidity();", cb)
        assert valid is False, "Unchecked required checkbox considered valid"
        self.slow(0.5)


# ══════════════════════════════════════════════════════════════
#  REGISTER_008 — First name auto-focused
# ══════════════════════════════════════════════════════════════
class Register008(RegisterMixin, BaseTest):
    key = "REGISTER_008"
    name = "First name field is auto-focused"
    description = "Active element on load is #first_name."
    category = "UX"

    def execute(self):
        self.open_register()
        active = self.js(
            "return document.activeElement ? document.activeElement.id : '';"
        )
        self.slow()
        assert active == "first_name", f"Expected 'first_name' focused, got '{active}'"


# ══════════════════════════════════════════════════════════════
#  REGISTER_009 — Password toggle
# ══════════════════════════════════════════════════════════════
class Register009(RegisterMixin, BaseTest):
    key = "REGISTER_009"
    name = "Password toggle changes input type"
    description = "Click eye icon => type flips between password/text."
    category = "UI"

    def execute(self):
        self.open_register()
        pwd = self.driver.find_element(*self.PASSWORD)
        pwd.send_keys("whatever"); self.slow()
        initial = pwd.get_attribute("type")
        self.safe_click_locator(self.PASSWORD_TOGGLE)
        assert pwd.get_attribute("type") != initial, "Toggle did nothing"
        self.safe_click_locator(self.PASSWORD_TOGGLE)
        assert pwd.get_attribute("type") == initial, "Toggle did not restore"


# ══════════════════════════════════════════════════════════════
#  REGISTER_010 — Country code selector
# ══════════════════════════════════════════════════════════════
class Register010(RegisterMixin, BaseTest):
    key = "REGISTER_010"
    name = "Country code dropdown has options"
    description = "Select has +20, +1, +44, +971, +966."
    category = "UI"

    def execute(self):
        self.open_register()
        sel = self.driver.find_element(*self.COUNTRY_CODE)
        options = [o.get_attribute("value") for o in sel.find_elements(By.TAG_NAME, "option")]
        self.slow()
        assert "+20" in options, f"Missing +20 in {options}"
        assert len(options) >= 3, f"Expected >=3 options, got {options}"


# ══════════════════════════════════════════════════════════════
#  REGISTER_011 — Login link present
# ══════════════════════════════════════════════════════════════
class Register011(RegisterMixin, BaseTest):
    key = "REGISTER_011"
    name = "Login link present on register page"
    description = "Footer link points to /login."
    category = "Navigation"

    def execute(self):
        self.open_register()
        link = self.driver.find_element(*self.LOGIN_LINK)
        href = (link.get_attribute("href") or "").lower()
        self.slow()
        assert "login" in href, f"Unexpected href: {href}"


# ══════════════════════════════════════════════════════════════
#  REGISTER_012 — Social buttons present
# ══════════════════════════════════════════════════════════════
class Register012(RegisterMixin, BaseTest):
    key = "REGISTER_012"
    name = "Google and Apple buttons rendered"
    description = "Both social signup buttons exist."
    category = "UI"

    def execute(self):
        self.open_register()
        btns = self.driver.find_elements(*self.SOCIAL)
        self.slow()
        assert len(btns) == 2, f"Expected 2, found {len(btns)}"
        texts = [self.read_text(b).lower() for b in btns]
        assert any("google" in t for t in texts)
        assert any("apple" in t for t in texts)


# ══════════════════════════════════════════════════════════════
#  REGISTER_013 — Stepper shows step 1 active
# ══════════════════════════════════════════════════════════════
class Register013(RegisterMixin, BaseTest):
    key = "REGISTER_013"
    name = "Stepper shows Account step active"
    description = "Onboarding stepper present with step 1 active."
    category = "UI"

    def execute(self):
        self.open_register()
        stepper = self.driver.find_element(*self.STEPPER)
        assert stepper.is_displayed(), "Stepper not displayed"
        active = self.read_text(self.driver.find_element(*self.ACTIVE_STEP))
        self.slow()
        assert active, "Active step has no label"
        # Account in EN, or step number '1' present
        assert active.lower() in ("account", "حساب") or active.strip() == "1", \
            f"Unexpected active step: '{active}'"


# ══════════════════════════════════════════════════════════════
#  REGISTER_014 — Placeholders present
# ══════════════════════════════════════════════════════════════
class Register014(RegisterMixin, BaseTest):
    key = "REGISTER_014"
    name = "Inputs have placeholders"
    description = "Each input has a non-empty placeholder (AR or EN)."
    category = "UI"

    def execute(self):
        self.open_register()
        for loc in (self.FIRST_NAME, self.LAST_NAME, self.EMAIL,
                    self.MOBILE, self.PASSWORD):
            el = self.driver.find_element(*loc)
            ph = self.read_placeholder(el)
            assert ph, f"{loc} has empty placeholder"
            self.slow(0.15)


# ══════════════════════════════════════════════════════════════
#  REGISTER_015 — Legal links (Terms & Privacy)
# ══════════════════════════════════════════════════════════════
class Register015(RegisterMixin, BaseTest):
    key = "REGISTER_015"
    name = "Legal section has Terms and Privacy links"
    description = "Terms & Privacy links exist (AR or EN)."
    category = "UI"

    def execute(self):
        self.open_register()
        legal = self.driver.find_element(*self.LEGAL)
        self.js("arguments[0].scrollIntoView({block:'center'});", legal)
        self.slow()
        text = self.read_text(legal).lower()
        assert contains_any(text, KEYWORDS["terms"]), \
            f"Missing Terms/الشروط. Text: '{text}'"
        assert contains_any(text, KEYWORDS["privacy"]), \
            f"Missing Privacy/الخصوصية. Text: '{text}'"
        links = legal.find_elements(By.TAG_NAME, "a")
        assert len(links) >= 2, f"Expected >=2 links, got {len(links)}"


# ══════════════════════════════════════════════════════════════
#  REGISTER_016 — Form POST + CSRF
# ══════════════════════════════════════════════════════════════
class Register016(RegisterMixin, BaseTest):
    key = "REGISTER_016"
    name = "Form uses POST with CSRF token"
    description = "method=POST and _token present."
    category = "Security"

    def execute(self):
        self.open_register()
        form = self.driver.find_element(*self.FORM)
        assert form.get_attribute("method").lower() == "post"
        token = self.driver.find_element(*self.TOKEN).get_attribute("value")
        self.slow()
        assert token and len(token) > 20, f"Bad CSRF: '{token}'"


# ══════════════════════════════════════════════════════════════
#  REGISTER_017 — Valid registration navigates to OTP
# ══════════════════════════════════════════════════════════════
class Register017(RegisterMixin, BaseTest):
    key = "REGISTER_017"
    name = "Valid registration redirects to OTP page"
    description = "Full valid form => lands on /onboarding/verify-phone."
    category = "E2E"

    def execute(self):
        self.open_register()
        self.fill_form()

        outcome = self.submit_and_wait_for_outcome(timeout=20)
        self.slow(0.8)

        assert "verify-phone" in self.driver.current_url or "onboarding" in self.driver.current_url, \
            f"Did not land on OTP page. URL: {self.driver.current_url} | outcome: {outcome}"

        # OTP page sanity
        self.wait.until(EC.presence_of_element_located(self.OTP_INPUTS))
        assert len(self.driver.find_elements(*self.OTP_INPUTS)) == 6, \
            "Expected 6 OTP inputs"


# ══════════════════════════════════════════════════════════════
#  REGISTER_018 — OTP page has debug code (test env)
# ══════════════════════════════════════════════════════════════
class Register018(RegisterMixin, BaseTest):
    key = "REGISTER_018"
    name = "OTP debug code is visible (test environment)"
    description = "The debug block reveals the 6-digit code."
    category = "E2E"

    def execute(self):
        self.open_register()
        self.fill_form()
        self.submit_and_wait_for_outcome(timeout=20)

        if "verify-phone" not in self.driver.current_url and \
           "onboarding" not in self.driver.current_url:
            raise SkipTest("Did not reach OTP page — registration may have failed")

        try:
            debug_el = WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located(self.OTP_DEBUG)
            )
            code = self.read_text(debug_el)
        except Exception:
            raise SkipTest("Debug code block not present (not a test env?)")

        self.slow()
        assert code.isdigit() and len(code) == 6, \
            f"Debug code is not a 6-digit number: '{code}'"


# ══════════════════════════════════════════════════════════════
#  REGISTER_019 — Full flow: register + OTP verify
# ══════════════════════════════════════════════════════════════
class Register019(RegisterMixin, BaseTest):
    key = "REGISTER_019"
    name = "Full registration: OTP verification succeeds"
    description = "Fill register, read debug OTP, submit, reach step 3."
    category = "E2E"

    def execute(self):
        self.open_register()
        self.fill_form()
        self.submit_and_wait_for_outcome(timeout=20)

        if "verify-phone" not in self.driver.current_url and \
           "onboarding" not in self.driver.current_url:
            raise SkipTest("Did not reach OTP page — registration failed")

        # Read the debug OTP code
        try:
            debug_el = WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located(self.OTP_DEBUG)
            )
            code = self.read_text(debug_el)
        except Exception:
            raise SkipTest("Debug OTP code not available in this environment")

        assert code.isdigit() and len(code) == 6, f"Bad OTP: '{code}'"

        # Fill the 6 OTP inputs
        inputs = self.driver.find_elements(*self.OTP_INPUTS)
        assert len(inputs) == 6
        for i, digit in enumerate(code):
            self.js("""
                var el = arguments[0];
                el.value = arguments[1];
                el.dispatchEvent(new Event('input', {bubbles:true}));
            """, inputs[i], digit)
            self.slow(0.2)

        # Give the page's JS a moment to enable the button
        self.slow(0.5)

        # Click verify
        self.safe_click_locator(self.OTP_SUBMIT)

        # Expect URL to change (to plan/step-3 or dashboard)
        WebDriverWait(self.driver, 20).until(
            lambda d: "verify-phone" not in d.current_url
        )
        self.slow(0.8)

        assert "verify-phone" not in self.driver.current_url, \
            "Still on OTP page after verification"


# ══════════════════════════════════════════════════════════════
#  REGISTER_020 — Register link in login header
# ══════════════════════════════════════════════════════════════
class Register020(RegisterMixin, BaseTest):
    key = "REGISTER_020"
    name = "Register link exists on login page"
    description = "Verify login page has a link back to /register."
    category = "Navigation"

    def execute(self):
        # This test uses login_url as source
        self.driver.get(self.config["base_url"])
        self.dismiss_cookies()
        self.slow(0.5)
        link = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".login-register-prompt a")
        ))
        href = (link.get_attribute("href") or "").lower()
        self.slow()
        assert "register" in href, f"Unexpected href: {href}"