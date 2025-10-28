import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# ---------- GLOBAL CONFIG ----------
BASE_URL = "http://localhost:5173"
DEFAULT_USERNAME = "superuser"
DEFAULT_PASSWORD = "superuser"

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)


# ---------- FUNCTION DEFINITIONS ----------
def login(username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD):
    """Logs into the system using given credentials."""
    try:
        driver.get(BASE_URL)
        time.sleep(2)  # wait for page load
        print(f"🔐 Logging in as: {username}")

        username_input = driver.find_element(By.ID, "username")
        username_input.clear()
        username_input.send_keys(username)

        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(password)

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("dashboard"))
        time.sleep(2)  # wait for dashboard to load

        print("✅ Login successful — redirected to dashboard.\n")
        return True

    except Exception as e:
        print(f"⚠️ Login error: {e}\n")
        return False


def add_category(category_name="paints"):
    """Adds a new category. Handles duplicate detection."""
    try:
        driver.get(BASE_URL + "/stocks")
        time.sleep(2)  # wait for page load

        add_category_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add Category')]"))
        )
        add_category_btn.click()
        time.sleep(1)
        print("🖱️ Clicked 'Add Category'")

        category_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter category name']"))
        )
        category_input.clear()
        category_input.send_keys(category_name)
        time.sleep(0.5)

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

        # Check duplicate
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'already exists')]"))
            )
            print(f"⚠️ Category '{category_name}' already exists.\n")
        except:
            print(f"✅ Category '{category_name}' added successfully!\n")

    except Exception as e:
        print(f"❌ Error adding category: {e}\n")


def select_base_unit(base_unit_name="Piece"):
    """Selects the Base Unit by name, or falls back to first available option if not found."""
    try:
        base_unit_elem = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[label[contains(text(),'Base Unit')]]/select"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", base_unit_elem)
        time.sleep(0.5)

        options = base_unit_elem.find_elements(By.TAG_NAME, "option")
        selected = False

        for option in options:
            if option.text.strip() == base_unit_name:
                option.click()
                print(f"✅ Selected Base Unit: {option.text}")
                selected = True
                break

        if not selected:
            for option in options:
                if option.get_attribute("value") != "":
                    option.click()
                    print(f"⚠️ Base Unit '{base_unit_name}' not found — fallback selected: {option.text}")
                    break
        time.sleep(0.5)

    except Exception as e:
        print(f"❌ Error selecting Base Unit: {e}")


def add_product(product_name="Acrylic Paint Set", category_name="paints", supplier_name="test"):
    """Adds a new product under the given category."""
    try:
        driver.get(BASE_URL + "/stocks")
        time.sleep(2)  # wait for page load

        add_product_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add Product')]"))
        )
        add_product_btn.click()
        time.sleep(1)
        print("🖱️ Clicked 'Add Product'")

        product_name_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter product name']"))
        )
        product_name_input.clear()
        product_name_input.send_keys(product_name)
        time.sleep(0.5)

        # Category
        category_select_elem = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='category-dropdown']/select"))
        )
        Select(category_select_elem).select_by_visible_text(category_name)
        time.sleep(0.5)

        # Supplier
        supplier_select_elem = driver.find_element(By.XPATH, "//div[label[contains(text(),'Supplier')]]/select")
        Select(supplier_select_elem).select_by_visible_text(supplier_name)
        time.sleep(0.5)

        # Base Unit
        select_base_unit("Piece")

        # Serial, Stock, Cost, Margin
        driver.find_element(By.XPATH, "//input[@placeholder='Serial number (optional)']").send_keys("SN-001")
        driver.find_element(By.XPATH, "//label[@id='stock_quantity']/following-sibling::input").send_keys("50")
        driver.find_element(By.XPATH, "//label[@id='cost_price']/following-sibling::input").send_keys("15")
        driver.find_element(By.XPATH, "//label[@id='margin']/following-sibling::input").send_keys("10")
        time.sleep(0.5)

        modal = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class,'rounded-2xl') and .//h3[contains(text(),'Add New Product')]]")
        ))
        create_btn = modal.find_element(By.XPATH, ".//button[contains(text(),'Create Product')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", create_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", create_btn)
        time.sleep(1)

        print(f"✅ Product '{product_name}' added successfully!\n")

    except Exception as e:
        print(f"❌ Error adding product: {e}\n")


def close_browser():
    """Closes the browser."""
    print("🧹 Closing browser...")
    driver.quit()


# ---------- MAIN EXECUTION ----------
if __name__ == "__main__":
    if login():
        add_category("paints")
        add_product("Acrylic Paint Set", "paints", "test")
    close_browser()
