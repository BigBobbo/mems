import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def browser():
    driver = webdriver.Firefox()  # or webdriver.Chrome()
    yield driver
    driver.quit()

def test_create_memorial_e2e(browser, live_server):
    """Test creating a memorial end-to-end"""
    # Go to login page
    browser.get(f'{live_server.url}/auth/login')
    
    # Login
    browser.find_element(By.NAME, 'email').send_keys('test@example.com')
    browser.find_element(By.NAME, 'password').send_keys('password123')
    browser.find_element(By.TAG_NAME, 'form').submit()
    
    # Go to create memorial page
    browser.get(f'{live_server.url}/create')
    
    # Fill out form
    browser.find_element(By.NAME, 'name').send_keys('E2E Test Memorial')
    browser.find_element(By.NAME, 'birth_date').send_keys('1960-01-01')
    browser.find_element(By.NAME, 'death_date').send_keys('2021-01-01')
    browser.find_element(By.NAME, 'biography').send_keys('E2E test biography')
    browser.find_element(By.TAG_NAME, 'form').submit()
    
    # Wait for redirect and check result
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'h1'))
    )
    assert 'E2E Test Memorial' in browser.page_source 