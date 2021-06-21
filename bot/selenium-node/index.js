const {Builder, By, Key, until} = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const firefox = require('selenium-webdriver/firefox');

(async function example() {
  let driver = await new Builder().forBrowser('firefox').setFirefoxOptions(new firefox.Options().headless())
  .build();
  try {
    await driver.get('http://localhost:5000/');
    await driver.wait(until.titleIs('webdriver - Google Search'), 5000);
  } finally {
    await driver.quit();
  }
})();