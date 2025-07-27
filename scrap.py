from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def slow_typing(element, text, delay=0.2):
    """พิมพ์ช้าๆทีละตัวลงในช่อง input"""
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

def get_cost_for(query, max_results=5):
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    driver.get("https://course.mytcas.com/")
    search_box = wait.until(EC.presence_of_element_located((By.ID, "search")))

    # พิมพ์ทีละตัว
    slow_typing(search_box, query)
    time.sleep(1)
    search_box.send_keys(Keys.ENTER)
    time.sleep(3)

    results = []

    # ดึงรายการหลักสูตร
    items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-cy='program-card'] a")))

    for i in range(min(max_results, len(items))):
        try:
            items = driver.find_elements(By.CSS_SELECTOR, "div[data-cy='program-card'] a")
            item = items[i]

            driver.execute_script("arguments[0].scrollIntoView();", item)
            driver.execute_script("arguments[0].click();", item)
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            title = soup.find("h2").text.strip()

            cost_section = soup.find(lambda tag: tag.name in ["div", "p", "span"] and "ค่าใช้จ่าย" in tag.text)
            cost_text = cost_section.text.strip() if cost_section else "ไม่พบข้อมูล"

            results.append({"title": title, "cost": cost_text})

            driver.back()
            time.sleep(2)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดกับรายการที่ {i+1}: {e}")
            continue

    driver.quit()
    return results


# ทดสอบ
if __name__ == "__main__":
    data = get_cost_for("วิศวกรรม ปัญญาประดิษฐ์", max_results=10)
    
    # บันทึก Excel
    df = pd.DataFrame(data)
    df.to_excel("ai_engineering_fees.xlsx", index=False)
    
    for d in data:
        print(f"{d['title']} → {d['cost']}")
