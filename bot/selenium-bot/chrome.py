import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument(
    "user-agent=[Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36]"
)


driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get("http://localhost:5000/")
time.sleep(3)
driver.close()
