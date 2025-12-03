from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(
        ChromeDriverManager().install(),
        options=opts
    )

def test_login_page_title_contains_login():
    driver = create_driver()
    driver.get("https://the-internet.herokuapp.com/login")
    assert "Login" in driver.title
    driver.quit()
