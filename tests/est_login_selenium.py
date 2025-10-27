# tests/test_login_selenium.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
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

# ---- Default credentials (fallback) ----
default_username = "superuser"
default_password = "superuser"

try:
    time.sleep(5)
    # ---- Open login page ----
    driver.get("http://localhost:5173/")  # Update with your URL

    print(f"Using username: {default_username}")
    print(f"Using password: {default_password}")

    # ---- Find login input fields ----
    try:
        username_input = driver.find_element(By.NAME, "username")
    except:
        username_input = driver.find_element(By.ID, "username")

    try:
        password_input = driver.find_element(By.NAME, "password")
    except:
        password_input = driver.find_element(By.ID, "password")

    # ---- Enter credentials ----
    username_input.clear()
    username_input.send_keys(default_username)
    password_input.clear()
    password_input.send_keys(default_password)

    # ---- Click Login button ----
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    # ---- Wait for dashboard ----
    try:
        wait.until(EC.url_contains("dashboard"))
        print("✅ Login successful — redirected to dashboard.")
    except:
        dashboard_heading = driver.find_elements(By.XPATH, "//h1[contains(text(), 'Dashboard')]")
        if dashboard_heading:
            print("✅ Login successful — dashboard element visible.")
        else:
            print("❌ Login failed — check credentials or selectors.")

except Exception as e:
    print(f"⚠️ Test error: {e}")
time.sleep(2)

# --- Navigate to Stocks page if redirected elsewhere ---
driver.get("http://localhost:5173/stocks")
time.sleep(5)
try:
    add_category_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Add Category')]"))
    )
    add_category_button.click()
    print("🖱️ Clicked 'Add Category'")

    # Wait for popup form
    category_name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter category name']"))
    )
    description_input = driver.find_element(By.XPATH, "//textarea[@placeholder='Enter category description']")

    # --- Fill form ---
    category_name_input.send_keys("paints")
    description_input.send_keys("Devices and gadgets")

    # --- Submit form ---
    save_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    save_button.click()

    print("✅ Category added successfully!")
    time.sleep(6)

except Exception as e:
    print(f"❌ Error while adding category: {e}")
time.sleep(5)
driver.quit()