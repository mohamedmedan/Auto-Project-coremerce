from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tests.base_test import BaseTest, SkipTest


class LoginMixin:
    feature = "login"
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "password")
    REMEMBER = (By.NAME, "remember")
    SUBMIT = (By.CSS_SELECTOR, "button.login-submit")
    TOGGLE = (By.CSS_SELECTOR, ".login-password-toggle")
    FORGOT = (By.CSS_SELECTOR, "a.login-forgot")
    REGISTER = (By.CSS_SELECTOR, ".login-register-prompt a")
    SOCIAL = (By.CSS_SELECTOR, ".login-social-btn")
    LEGAL = (By.CSS_SELECTOR, ".login-legal")
    HEADING = (By.CSS_SELECTOR, ".login-heading")
    TITLE = (By.CSS_SELECTOR, ".login-title")
    LOGO = (By.CSS_SELECTOR, ".login-logo")
    FORM = (By.ID, "form_data")
    TOKEN = (By.CSS_SELECTOR, "input[name='_token']")

    def open_login(self):
        self.driver.get(self.config["base_url"])
        self.wait.until(EC.presence_of_element_located(self.EMAIL))

    def js(self, script, *args):
        return self.driver.execute_script(script, *args)


class Login001(LoginMixin, BaseTest):
    key = "LOGIN_001"; name = "Login page loads"; category = "Smoke"
    description = "Logo, heading, inputs, submit, forgot, register visible."
    def execute(self):
        self.open_login()
        for loc in (self.LOGO, self.HEADING, self.TITLE, self.EMAIL,
                    self.PASSWORD, self.SUBMIT, self.FORGOT, self.REGISTER):
            assert self.driver.find_element(*loc).is_displayed(), f"{loc} missing"


class Login002(LoginMixin, BaseTest):
    key = "LOGIN_002"; name = "Email field accepts input"; category = "Functional"
    description = "Type a valid email and verify its value."
    def execute(self):
        self.open_login()
        el = self.driver.find_element(*self.EMAIL); el.clear()
        el.send_keys("tester@example.com")
        assert el.get_attribute("value") == "tester@example.com"


class Login003(LoginMixin, BaseTest):
    key = "LOGIN_003"; name = "Password field accepts input"; category = "Functional"
    description = "Type a password and verify its value."
    def execute(self):
        self.open_login()
        el = self.driver.find_element(*self.PASSWORD); el.clear()
        el.send_keys("Secret123!")
        assert el.get_attribute("value") == "Secret123!"


class Login004(LoginMixin, BaseTest):
    key = "LOGIN_004"; name = "Password toggle changes type"; category = "UI"
    description = "Click eye toggle, verify input type flips."
    def execute(self):
        self.open_login()
        pwd = self.driver.find_element(*self.PASSWORD)
        tog = self.driver.find_element(*self.TOGGLE)
        t1 = pwd.get_attribute("type"); tog.click()
        assert pwd.get_attribute("type") != t1; tog.click()
        assert pwd.get_attribute("type") == t1


class Login005(LoginMixin, BaseTest):
    key = "LOGIN_005"; name = "Remember me toggles"; category = "UI"
    description = "Click checkbox and verify state changes."
    def execute(self):
        self.open_login()
        cb = self.driver.find_element(*self.REMEMBER)
        assert not cb.is_selected(); cb.click(); assert cb.is_selected()


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
        el = self.driver.find_element(*self.EMAIL); el.send_keys("tager")
        msg = self.js("return arguments[0].validationMessage;", el)
        assert self.js("return arguments[0].checkValidity();", el) is False
        assert "@" in msg, f"Expected '@' in '{msg}'"


class Login008(LoginMixin, BaseTest):
    key = "LOGIN_008"; name = "Empty password required"; category = "Validation"
    description = "Fill email only, password must be invalid."
    def execute(self):
        self.open_login()
        self.driver.find_element(*self.EMAIL).send_keys("tester@example.com")
        pwd = self.driver.find_element(*self.PASSWORD)
        assert self.js("return arguments[0].checkValidity();", pwd) is False


class Login009(LoginMixin, BaseTest):
    key = "LOGIN_009"; name = "Invalid credentials show error"; category = "Auth"
    description = "Wrong creds produce error banner."
    def execute(self):
        self.open_login()
        c = self.config["credentials"]["invalid"]
        self.driver.find_element(*self.EMAIL).send_keys(c["email"])
        self.driver.find_element(*self.PASSWORD).send_keys(c["password"])
        self.driver.find_element(*self.SUBMIT).click()
        WebDriverWait(self.driver, 15).until(
            lambda d: "do not match" in d.page_source.lower()
            or "credentials" in d.page_source.lower()
        )


class Login010(LoginMixin, BaseTest):
    key = "LOGIN_010"; name = "Valid credentials log in"; category = "Auth"
    description = "Submit valid creds => redirect away from /login."
    def execute(self):
        c = self.config["credentials"]["valid"]
        if "REPLACE" in c["email"].upper() or not c["email"]:
            raise SkipTest("Valid credentials not configured")
        self.open_login()
        self.driver.find_element(*self.EMAIL).send_keys(c["email"])
        self.driver.find_element(*self.PASSWORD).send_keys(c["password"])
        self.driver.find_element(*self.SUBMIT).click()
        WebDriverWait(self.driver, 20).until(
            lambda d: "/login" not in d.current_url.rstrip("/")
        )


class Login011(LoginMixin, BaseTest):
    key = "LOGIN_011"; name = "Forgot password link"; category = "Navigation"
    description = "Href contains /forgot-password."
    def execute(self):
        self.open_login()
        h = self.driver.find_element(*self.FORGOT).get_attribute("href")
        assert h and "forgot-password" in h, f"Unexpected href: {h}"


class Login012(LoginMixin, BaseTest):
    key = "LOGIN_012"; name = "Register link"; category = "Navigation"
    description = "Href contains /register."
    def execute(self):
        self.open_login()
        h = self.driver.find_element(*self.REGISTER).get_attribute("href")
        assert h and "register" in h, f"Unexpected href: {h}"


class Login013(LoginMixin, BaseTest):
    key = "LOGIN_013"; name = "Social buttons rendered"; category = "UI"
    description = "Google and Apple buttons exist."
    def execute(self):
        self.open_login()
        b = self.driver.find_elements(*self.SOCIAL)
        assert len(b) == 2, f"Expected 2, found {len(b)}"
        t = [x.text.strip().lower() for x in b]
        assert any("google" in x for x in t) and any("apple" in x for x in t)


class Login014(LoginMixin, BaseTest):
    key = "LOGIN_014"; name = "Legal links present"; category = "UI"
    description = "Terms and Privacy links in legal text."
    def execute(self):
        self.open_login()
        legal = self.driver.find_element(*self.LEGAL)
        t = legal.text.lower()
        assert "terms" in t and "privacy" in t
        assert len(legal.find_elements(By.TAG_NAME, "a")) >= 2


class Login015(LoginMixin, BaseTest):
    key = "LOGIN_015"; name = "Enter submits form"; category = "UX"
    description = "Press Enter in password field."
    def execute(self):
        self.open_login()
        self.driver.find_element(*self.EMAIL).send_keys("tester@example.com")
        pwd = self.driver.find_element(*self.PASSWORD); pwd.send_keys("somepass")
        u = self.driver.current_url; pwd.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 5).until(
            lambda d: d.current_url != u or "do not match" in d.page_source.lower()
        )


class Login016(LoginMixin, BaseTest):
    key = "LOGIN_016"; name = "Email auto-focused"; category = "UX"
    description = "Active element after load is email input."
    def execute(self):
        self.open_login()
        a = self.js("return document.activeElement ? document.activeElement.id : '';")
        assert a == "email", f"Focused: {a}"


class Login017(LoginMixin, BaseTest):
    key = "LOGIN_017"; name = "POST + CSRF token"; category = "Security"
    description = "Form method POST and _token present."
    def execute(self):
        self.open_login()
        f = self.driver.find_element(*self.FORM)
        assert f.get_attribute("method").lower() == "post"
        tok = self.driver.find_element(*self.TOKEN).get_attribute("value")
        assert tok and len(tok) > 20


class Login018(LoginMixin, BaseTest):
    key = "LOGIN_018"; name = "Placeholders correct"; category = "UI"
    description = "Email and password placeholders."
    def execute(self):
        self.open_login()
        e = self.driver.find_element(*self.EMAIL).get_attribute("placeholder").lower()
        p = self.driver.find_element(*self.PASSWORD).get_attribute("placeholder").lower()
        assert "email" in e and "password" in p


class Login019(LoginMixin, BaseTest):
    key = "LOGIN_019"; name = "Submit says Sign In"; category = "UI"
    description = "Button text contains 'sign in'."
    def execute(self):
        self.open_login()
        b = self.driver.find_element(*self.SUBMIT)
        assert "sign in" in b.text.strip().lower()


class Login020(LoginMixin, BaseTest):
    key = "LOGIN_020"; name = "Heading Welcome back"; category = "Content"
    description = "H1 equals 'Welcome back'."
    def execute(self):
        self.open_login()
        h = self.driver.find_element(*self.HEADING).text.strip()
        assert h.lower() == "welcome back", f"Got: {h}"
