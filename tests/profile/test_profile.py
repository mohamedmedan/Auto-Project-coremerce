import os
import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.base_test import BaseTest, SkipTest

# ── Avatar image path ─────────────────────────────────────────
AVATAR_PATH = Path(__file__).resolve().parent / "av.png"


# ══════════════════════════════════════════════════════════════
#  Bilingual keyword sets
# ══════════════════════════════════════════════════════════════
KEYWORDS = {
    "personal_info": [
        "personal info", "personal information",
        "المعلومات الشخصية", "البيانات الشخصية", "معلومات",
    ],
    "name_required": [
        "name field is required", "the name field", "name is required",
        "name must", "الاسم مطلوب", "حقل الاسم", "الاسم",
    ],
    "email_invalid": [
        "valid email", "email must be", "email address",
        "بريد صالح", "بريد إلكتروني صالح", "valid email address",
    ],
    "success_update": [
        "successfully updated", "updated successfully",
        "personal info successfully", "changes saved", "saved successfully",
        "تم التحديث", "تم تحديث", "بنجاح", "تم الحفظ", "تم بنجاح",
    ],
    "save_button": [
        "save changes", "save", "update",
        "حفظ", "تحديث", "حفظ التغييرات",
    ],
}

SUCCESS_SELECTORS = [
    (By.CSS_SELECTOR, ".alert-success"),
    (By.CSS_SELECTOR, "[role='alert'].alert-success"),
    (By.CSS_SELECTOR, ".toast-success"),
    (By.CSS_SELECTOR, ".swal2-success"),
    (By.CSS_SELECTOR, ".alert.alert-success"),
    (By.CSS_SELECTOR, "div.alert-success"),
    (By.CSS_SELECTOR, ".toast-body"),
    (By.CSS_SELECTOR, ".notification-success"),
    (By.CSS_SELECTOR, ".flash-message.success"),
    (By.CSS_SELECTOR, "[data-toast-type='success']"),
]

ERROR_SELECTORS = [
    (By.CSS_SELECTOR, ".alert-danger"),
    (By.CSS_SELECTOR, ".alert-error"),
    (By.CSS_SELECTOR, ".invalid-feedback"),
    (By.CSS_SELECTOR, ".text-danger"),
    (By.CSS_SELECTOR, ".error-message"),
    (By.CSS_SELECTOR, "[role='alert']"),
    (By.CSS_SELECTOR, "div.alert"),
    (By.CSS_SELECTOR, ".form-error"),
    (By.CSS_SELECTOR, ".help-block"),
    (By.CSS_SELECTOR, ".field-error"),
    (By.CSS_SELECTOR, "small.text-danger"),
    (By.CSS_SELECTOR, ".alert.alert-danger"),
]


def contains_any(text, keywords):
    if not text:
        return False
    low = text.lower()
    return any(k.lower() in low for k in keywords)


class ProfileMixin:
    feature = "profile"

    # ── Form locators ─────────────────────────────────────
    FORM         = (By.CSS_SELECTOR, "form[action*='edit-profile']")
    AVATAR       = (By.ID, "blah")
    FILE_INPUT   = (By.ID, "file-1")
    NAME         = (By.ID, "name")
    EMAIL        = (By.ID, "email")
    MOBILE       = (By.ID, "mobile")
    SUBMIT       = (By.CSS_SELECTOR, "input[type='submit'][value='Save Changes']")
    SUBMIT_ALT   = (By.CSS_SELECTOR, "input.btn-primary[type='submit']")
    TOKEN        = (By.CSS_SELECTOR, "form[action*='edit-profile'] input[name='_token']")
    CARD_HEADER  = (By.XPATH,
                    "//h5[contains(.,'Personal Info') or contains(.,'المعلومات الشخصية')]")

    # ── Cookie banner ─────────────────────────────────────
    COOKIE_ACCEPT = (By.ID, "c-p-bn")

    # ══════════════════════════════════════════════════════
    #  Timing & low-level helpers
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

    def is_alive(self):
        """Check the driver still has a live browser window."""
        try:
            _ = self.driver.window_handles
            return True
        except Exception:
            return False

    def ensure_alive(self):
        if not self.is_alive():
            raise AssertionError("Browser window is no longer available (session died)")

    def navigate(self, url):
        """driver.get with a pre-check."""
        self.ensure_alive()
        self.driver.get(url)
        self.ensure_alive()

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
        self.slow(0.2)
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

    def read_value(self, element):
        """Always reads the live DOM property `value`, not the HTML attribute."""
        return self.js("return (arguments[0].value !== undefined) "
                       "? String(arguments[0].value) : '';", element)

    # ══════════════════════════════════════════════════════
    #  ⭐ ROBUST fill_field: try native, fallback to JS
    # ══════════════════════════════════════════════════════
    def fill_field(self, locator, value):
        """
        Fills a field safely and returns the *actual* value that ended up
        in the DOM. Uses native send_keys first, then JS as a fallback.
        """
        value = "" if value is None else str(value)

        el = self.wait.until(EC.presence_of_element_located(locator))
        self.js("arguments[0].scrollIntoView({block:'center'});", el)
        self.slow(0.15)

        # ── Attempt 1: native interaction ─────────────────
        try:
            self.js("arguments[0].focus();", el)
            el.click()
            self.slow(0.1)
            el.clear()
            self.slow(0.1)
            if value:
                el.send_keys(value)
            self.slow(0.2)
        except Exception:
            pass

        # Verify what actually landed
        current = self.read_value(el)
        if current == value:
            return current

        # ── Attempt 2: JS-based set + events ──────────────
        try:
            self.js("""
                var el = arguments[0], val = arguments[1];
                el.focus();
                // Clear
                el.value = '';
                el.dispatchEvent(new Event('input', {bubbles:true}));
                el.dispatchEvent(new Event('change', {bubbles:true}));
                // Set new value
                el.value = val;
                el.dispatchEvent(new Event('input', {bubbles:true}));
                el.dispatchEvent(new Event('change', {bubbles:true}));
                el.dispatchEvent(new KeyboardEvent('keyup', {bubbles:true}));
                el.blur();
            """, el, value)
            self.slow(0.25)
        except Exception:
            pass

        return self.read_value(el)

    # ══════════════════════════════════════════════════════
    #  Login (fast — minimizes delays during login only)
    # ══════════════════════════════════════════════════════
    def login(self):
        creds = self.config["credentials"]["valid"]
        if not creds.get("email") or "REPLACE" in creds["email"].upper():
            raise SkipTest("credentials.valid not configured")

        # Speed up login: temporarily lower the step delay
        old_delay = self.config.get("step_delay", 0.6)
        self.config["step_delay"] = 0.05
        try:
            self.navigate(self.config["base_url"])
            self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            self.dismiss_cookies()

            # Use the JS-robust fill so login fields always populate
            self.fill_field((By.ID, "email"), creds["email"])
            self.fill_field((By.ID, "password"), creds["password"])

            self.dismiss_cookies()
            self.safe_click_locator((By.CSS_SELECTOR, "button.login-submit"))

            WebDriverWait(self.driver, 25).until(
                lambda d: "/login" not in d.current_url.rstrip("/")
            )
        finally:
            self.config["step_delay"] = old_delay
        self.slow(0.3)

    # ══════════════════════════════════════════════════════
    #  Open /profile (login if needed)
    # ══════════════════════════════════════════════════════
    def open_profile(self):
        profile_url = self.config.get("profile_url", "").strip()
        if not profile_url:
            raise SkipTest("profile_url not configured in config.json")

        url = self.driver.current_url or ""
        not_logged_in = (
            not url
            or url.startswith("data:")
            or "about:blank" in url
            or "/login" in url
        )
        if not_logged_in:
            self.login()

        self.navigate(profile_url)
        self.dismiss_cookies()
        self.slow(0.5)

        # Bounced to login? Log in and retry once
        if "/login" in self.driver.current_url:
            self.login()
            self.navigate(profile_url)
            self.dismiss_cookies()
            self.slow(0.5)

        self.wait.until(EC.presence_of_element_located(self.FORM))

    # ══════════════════════════════════════════════════════
    #  Banner detection
    # ══════════════════════════════════════════════════════
    def _collect_text(self, selectors):
        chunks = []
        for sel in selectors:
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
        return self._collect_text(SUCCESS_SELECTORS)

    def visible_error_text(self):
        return self._collect_text(ERROR_SELECTORS)

    def wait_for_success(self, timeout=15):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not self.is_alive():
                return ""
            txt = self.visible_success_text()
            if txt and contains_any(txt, KEYWORDS["success_update"]):
                return txt
            if contains_any(self.driver.page_source, KEYWORDS["success_update"]):
                return "success (page source)"
            time.sleep(0.35)
        return ""

    def wait_for_error(self, timeout=15):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not self.is_alive():
                return ""
            txt = self.visible_error_text()
            if txt:
                return txt
            if contains_any(self.driver.page_source, KEYWORDS["name_required"]):
                return "name required (page source)"
            if contains_any(self.driver.page_source, KEYWORDS["email_invalid"]):
                return "email invalid (page source)"
            time.sleep(0.35)
        return ""

    # ══════════════════════════════════════════════════════
    #  Snapshot current values
    # ══════════════════════════════════════════════════════
    def current_values(self):
        return {
            "name":   self.read_value(self.driver.find_element(*self.NAME)),
            "email":  self.read_value(self.driver.find_element(*self.EMAIL)),
            "mobile": self.read_value(self.driver.find_element(*self.MOBILE)),
        }

    def click_save(self):
        try:
            self.safe_click_locator(self.SUBMIT)
        except Exception:
            self.safe_click_locator(self.SUBMIT_ALT)
        # Give the form a moment to start submitting
        self.slow(0.4)


# ══════════════════════════════════════════════════════════════
#  PROFILE_001 — Page loads
# ══════════════════════════════════════════════════════════════
class Profile001(ProfileMixin, BaseTest):
    key = "PROFILE_001"
    name = "Profile page loads with form elements"
    description = "Form, avatar, name, email, mobile inputs visible."
    category = "Smoke"

    def execute(self):
        self.open_profile()
        for loc in (self.FORM, self.AVATAR, self.NAME, self.EMAIL, self.MOBILE):
            assert self.driver.find_element(*loc).is_displayed(), f"{loc} missing"
            self.slow(0.15)


# ══════════════════════════════════════════════════════════════
#  PROFILE_002 — Form POST + multipart + CSRF
# ══════════════════════════════════════════════════════════════
class Profile002(ProfileMixin, BaseTest):
    key = "PROFILE_002"
    name = "Form uses POST, multipart, and has CSRF"
    description = "method=POST, enctype=multipart, _token present."
    category = "Security"

    def execute(self):
        self.open_profile()
        form = self.driver.find_element(*self.FORM)
        assert form.get_attribute("method").lower() == "post"
        enctype = (form.get_attribute("enctype") or "").lower()
        assert "multipart" in enctype, f"enctype: '{enctype}'"
        tok = self.driver.find_element(*self.TOKEN).get_attribute("value")
        self.slow()
        assert tok and len(tok) > 20


# ══════════════════════════════════════════════════════════════
#  PROFILE_003/004/005 — Pre-filled values
# ══════════════════════════════════════════════════════════════
class Profile003(ProfileMixin, BaseTest):
    key = "PROFILE_003"; name = "Name field is pre-filled"; category = "Functional"
    description = "Name input already has a value on load."
    def execute(self):
        self.open_profile()
        val = self.current_values()["name"]
        self.slow()
        assert val.strip(), "Name is empty on load"


class Profile004(ProfileMixin, BaseTest):
    key = "PROFILE_004"; name = "Email field is pre-filled"; category = "Functional"
    description = "Email input already has a value on load."
    def execute(self):
        self.open_profile()
        val = self.current_values()["email"]
        self.slow()
        assert val.strip() and "@" in val, f"Email: '{val}'"


class Profile005(ProfileMixin, BaseTest):
    key = "PROFILE_005"; name = "Mobile field is pre-filled"; category = "Functional"
    description = "Mobile input already has a value on load."
    def execute(self):
        self.open_profile()
        val = self.current_values()["mobile"]
        self.slow()
        assert val.strip(), "Mobile is empty on load"


# ══════════════════════════════════════════════════════════════
#  PROFILE_006 — Avatar rendered
# ══════════════════════════════════════════════════════════════
class Profile006(ProfileMixin, BaseTest):
    key = "PROFILE_006"; name = "Avatar image is rendered"; category = "UI"
    description = "The #blah avatar has a non-empty src."
    def execute(self):
        self.open_profile()
        src = self.driver.find_element(*self.AVATAR).get_attribute("src") or ""
        self.slow()
        assert src.startswith("http") or src.startswith("data:image"), \
            f"Avatar src: '{src}'"


# ══════════════════════════════════════════════════════════════
#  PROFILE_007/008/009 — Fields accept input (FIXED)
# ══════════════════════════════════════════════════════════════
class Profile007(ProfileMixin, BaseTest):
    key = "PROFILE_007"
    name = "Name field accepts input"
    description = "Type into name and verify value."
    category = "Functional"

    def execute(self):
        self.open_profile()
        original = self.current_values()["name"]
        got = self.fill_field(self.NAME, "TestName123")
        assert got == "TestName123", f"Got: '{got}'"
        # restore
        self.fill_field(self.NAME, original)


class Profile008(ProfileMixin, BaseTest):
    key = "PROFILE_008"
    name = "Email field accepts input"
    description = "Type a new email and verify value."
    category = "Functional"

    def execute(self):
        self.open_profile()
        original = self.current_values()["email"]
        got = self.fill_field(self.EMAIL, "temp@example.com")
        assert got == "temp@example.com", f"Got: '{got}'"
        self.fill_field(self.EMAIL, original)


class Profile009(ProfileMixin, BaseTest):
    key = "PROFILE_009"
    name = "Mobile field accepts input"
    description = "Type a new mobile and verify value."
    category = "Functional"

    def execute(self):
        self.open_profile()
        original = self.current_values()["mobile"]
        got = self.fill_field(self.MOBILE, "01112223333")
        assert got == "01112223333", f"Got: '{got}'"
        self.fill_field(self.MOBILE, original)


# ══════════════════════════════════════════════════════════════
#  PROFILE_010 — Save button label
# ══════════════════════════════════════════════════════════════
class Profile010(ProfileMixin, BaseTest):
    key = "PROFILE_010"; name = "Submit button says Save Changes"; category = "UI"
    description = "Submit value contains 'Save'."
    def execute(self):
        self.open_profile()
        btn = self.driver.find_element(*self.SUBMIT)
        value = btn.get_attribute("value") or ""
        self.slow()
        assert contains_any(value, KEYWORDS["save_button"]), f"Value: '{value}'"


# ══════════════════════════════════════════════════════════════
#  PROFILE_011 — Empty name triggers required error (FIXED)
# ══════════════════════════════════════════════════════════════
class Profile011(ProfileMixin, BaseTest):
    key = "PROFILE_011"
    name = "Empty name triggers 'field is required' error"
    description = "Clearing name and saving shows required-field error."
    category = "Validation"

    def execute(self):
        self.open_profile()
        original = self.current_values()["name"]

        # Clear the name field robustly
        empty_ok = self.fill_field(self.NAME, "")
        assert empty_ok == "", f"Could not clear name field, got: '{empty_ok}'"

        # HTML5 check (in case the field has `required`)
        name_el = self.driver.find_element(*self.NAME)
        html5_invalid = not bool(
            self.js("return arguments[0].checkValidity();", name_el)
        )

        self.click_save()

        # Wait for either a server-side error OR the page not navigating
        err = self.wait_for_error(timeout=12)
        self.slow(0.5)

        # Check if a success message appeared (that would mean the test failed)
        success = self.visible_success_text()

        # Restore original name (best effort)
        try:
            if self.is_alive():
                self.navigate(self.config["profile_url"])
                self.wait.until(EC.presence_of_element_located(self.FORM))
                self.fill_field(self.NAME, original)
                self.click_save()
                self.wait_for_success(timeout=8)
        except Exception:
            pass

        assert not success, \
            f"Form accepted empty name and showed success: '{success}'"

        assert html5_invalid or err, (
            f"Expected name-required error. "
            f"html5_invalid={html5_invalid}, err='{err}', "
            f"url={self.driver.current_url}"
        )


# ══════════════════════════════════════════════════════════════
#  PROFILE_012 — Save unchanged shows success
# ══════════════════════════════════════════════════════════════
class Profile012(ProfileMixin, BaseTest):
    key = "PROFILE_012"
    name = "Saving unchanged data shows success"
    description = "Click Save without changes -> success banner."
    category = "Functional"

    def execute(self):
        self.open_profile()
        self.click_save()
        msg = self.wait_for_success(timeout=15)
        self.slow(0.5)
        assert msg, "No success message after saving"


# ══════════════════════════════════════════════════════════════
#  PROFILE_013 — Update name/mobile shows success
# ══════════════════════════════════════════════════════════════
class Profile013(ProfileMixin, BaseTest):
    key = "PROFILE_013"
    name = "Updating name shows success"
    description = "Change name, save, expect success."
    category = "E2E"

    def execute(self):
        self.open_profile()
        original = self.current_values()

        new_name = (original["name"] or "user").strip() + "X"
        got = self.fill_field(self.NAME, new_name)
        assert got == new_name, f"fill failed: '{got}'"

        self.click_save()
        msg = self.wait_for_success(timeout=15)
        self.slow(0.5)

        # Restore
        try:
            if self.is_alive():
                self.navigate(self.config["profile_url"])
                self.wait.until(EC.presence_of_element_located(self.FORM))
                self.fill_field(self.NAME, original["name"])
                self.click_save()
                self.wait_for_success(timeout=8)
        except Exception:
            pass

        assert msg, "No success message after updating name"


# ══════════════════════════════════════════════════════════════
#  PROFILE_014 — Invalid email rejected (FIXED)
# ══════════════════════════════════════════════════════════════
class Profile014(ProfileMixin, BaseTest):
    key = "PROFILE_014"
    name = "Invalid email format is rejected"
    description = "Type 'abc' as email, save -> email must NOT change."
    category = "Validation"

    def execute(self):
        self.open_profile()
        original = self.current_values()["email"]

        got = self.fill_field(self.EMAIL, "abc")
        assert got == "abc", f"Could not set email to 'abc', got: '{got}'"

        self.click_save()
        err = self.wait_for_error(timeout=10)
        success = self.visible_success_text()
        self.slow(0.5)

        # Reload and check current email
        after_email = original
        try:
            if self.is_alive():
                self.navigate(self.config["profile_url"])
                self.wait.until(EC.presence_of_element_located(self.FORM))
                self.slow(0.4)
                after_email = self.current_values()["email"]
        except Exception:
            pass

        # If the server rejected 'abc', email should still equal the original
        rejected = (after_email == original)

        # Restore (best effort)
        try:
            if self.is_alive() and not rejected:
                self.navigate(self.config["profile_url"])
                self.wait.until(EC.presence_of_element_located(self.FORM))
                self.fill_field(self.EMAIL, original)
                self.click_save()
                self.wait_for_success(timeout=8)
        except Exception:
            pass

        assert rejected or err, (
            f"Server accepted invalid email 'abc'. "
            f"Email after reload: '{after_email}', "
            f"success_msg='{success}', err='{err}'"
        )


# ══════════════════════════════════════════════════════════════
#  PROFILE_015 — File input present
# ══════════════════════════════════════════════════════════════
class Profile015(ProfileMixin, BaseTest):
    key = "PROFILE_015"
    name = "Profile image file input is present"
    description = "input#file-1[name='profile_image'] exists."
    category = "UI"

    def execute(self):
        self.open_profile()
        fi = self.driver.find_element(*self.FILE_INPUT)
        self.slow()
        assert fi.get_attribute("type") == "file"
        assert fi.get_attribute("name") == "profile_image"


# ══════════════════════════════════════════════════════════════
#  PROFILE_016 — Avatar preview on file select
# ══════════════════════════════════════════════════════════════
class Profile016(ProfileMixin, BaseTest):
    key = "PROFILE_016"
    name = "Selecting a file updates the avatar preview"
    description = "Attach av.png -> #blah src becomes a blob: URL."
    category = "UI"

    def execute(self):
        self.open_profile()
        if not AVATAR_PATH.exists():
            raise SkipTest(f"Avatar not found at {AVATAR_PATH}")

        img = self.driver.find_element(*self.AVATAR)
        src_before = img.get_attribute("src") or ""

        self.driver.find_element(*self.FILE_INPUT).send_keys(str(AVATAR_PATH))
        self.slow(1.0)

        src_after = img.get_attribute("src") or ""
        assert src_after and src_after != src_before, \
            "Avatar src did not change after selecting a file"
        assert src_after.startswith("blob:") or src_after.startswith("data:image"), \
            f"Unexpected preview src: '{src_after[:60]}'"


# ══════════════════════════════════════════════════════════════
#  PROFILE_017 — Upload avatar + save
# ══════════════════════════════════════════════════════════════
class Profile017(ProfileMixin, BaseTest):
    key = "PROFILE_017"
    name = "Uploading a new avatar succeeds"
    description = "Attach av.png, save -> success banner."
    category = "E2E"

    def execute(self):
        self.open_profile()
        if not AVATAR_PATH.exists():
            raise SkipTest(f"Avatar not found at {AVATAR_PATH}")

        self.driver.find_element(*self.FILE_INPUT).send_keys(str(AVATAR_PATH))
        self.slow(1.0)
        self.click_save()

        msg = self.wait_for_success(timeout=20)
        self.slow(0.6)
        assert msg, "No success message after uploading avatar"


# ══════════════════════════════════════════════════════════════
#  PROFILE_018 — Name persists after reload (FIXED)
# ══════════════════════════════════════════════════════════════
class Profile018(ProfileMixin, BaseTest):
    key = "PROFILE_018"
    name = "Name value persists after page reload"
    description = "Save unchanged data, reload, name is still present."
    category = "Functional"

    def execute(self):
        self.open_profile()
        original_name = self.current_values()["name"]

        self.click_save()
        self.wait_for_success(timeout=15)
        self.slow(0.5)

        # Guard against the driver having died
        if not self.is_alive():
            raise AssertionError("Browser window died after save; cannot verify reload")

        # Re-navigate instead of refresh() (more reliable across drivers)
        self.navigate(self.config["profile_url"])
        self.dismiss_cookies()
        self.wait.until(EC.presence_of_element_located(self.FORM))
        self.slow(0.5)

        after = self.current_values()["name"]
        assert after.strip() == original_name.strip(), \
            f"Name changed after reload: '{original_name}' -> '{after}'"


# ══════════════════════════════════════════════════════════════
#  PROFILE_019 — Personal Info header visible
# ══════════════════════════════════════════════════════════════
class Profile019(ProfileMixin, BaseTest):
    key = "PROFILE_019"
    name = "Personal Info header is visible"
    description = "The card header shows Personal Info (AR or EN)."
    category = "UI"

    def execute(self):
        self.open_profile()
        header = self.wait.until(EC.presence_of_element_located(self.CARD_HEADER))
        self.js("arguments[0].scrollIntoView({block:'center'});", header)
        self.slow()
        assert header.is_displayed()


# ══════════════════════════════════════════════════════════════
#  PROFILE_020 — Login then /profile works
# ══════════════════════════════════════════════════════════════
class Profile020(ProfileMixin, BaseTest):
    key = "PROFILE_020"
    name = "After login, navigating to /profile works"
    description = "Login, then /profile loads without bounce."
    category = "Auth"

    def execute(self):
        self.navigate(self.config["base_url"])
        self.dismiss_cookies()
        self.slow(0.3)

        # Try /profile — should bounce to /login if not authed
        self.navigate(self.config["profile_url"])
        self.slow(0.5)
        bounced_to_login = "/login" in self.driver.current_url

        if bounced_to_login:
            self.login()

        self.navigate(self.config["profile_url"])
        self.dismiss_cookies()
        self.slow(0.5)

        assert "/login" not in self.driver.current_url, \
            f"Still bounced to login. URL: {self.driver.current_url}"
        self.wait.until(EC.presence_of_element_located(self.FORM))