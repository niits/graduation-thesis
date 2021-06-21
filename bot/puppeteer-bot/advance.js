// https://codeburst.io/a-guide-to-automating-scraping-the-web-with-javascript-chrome-puppeteer-node-js-b18efb9e9921

const puppeteer = require("puppeteer");
const { createCursor, path } = require("ghost-cursor");

let scrape = async() => {
    const args = [
        '--user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"',
        "--window-size=1920,1080",
    ];

    const options = {
        args,
        headless: true,
        ignoreHTTPSErrors: true,
        userDataDir: "./tmp",
    };

    for (i = 0; i < 2500; i++) {
        console.log(`Lần thứ ${i+1}`)

        const browser = await puppeteer.launch(options);
        const page = await browser.newPage();

        var duration = Math.floor(Math.random() * 6) + 1; // b/w 1 and 6
        setTimeout(function() {}, duration);
        var zoneid = Math.floor(Math.random() * 8) + 1; // b/w 1 and 6

        await page.goto(`http://localhost:5000/landing_page/?predetermined=bot&zoneid=${zoneid}`);
        await page.waitFor(3000 + Math.random() * 3000);
        const cursor = createCursor(page);

        for (j = 0; j < Math.floor(Math.random() * 4); j++) {
            var to = {
                x: Math.floor(Math.random() * 1920),
                y: Math.floor(Math.random() * 1080),
            };

            await cursor.moveTo(to);
        }
        await cursor.click("button#button");
        console.log(new Date().toLocaleString());
        browser.close();
    }
    return i;
};

scrape().then((value) => {
    console.log(JSON.stringify(value, null, 4));
});