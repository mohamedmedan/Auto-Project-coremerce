from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def create_driver(browser="chrome", headless=False, implicit_wait=5):
    browser = (browser or "chrome").lower()
    if browser == "chrome":
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-notifications")
        opts.add_argument("--disable-popup-blocking")
        opts.add_argument("--disable-infobars")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        if headless:
            opts.add_argument("--headless=new")
            opts.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=opts,
        )
    elif browser == "firefox":
        opts = FirefoxOptions()
        if headless:
            opts.add_argument("-headless")
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=opts,
        )
    elif browser == "edge":
        opts = EdgeOptions()
        if headless:
            opts.add_argument("--headless=new")
        driver = webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()),
            options=opts,
        )
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    driver.implicitly_wait(implicit_wait)
    return driver
