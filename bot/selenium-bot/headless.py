import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(
    "user-agent=[Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36]"
)
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--profile-directory=Default")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-plugins-discovery")
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get("http://localhost:5000/")
el = driver.find_element_by_tag_name("body")
print(el.text)
time.sleep(3)
driver.close()
