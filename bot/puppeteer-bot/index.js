// https://codeburst.io/a-guide-to-automating-scraping-the-web-with-javascript-chrome-puppeteer-node-js-b18efb9e9921

const puppeteer = require("puppeteer");
const { createCursor } = require("ghost-cursor")

let scrape = async() => {
    const args = [
        '--user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"',
    ];

    const options = {
        args,
        headless: true,
        ignoreHTTPSErrors: true,
        userDataDir: "./tmp",
    };

    const browser = await puppeteer.launch(options);
    const page = await browser.newPage();
    for (i = 0; i < 50; i++) {
        var duration = Math.floor(Math.random() * 300) + 1; // b/w 1 and 6
        setTimeout(function() {}, duration);

        await page.goto("http://localhost:5000/landing_page?predetermined=bot");
        await page.waitFor(1000 + Math.random() * 2000);
        const cursor = createCursor(page)
        await cursor.click("button#button");
    }
    browser.close();
    return i;
};

scrape().then((value) => {
    console.log(JSON.stringify(value, null, 4));
});