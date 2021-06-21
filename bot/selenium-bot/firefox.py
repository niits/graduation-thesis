import time

from selenium import webdriver

driver = webdriver.Firefox()
driver.get("http://165.22.253.247/")

print(driver.title)
time.sleep(3)
driver.close()
