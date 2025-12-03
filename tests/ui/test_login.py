# tests/ui/test_login.py

import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

UI_BASE_URL = os.getenv("UI_BASE_URL", "https://the-internet.herokuapp.com")

def create_driver():
    """Create a Chrome WebDriver that works both locally and in Jenkins.

    - If SELENIUM_REMOTE_URL is set => use RemoteWebDriver (Selenium docker).
    - Otherwise => use local Chrome via Selenium Manager.
    """
    opts = Options()

    # Headless in CI by default
    if os.getenv("CI", "false").lower() == "true":
        opts.add_argument("--headless=new")

    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    remote_url = os.getenv("SELENIUM_REMOTE_URL")

    if remote_url:
        # Use Selenium grid / standalone-chrome container
        return webdriver.Remote(
            command_executor=remote_url,
            options=opts,
        )
    else:
        # Local Chrome (Selenium Manager will download chromedriver automatically)
        return webdriver.Chrome(options=opts)


def test_login_page_title_contains_login():
    """Verify that the login page title contains the word 'Login'."""
    driver = create_driver()
    try:
        driver.get(f"{UI_BASE_URL}/login")
        assert "Login" in driver.title
    finally:
        driver.quit()


def test_login_form_has_username_and_password_fields():
    """Verify login form contains username and password fields."""
    driver = create_driver()
    try:
        driver.get(f"{UI_BASE_URL}/login")

        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password")

        assert username is not None
        assert password is not None
    finally:
        driver.quit()
