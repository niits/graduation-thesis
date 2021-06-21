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
        var zoneid = Math.floor(Math.random() * 8) + 1; // b/w 1 and 6

        await page.goto(`https://165.232.166.107/landing_page/shop?predetermined=bot&zoneid=${zoneid}`);
        var duration = Math.floor(Math.random() * 6) + 1; // b/w 1 and 6
        setTimeout(function() {}, duration);
        const elHandleArray = await page.$$('a.add_to_cart_button')

        const target_id = Math.floor(Math.random() * elHandleArray.length);
        const target = elHandleArray[target_id]
        const cursor = createCursor(page);

        const steps = Math.random() * 10 + 3
        console.log(steps)
        for (j = 0; j < steps; j++) {
            var to = elHandleArray[Math.floor(Math.random() * elHandleArray.length)]
            var { x, y, width, height } = await to.boundingBox();
            await cursor.moveTo({
                x: x + Math.floor(Math.random() * width),
                y: y + Math.floor(Math.random() * height),
            });
        }
        var { x, y, width, height } = await target.boundingBox();

        await cursor.moveTo({
            x: x + Math.floor(Math.random() * width),
            y: y + Math.floor(Math.random() * height),
        });

        await target.click({
            delay: Math.floor(Math.random() * 200)
        })
        browser.close();
    }
    return i;
};

scrape().then((value) => {
    console.log(JSON.stringify(value, null, 4));
});