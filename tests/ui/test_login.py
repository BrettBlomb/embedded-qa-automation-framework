# tests/ui/test_login.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from framework.config import get_selenium_base_url

def test_login_page_title_contains_login():
    """Verify that the login page title contains the word 'Login'."""
    driver = webdriver.Chrome()  # Jenkins node will need chromedriver
    try:
        driver.get(get_selenium_base_url() + "/login")
        assert "Login" in driver.title
    finally:
        driver.quit()

def test_login_form_has_username_and_password_fields():
    """Verify login form contains username and password fields."""
    driver = webdriver.Chrome()
    try:
        driver.get(get_selenium_base_url() + "/login")
        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        assert username.is_displayed()
        assert password.is_displayed()
    finally:
        driver.quit()
