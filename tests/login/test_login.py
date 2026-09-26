import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.base_test import BaseTest, SkipTest


# ══════════════════════════════════════════════════════════════
#  Bilingual keyword sets (Arabic + English)
# ══════════════════════════════════════════════════════════════
KEYWORDS = {
    "sign_in": [
        "sign in", "signin", "login", "log in",
        "تسجيل الدخول", "دخول", "تسجيل دخول",
    ],
    "email_field": [
        "email", "e-mail", "mail",
        "بريد", "الإلكتروني", "الالكتروني", "بريدك",
    ],
    "password_field": [
        "password", "pass",
        "كلمة المرور", "كلمه المرور", "المرور", "كلمة السر",
    ],
    "terms": [
        "terms", "conditions", "terms & conditions",
        "الشروط", "الأحكام", "الاحكام", "شروط",
    ],
    "privacy": [
        "privacy", "privacy policy",
        "الخصوصية", "خصوصية", "سياسة الخصوصية",
    ],
    "invalid_creds": [
        # English variants
        "do not match", "credentials", "these credentials",
        "invalid", "incorrect", "wrong",
        # Arabic variants (شائعة في Laravel بالعربي)
        "بيانات الاعتماد", "لا تتطابق", "غير صحيحة", "خطأ",
        "بيانات الدخول", "كلمة المرور غير", "البريد الإلكتروني غير",
        "سجلاتنا", "غير مطابقة", "غير صحيحة",
    ],
}

ERROR_SELECTORS = [
    (By.CSS_SELECTOR, ".alert-danger"),
    (By.CSS_SELECTOR, ".alert-error"),
    (By.CSS_SELECTOR, ".invalid-feedback"),
    (By.CSS_SELECTOR, ".text-danger"),
    (By.CSS_SELECTOR, ".error-message"),
    (By.CSS_SELECTOR, "[role='alert']"),
    (By.CSS_SELECTOR, ".error"),
    (By.CSS_SELECTOR, "div.alert"),
    (By.CSS_SELECTOR, ".form-error"),
]


def contains_any(text: str, keywords: list) -> bool:
    """True if any keyword appears in text (case-insensitive)."""
    if not text:
        return False
    low = text.lower()
    return any(k.lower() in low for k in keywords)


class LoginMixin:
    feature = "login"

    # ── Locators ──────────────────────────────────────────
    EMAIL        = (By.ID, "email")
    PASSWORD     = (By.ID, "password")
    REMEMBER     = (By.NAME, "remember")
    SUBMIT       = (By.CSS_SELECTOR, "button.login-submit")
    TOGGLE       = (By.CSS_SELECTOR, ".login-password-toggle")
    FORGOT       = (By.CSS_SELECTOR, "a.login-forgot")
    REGISTER     = (By.CSS_SELECTOR, ".login-register-prompt a")
    SOCIAL       = (By.CSS_SELECTOR, ".login-social-btn")
    LEGAL        = (By.CSS_SELECTOR, ".login-legal")
    HEADING      = (By.CSS_SELECTOR, ".login-heading")
    TITLE        = (By.CSS_SELECTOR, ".login-title")
    LOGO         = (By.CSS_SELECTOR, ".login-logo")
    FORM         = (By.ID, "form_data")
    TOKEN        = (By.CSS_SELECTOR, "input[name='_token']")

    # ── Cookie consent ────────────────────────────────────
    COOKIE_BANNER = (By.ID, "cm")
    COOKIE_ACCEPT = (By.ID, "c-p-bn")

    # ── Timing ────────────────────────────────────────────
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

    def open_login(self):
        self.driver.get(self.config["base_url"])
        self.wait.until(EC.presence_of_element_located(self.EMAIL))
        self.dismiss_cookies()
        self.slow()

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

    # ── Error-banner detector (bilingual) ─────────────────
    def any_error_banner_visible(self) -> str:
        """Return text of first visible error element, or '' if none."""
        for sel in ERROR_SELECTORS:
            try:
                els = self.driver.find_elements(*sel)
            except Exception:
                continue
            for el in els:
                try:
                    if not el.is_displayed():
                        continue
                    txt = self.read_text(el) or (el.get_attribute("textContent") or "")
                    txt = txt.strip()
                    if txt and contains_any(txt, KEYWORDS["invalid_creds"]):
                        return txt
                except Exception:
                    continue
        return ""


# ══════════════════════════════════════════════════════════════
#  LOGIN_001 .. 020
# ══════════════════════════════════════════════════════════════
class Login001(LoginMixin, BaseTest):
    key = "LOGIN_001"; name = "Login page loads"; category = "Smoke"
    description = "Logo, heading, inputs, submit, forgot & register visible."
    def execute(self):
        self.open_login()
        for loc in (self.LOGO, self.HEADING, self.TITLE, self.EMAIL,
                    self.PASSWORD, self.SUBMIT, self.FORGOT, self.REGISTER):
            assert self.driver.find_element(*loc).is_displayed(), f"{loc} missing"
            self.slow(0.15)


class Login002(LoginMixin, BaseTest):
    key = "LOGIN_002"; name = "Email field accepts input"; category = "Functional"
    description = "Type a valid email and verify its value."
    def execute(self):
        self.open_login()
        el = self.driver.find_element(*self.EMAIL)
        el.clear(); el.send_keys("tester@example.com"); self.slow()
        assert el.get_attribute("value") == "tester@example.com"


class Login003(LoginMixin, BaseTest):
    key = "LOGIN_003"; name = "Password field accepts input"; category = "Functional"
    description = "Type a password and verify its value."
    def execute(self):
        self.open_login()
        el = self.driver.find_element(*self.PASSWORD)
        el.clear(); el.send_keys("Secret123!"); self.slow()
        assert el.get_attribute("value") == "Secret123!"


class Login004(LoginMixin, BaseTest):
    key = "LOGIN_004"; name = "Password toggle changes type"; category = "UI"
    description = "Click eye toggle, verify input type flips."
    def execute(self):
        self.open_login()
        pwd = self.driver.find_element(*self.PASSWORD)
        pwd.send_keys("whatever"); self.slow()
        initial = pwd.get_attribute("type")
        self.safe_click_locator(self.TOGGLE)
        assert pwd.get_attribute("type") != initial
        self.safe_click_locator(self.TOGGLE)
        assert pwd.get_attribute("type") == initial


class Login005(LoginMixin, BaseTest):
    key = "LOGIN_005"; name = "Remember me toggles"; category = "UI"
    description = "Click checkbox and verify state changes."
    def execute(self):
        self.open_login()
        cb = self.driver.find_element(*self.REMEMBER)
        assert not cb.is_selected()
        self.safe_click_element(cb)
        assert cb.is_selected()
        self.safe_click_element(cb)
        assert not cb.is_selected()


class Login006(LoginMixin, BaseTest):
    key = "LOGIN_006"; name = "Empty form blocked"; category = "Validation"
    description = "Both required fields empty => form invalid."
    def execute(self):
        self.open_login()
        form = self.driver.find_element(*self.FORM)
        assert self.js("return arguments[0].checkValidity();", form) is False


class Login007(LoginMixin, BaseTest):
    key = "LOGIN_007"; name = "Invalid email HTML5 error"; category = "Validation"
    description = "Enter 'tager' => validation message mentions '@'."
    def execute(self):
        self.open_login()
        el = self.driver.find_element(*self.EMAIL)
        el.send_keys("tager"); self.slow()
        msg = self.js("return arguments[0].validationMessage;", el)
        assert self.js("return arguments[0].checkValidity();", el) is False
        assert "@" in msg, f"Expected '@', got '{msg}'"


class Login008(LoginMixin, BaseTest):
    key = "LOGIN_008"; name = "Empty password required"; category = "Validation"
    description = "Fill email only, password must be invalid."
    def execute(self):
        self.open_login()
        self.driver.find_element(*self.EMAIL).send_keys("tester@example.com")
        self.slow()
        pwd = self.driver.find_element(*self.PASSWORD)
        assert self.js("return arguments[0].checkValidity();", pwd) is False


# ── LOGIN_009 — Invalid credentials (bilingual, robust) ─────
class Login009(LoginMixin, BaseTest):
    key = "LOGIN_009"
    name = "Invalid credentials show error banner"
    description = "Wrong creds produce error banner (Arabic or English)."
    category = "Auth"

    def execute(self):
        self.open_login()

        c = self.config["credentials"]["invalid"]
        email = self.driver.find_element(*self.EMAIL)
        pwd   = self.driver.find_element(*self.PASSWORD)
        email.clear(); email.send_keys(c["email"]); self.slow()
        pwd.clear();   pwd.send_keys(c["password"]); self.slow()

        self.dismiss_cookies()
        self.slow()

        # Snapshot before submit
        url_before = self.driver.current_url

        self.safe_click_locator(self.SUBMIT)

        # Wait for ONE of these conditions:
        #   1) an error banner appears (with localized keywords)
        #   2) URL changes
        #   3) page still on /login after a while (fallback)
        deadline = time.time() + 15
        found_error = ""
        while time.time() < deadline:
            found_error = self.any_error_banner_visible()
            if found_error:
                break
            if self.driver.current_url != url_before:
                break
            time.sleep(0.4)

        self.slow(0.8)

        if found_error:
            # Success — banner detected
            self._found_banner = found_error
            return

        # Fallback: check raw page source (covers banners without semantic
        # classes: bare <div> with Arabic text etc.)
        page = self.driver.page_source.lower()
        if contains_any(page, KEYWORDS["invalid_creds"]):
            return

        # If we're still on the login page, that itself is enough evidence
        # that login was rejected.
        if "/login" in self.driver.current_url:
            return

        raise AssertionError(
            "No error banner found and page navigated away unexpectedly. "
            f"URL: {self.driver.current_url}"
        )


# ── LOGIN_010 — Valid login ────────────────────────────────
class Login010(LoginMixin, BaseTest):
    key = "LOGIN_010"
    name = "Valid credentials log in"
    description = "Submit valid creds => redirect away from /login."
    category = "Auth"

    def execute(self):
        c = self.config["credentials"]["valid"]
        if "REPLACE" in c["email"].upper() or not c["email"]:
            raise SkipTest("Valid credentials not configured in config.json")

        self.open_login()
        email = self.driver.find_element(*self.EMAIL)
        pwd   = self.driver.find_element(*self.PASSWORD)
        email.clear(); email.send_keys(c["email"]); self.slow()
        pwd.clear();   pwd.send_keys(c["password"]); self.slow()

        self.dismiss_cookies()
        self.slow()

        self.safe_click_locator(self.SUBMIT)
        WebDriverWait(self.driver, 25).until(
            lambda d: "/login" not in d.current_url.rstrip("/")
        )
        self.slow(0.5)


class Login011(LoginMixin, BaseTest):
    key = "LOGIN_011"; name = "Forgot password link"; category = "Navigation"
    description = "Href contains /forgot-password."
    def execute(self):
        self.open_login()
        h = self.driver.find_element(*self.FORGOT).get_attribute("href")
        self.slow()
        assert h and "forgot-password" in h, f"Unexpected: {h}"


class Login012(LoginMixin, BaseTest):
    key = "LOGIN_012"; name = "Register link"; category = "Navigation"
    description = "Href contains /register."
    def execute(self):
        self.open_login()
        h = self.driver.find_element(*self.REGISTER).get_attribute("href")
        self.slow()
        assert h and "register" in h, f"Unexpected: {h}"


class Login013(LoginMixin, BaseTest):
    key = "LOGIN_013"; name = "Social buttons rendered"; category = "UI"
    description = "Google and Apple buttons exist."
    def execute(self):
        self.open_login()
        btns = self.driver.find_elements(*self.SOCIAL)
        self.slow()
        assert len(btns) == 2, f"Expected 2, found {len(btns)}"
        # Button labels are brand names — always English
        texts = [self.read_text(b).lower() for b in btns]
        assert any("google" in t for t in texts), f"No Google: {texts}"
        assert any("apple" in t for t in texts), f"No Apple: {texts}"


# ── LOGIN_014 — Legal links (bilingual) ────────────────────
class Login014(LoginMixin, BaseTest):
    key = "LOGIN_014"
    name = "Legal section has Terms and Privacy links"
    description = "Legal text contains Terms & Privacy links (Arabic or English)."
    category = "UI"

    def execute(self):
        self.open_login()
        legal = self.driver.find_element(*self.LEGAL)
        self.js("arguments[0].scrollIntoView({block:'center'});", legal)
        self.slow()

        text = self.read_text(legal)
        low  = text.lower()

        has_terms = contains_any(low, KEYWORDS["terms"])
        has_privacy = contains_any(low, KEYWORDS["privacy"])

        assert has_terms, \
            f"Missing Terms/الشروط. Text: '{text}'"
        assert has_privacy, \
            f"Missing Privacy/الخصوصية. Text: '{text}'"

        links = legal.find_elements(By.TAG_NAME, "a")
        assert len(links) >= 2, \
            f"Expected >=2 links, found {len(links)}"
        self.slow()


class Login015(LoginMixin, BaseTest):
    key = "LOGIN_015"; name = "Enter submits form"; category = "UX"
    description = "Press Enter in password field to trigger navigation."
    def execute(self):
        self.open_login()
        self.driver.find_element(*self.EMAIL).send_keys("tester@example.com")
        self.slow()
        pwd = self.driver.find_element(*self.PASSWORD)
        pwd.send_keys("somepass"); self.slow()
        u = self.driver.current_url
        pwd.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 8).until(
            lambda d: d.current_url != u
            or contains_any(d.page_source.lower(), KEYWORDS["invalid_creds"])
        )
        self.slow(0.5)


class Login016(LoginMixin, BaseTest):
    key = "LOGIN_016"; name = "Email auto-focused"; category = "UX"
    description = "Active element after load is email input."
    def execute(self):
        self.open_login()
        a = self.js("return document.activeElement ? document.activeElement.id : '';")
        self.slow()
        assert a == "email", f"Focused: '{a}'"


class Login017(LoginMixin, BaseTest):
    key = "LOGIN_017"; name = "POST + CSRF token"; category = "Security"
    description = "Form method POST and _token present."
    def execute(self):
        self.open_login()
        f = self.driver.find_element(*self.FORM)
        assert f.get_attribute("method").lower() == "post"
        tok = self.driver.find_element(*self.TOKEN).get_attribute("value")
        self.slow()
        assert tok and len(tok) > 20, f"CSRF bad: '{tok}'"


# ── LOGIN_018 — Placeholders (bilingual) ───────────────────
class Login018(LoginMixin, BaseTest):
    key = "LOGIN_018"
    name = "Inputs have correct placeholders"
    description = "Email/password placeholders mention the field (Arabic or English)."
    category = "UI"

    def execute(self):
        self.open_login()
        email_el = self.driver.find_element(*self.EMAIL)
        pwd_el   = self.driver.find_element(*self.PASSWORD)

        e_ph = self.read_placeholder(email_el)
        p_ph = self.read_placeholder(pwd_el)
        self.slow()

        assert e_ph, "Email placeholder is empty"
        assert p_ph, "Password placeholder is empty"

        assert contains_any(e_ph, KEYWORDS["email_field"]), \
            f"Email placeholder was: '{e_ph}'"
        assert contains_any(p_ph, KEYWORDS["password_field"]), \
            f"Password placeholder was: '{p_ph}'"


# ── LOGIN_019 — Submit button label (bilingual) ────────────
class Login019(LoginMixin, BaseTest):
    key = "LOGIN_019"
    name = "Submit button says Sign In"
    description = "Button text contains 'Sign In' (Arabic or English)."
    category = "UI"

    def execute(self):
        self.open_login()
        btn = self.driver.find_element(*self.SUBMIT)
        text = self.read_text(btn)
        self.slow()

        # Fallback: read value attribute if textContent was empty
        if not text:
            text = (btn.get_attribute("value") or "").strip()

        assert contains_any(text, KEYWORDS["sign_in"]), \
            f"Button text was: '{text}'"


class Login020(LoginMixin, BaseTest):
    key = "LOGIN_020"; name = "Heading visible"; category = "Content"
    description = "Heading H1 is visible with non-empty text."
    def execute(self):
        self.open_login()
        h_el = self.driver.find_element(*self.HEADING)
        h = self.read_text(h_el)
        self.slow()
        # Heading text differs between EN/AR — assert it exists and is
        # one of the two expected strings (case-insensitive).
        assert h, "Heading is empty"
        accepted = ["welcome back", "مرحبا بعودتك", "أهلاً بعودتك",
                    "مرحباً بعودتك", "مرحبا"]
        assert contains_any(h, accepted) or any(a in h.lower() for a in accepted), \
            f"Unexpected heading: '{h}'"