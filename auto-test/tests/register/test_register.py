from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.base_test import BaseTest, SkipTest


class RegisterMixin:
    feature = "register"
    NAME = (By.ID, "name")
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "password")
    CONFIRM = (By.ID, "password_confirmation")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")
    LOGIN_LINK = (By.CSS_SELECTOR, "a[href*='login']")
    FORM = (By.TAG_NAME, "form")
    HEADING = (By.TAG_NAME, "h1")

    def open_register(self):
        url = self.config.get("register_url", "").strip()
        if not url:
            raise SkipTest("register_url not configured in config.json")
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located(self.FORM))

    def js(self, script, *args):
        return self.driver.execute_script(script, *args)


class Register001(RegisterMixin, BaseTest):
    key = "REGISTER_001"; name = "Register page loads"; category = "Smoke"
    description = "Form and heading visible."
    def execute(self):
        self.open_register()
        assert self.driver.find_element(*self.FORM).is_displayed()
        assert self.driver.find_element(*self.HEADING).is_displayed()


class Register002(RegisterMixin, BaseTest):
    key = "REGISTER_002"; name = "Required fields present"; category = "Functional"
    description = "Name, email and password inputs visible."
    def execute(self):
        self.open_register()
        for loc in (self.NAME, self.EMAIL, self.PASSWORD):
            assert self.driver.find_element(*loc).is_displayed(), f"{loc} missing"


class Register003(RegisterMixin, BaseTest):
    key = "REGISTER_003"; name = "Empty form blocked"; category = "Validation"
    description = "checkValidity() is False on empty form."
    def execute(self):
        self.open_register()
        f = self.driver.find_element(*self.FORM)
        assert self.js("return arguments[0].checkValidity();", f) is False


class Register004(RegisterMixin, BaseTest):
    key = "REGISTER_004"; name = "Invalid email error"; category = "Validation"
    description = "Typing 'abc' produces '@' validation message."
    def execute(self):
        self.open_register()
        el = self.driver.find_element(*self.EMAIL); el.send_keys("abc")
        msg = self.js("return arguments[0].validationMessage;", el)
        assert self.js("return arguments[0].checkValidity();", el) is False
        assert "@" in msg


class Register005(RegisterMixin, BaseTest):
    key = "REGISTER_005"; name = "Login link present"; category = "Navigation"
    description = "Link to login page exists."
    def execute(self):
        self.open_register()
        l = self.driver.find_element(*self.LOGIN_LINK)
        assert "login" in (l.get_attribute("href") or "").lower()
