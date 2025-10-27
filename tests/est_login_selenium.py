import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# ---- Chrome Options ----
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)
BASE_URL = "http://localhost:5173"

# ---- Default credentials ----
default_username = "superuser"
default_password = "superuser"

# ---- Login ----
try:
    driver.get(BASE_URL)
    print(f"Using username: {default_username}")
    print(f"Using password: {default_password}")

    username_input = driver.find_element(By.ID, "username")
    username_input.clear()
    username_input.send_keys(default_username)

    password_input = driver.find_element(By.ID, "password")
    password_input.clear()
    password_input.send_keys(default_password)

    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    wait.until(EC.url_contains("dashboard"))
    print("✅ Login successful — redirected to dashboard.")

except Exception as e:
    print(f"⚠️ Login error: {e}")

time.sleep(2)

# ---- Add Category ----
try:
    driver.get(BASE_URL + "/stocks")
    add_category_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add Category')]"))
    )
    add_category_btn.click()
    print("🖱️ Clicked 'Add Category'")

    category_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter category name']"))
    )
    category_input.clear()
    category_input.send_keys("paints")

    save_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    save_button.click()

    # Check for duplicate
    try:
        duplicate_alert = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'already exists')]"))
        )
        print("⚠️ Category already exists.")
    except:
        print("✅ Category added successfully!")

    time.sleep(2)

except Exception as e:
    print(f"❌ Error adding category: {e}")

# ---- Add Product ----
try:
    add_product_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add Product')]"))
    )
    add_product_btn.click()
    print("🖱️ Clicked 'Add Product'")

    # Product Name
    product_name_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter product name']"))
    )
    product_name_input.clear()
    product_name_input.send_keys("Acrylic Paint Set")

    # Category Select
    category_select_elem = wait.until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='category-dropdown']/select"))
    )
    Select(category_select_elem).select_by_visible_text("paints")

    # Supplier Select
    supplier_select_elem = driver.find_element(By.XPATH, "//div[label[contains(text(),'Supplier')]]/select")
    Select(supplier_select_elem).select_by_visible_text("test")

    # Wait until the Base Unit select is clickable
    base_unit_div = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[label[contains(text(),'Base Unit')]]/select"))
    )

    # Click to open the dropdown (sometimes optional for native select)
    driver.execute_script("arguments[0].scrollIntoView(true);", base_unit_div)
    time.sleep(0.5)

    # Choose the first real option (skip "Select Unit")
    options = base_unit_div.find_elements(By.TAG_NAME, "option")
    for option in options:
        if option.get_attribute("value") != "":
            option.click()
            print(f"✅ Selected Base Unit: {option.text}")
            pass
    
    # Optional Serial Number
    serial_number_input = driver.find_element(By.XPATH, "//input[@placeholder='Serial number (optional)']")
    serial_number_input.send_keys("SN-001")

    # Number Fields
    stock_input = driver.find_element(By.XPATH, "//label[@id='stock_quantity']/following-sibling::input")
    stock_input.send_keys("50")

    cost_input = driver.find_element(By.XPATH, "//label[@id='cost_price']/following-sibling::input")
    cost_input.send_keys("15")

    margin_input = driver.find_element(By.XPATH, "//label[@id='margin']/following-sibling::input")
    margin_input.send_keys("10")


    # Wait for the Add Product modal to appear
    modal = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//div[contains(@class,'rounded-2xl') and .//h3[contains(text(),'Add New Product')]]")
    ))

    # Find the 'Create Product' button inside this modal
    create_product_btn = modal.find_element(By.XPATH, ".//button[contains(text(),'Create Product')]")

    # Scroll it into view
    driver.execute_script("arguments[0].scrollIntoView(true);", create_product_btn)
    time.sleep(0.5)

    # Click using JavaScript to bypass 'not interactable' issues
    driver.execute_script("arguments[0].click();", create_product_btn)

    print("✅ Product added successfully!")

except Exception as e:
    print(f"❌ Error adding product: {e}")

time.sleep(3)
driver.quit()
