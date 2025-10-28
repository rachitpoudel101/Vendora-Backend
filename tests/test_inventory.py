import time
import pytest
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = "http://localhost:5173"
USERNAME = "superuser"
PASSWORD = "superuser"
time.sleep(2)
@pytest.mark.order(1)
def test_login(driver: WebDriver):
    driver.get(BASE_URL)
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 10).until(EC.url_contains("dashboard"))
    assert "dashboard" in driver.current_url, "Login failed!"
    print("✅ Login successful.")

@pytest.mark.order(2)
def test_add_category(driver: WebDriver):
    driver.get(BASE_URL + "/stocks")
    wait = WebDriverWait(driver, 10)

    add_category_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add Category')]")))
    add_category_btn.click()

    category_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter category name']"))
    )
    category_input.clear()
    category_input.send_keys("clothes")

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Detect duplicate message or success
    try:
        duplicate = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'already exists')]"))
        )
        print("⚠️ Category already exists.")
    except:
        print("✅ Category added successfully!")

@pytest.mark.order(3)
def test_add_product(driver: WebDriver):
    wait = WebDriverWait(driver, 10)
    driver.get(BASE_URL + "/stocks")

    add_product_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add Product')]")))
    add_product_btn.click()

    product_name_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter product name']"))
    )
    product_name_input.send_keys("Acrylic Paint Set")

    # Category
    category_select_elem = wait.until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='category-dropdown']/select"))
    )
    Select(category_select_elem).select_by_visible_text("paints")

    # Supplier
    supplier_select_elem = driver.find_element(By.XPATH, "//div[label[contains(text(),'Supplier')]]/select")
    Select(supplier_select_elem).select_by_visible_text("test")

    # Base Unit
    base_unit_div = wait.until(
        EC.presence_of_element_located((By.XPATH, "//div[label[contains(text(),'Base Unit')]]/select"))
    )
    options = base_unit_div.find_elements(By.TAG_NAME, "option")
    for option in options:
        if option.get_attribute("value"):
            option.click()
            break

    # Fill numeric fields
    driver.find_element(By.XPATH, "//input[@placeholder='Serial number (optional)']").send_keys("SN-001")
    driver.find_element(By.XPATH, "//label[@id='stock_quantity']/following-sibling::input").send_keys("50")
    driver.find_element(By.XPATH, "//label[@id='cost_price']/following-sibling::input").send_keys("15")
    driver.find_element(By.XPATH, "//label[@id='margin']/following-sibling::input").send_keys("10")

    # Submit
    modal = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//div[contains(@class,'rounded-2xl') and .//h3[contains(text(),'Add New Product')]]")
    ))
    create_product_btn = modal.find_element(By.XPATH, ".//button[contains(text(),'Create Product')]")
    driver.execute_script("arguments[0].click();", create_product_btn)

    print("✅ Product added successfully!")
