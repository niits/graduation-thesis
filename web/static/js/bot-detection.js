(function (name, context, definition) {
    "use strict";
    if (
        typeof window !== "undefined" &&
        typeof window.define === "function" &&
        window.define.amd
    ) {
        window.define(definition);
    } else if (typeof module !== "undefined" && module.exports) {
        module.exports = definition();
    } else if (context.exports) {
        context.exports = definition();
    } else {
        context[name] = definition();
    }
})("BotDetection", this, function () {

    var hash_id = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0,
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
    const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

    let mouseEvents = [];
    let lastButtonState = 0;
    let lastScrollState = document.scrollY;
    document.addEventListener("mousedown", (e) => {
        const getMouseButtonEvent = (buttons) => {
            switch (buttons) {
                case 0:
                    return "UNDEFINED";
                case 1:
                    return "LEFT_DOWN";
                case 2:
                    return "RIGHT_DOWN";
                case 3:
                    return "LEFT_RIGHT_DOWN";
                case 4:
                    return "SCROLL_PUSH";
            }
        };
        lastButtonState = e.buttons;
        const singleMouseEvent = {
            x_client: e.clientX,
            y_client: e.clientY,
            event: getMouseButtonEvent(lastButtonState),
            timestamp: (new Date()).toISOString(),
            x_window: window.screen.width,
            y_window: window.screen.height,
        };
        mouseEvents.push(singleMouseEvent);
    });

    document.addEventListener("mouseup", (e) => {
        const getMouseButtonEvent = () => {
            switch (lastButtonState) {
                case 0:
                    return "UNDEFINED";
                case 1:
                    return "LEFT_UP";
                case 2:
                    return "RIGHT_UP"; // TODO: problem detecting RIGHT_UP due to contextmenu pop-up
                case 3:
                    return "LEFT_RIGHT_UP";
                case 4:
                    return "SCROLL_PULL";
            }
            lastButtonState = 0;
        };

        const clickEvent = {
            x_client: e.clientX,
            y_client: e.clientY,
            x_window: window.screen.width,
            y_window: window.screen.height,
            timestamp: (new Date()).toISOString(),
            event: getMouseButtonEvent(),
        };
        mouseEvents.push(clickEvent);
    });

    document.addEventListener("wheel", (e) => {
        const singleScrollEvent = {
            x_client: e.clientX,
            y_client: e.clientY,
            event: lastScrollState > window.scrollY ? "SCROLL_UP" : "SCROLL_DOWN",
            timestamp: (new Date()).toISOString(),
            x_window: window.screen.width,
            y_window: window.screen.height,
        };
        mouseEvents.push(singleScrollEvent);
        lastScrollState = window.scrollY;
    });

    document.addEventListener("mousemove", (e) => {
        const mouseMoveEvent = {
            x_client: e.clientX,
            y_client: e.clientY,
            event: "MOVE",
            timestamp: (new Date()).toISOString(),
            x_window: window.screen.width,
            y_window: window.screen.height,
        };
        mouseEvents.push(mouseMoveEvent);
    });

    function get_param (param_name) {
        var result = null;
        location.search
            .substr(1)
            .split("&")
            .forEach(function (item) {
                item = decodeURIComponent(item).replace('\"', '').replace('\'', '')
                tmp = item.split("=");
                if (tmp.length > 0 && tmp[0] === param_name) result = decodeURIComponent(tmp[1]);
            });
            return result;
        }

    function sendData(tracking_param_name, data_storage_address) {
        if (mouseEvents.length !== 0) {
            const data = mouseEvents;

            var xhr = new XMLHttpRequest();

            xhr.open("POST", data_storage_address + "/data/mouse_events", true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(
                JSON.stringify({
                    data: {
                        events: data,
                        tracking_code: get_param(tracking_param_name),
                        hash_id,
                        path: window.location.origin,
                        predetermined: get_param('predetermined') !== null ? get_param('predetermined') : 'not_predicted',
                        zone_id: get_param('zone_id') !== null ? get_param('zone_id') : Math.floor(Math.random() * 9) + 1,
                    },
                })
            );
            mouseEvents = [];
        }
        wait(200).then(sendData.bind(null, tracking_param_name, data_storage_address));
    };

    function traverseAndFlatten(currentNode, target, flattenedKey) {
        for (var key in currentNode) {
            if (currentNode.hasOwnProperty(key)) {
                var newKey;
                if (flattenedKey === undefined) {
                    newKey = key;
                } else {
                    newKey = flattenedKey + "." + key;
                }

                var value = currentNode[key];
                if (typeof value === "object") {
                    traverseAndFlatten(value, target, newKey);
                } else {
                    target[newKey] = value;
                }
            }
        }
    }

    function flatten(obj) {
        var flattenedObject = {};
        traverseAndFlatten(obj, flattenedObject);
        return flattenedObject;
    }

    function getBrownerName() {
        var isOpera =
            (!!window.opr && !!opr.addons) ||
            !!window.opera ||
            navigator.userAgent.indexOf(" OPR/") >= 0;

        // Firefox 1.0+
        var isFirefox = typeof InstallTrigger !== "undefined";

        // Safari 3.0+ "[object HTMLElementConstructor]"
        var isSafari =
            /constructor/i.test(window.HTMLElement) ||
            (function (p) {
                return p.toString() === "[object SafariRemoteNotification]";
            })(!window["safari"] ||
                (typeof safari !== "undefined" && window["safari"].pushNotification)
            );

        // Internet Explorer 6-11
        var isIE = /*@cc_on!@*/ false || !!document.documentMode;

        // Edge 20+
        var isEdge = !isIE && !!window.StyleMedia;

        // Chrome 1 - 79
        var isChrome = !!window.chrome && (!!window.chrome.webstore || !!window.chrome.runtime);

        // Edge (based on chromium) detection
        var isEdgeChromium = isChrome && navigator.userAgent.indexOf("Edg") != -1;

        // Blink engine detection
        var isBlink = (isChrome || isOpera) && !!window.CSS;
        return {
            Opera: isOpera,
            Firefox: isFirefox,
            Safari: isSafari,
            Edge: isEdge,
            IE: isIE,
            Chrome: isChrome,
            EdgeChromium: isEdgeChromium,
            Blink: isBlink,
        };
    }

    function getFingerprint() {
        return {
            exist: {
                general: {
                    webgl: (function () {
                        var canvas = document.createElement("canvas");
                        var gl = canvas.getContext("webgl");

                        var debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
                        var vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                        var renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);

                        return vendor == "Brian Paul" && renderer == "Mesa OffScreen";
                    })(),
                    notification: (function () {
                        navigator.permissions
                            .query({
                                name: "notifications",
                            })
                            .then(function (permissionStatus) {
                                return (
                                    Notification.permission === "denied" &&
                                    permissionStatus.state === "prompt"
                                );
                            });
                    })(navigator),
                    image: (function () {
                        var detected = false;
                        var body = document.getElementsByTagName("body")[0];
                        var image = document.createElement("img");
                        image.src = "static/img/a.png";
                        body.appendChild(image);
                        image.onerror = function () {
                            detected = image.width === 0 && image.height === 0;
                        };
                        image.remove();
                        return detected;
                    })(document),
                    window: {
                        missing_outer_width: !window.outerWidth,
                        missing_outer_height: !window.outerHeight,
                    },
                    navigator: {
                        missing_onLine: !navigator.onLine,
                        empty_plugins: getBrownerName()["Chrome"] && navigator.plugins.length == 0,
                    },
                    Function: {
                        missing_bind: !Function.prototype.bind,
                        toString: {
                            bind: Function.prototype.bind.toString().replace(/bind/g, "Error") !=
                                Error.toString(),
                            toString: Function.prototype.toString
                                .toString()
                                .replace(/toString/g, "Error") != Error.toString(),
                        },
                    },
                },
                phantom: {
                    user_agent: navigator.userAgent.toLowerCase().includes("phantom"),
                    _phantom: window._phantom == true,
                    callPhantom: window.callPhantom == true,
                    __phantomas: window.__phantomas == true,
                },
                selenium: {
                    webdriver: "webdriver" in window,
                    _Selenium_IDE_Recorder: "_Selenium_IDE_Recorder" in window,
                    callSelenium: "callSelenium" in window,
                    _selenium: "_selenium" in window,
                    __webdriver_script_fn: "__webdriver_script_fn" in document,
                    __driver_evaluate: "__driver_evaluate" in document,
                    __webdriver_evaluate: "__webdriver_evaluate" in document,
                    __selenium_evaluate: "__selenium_evaluate" in document,
                    __fxdriver_evaluate: "__fxdriver_evaluate" in document,
                    __driver_unwrapped: "__driver_unwrapped" in document,
                    __webdriver_unwrapped: "__webdriver_unwrapped" in document,
                    __selenium_unwrapped: "__selenium_unwrapped" in document,
                    __fxdriver_unwrapped: "__fxdriver_unwrapped" in document,
                    __webdriver_script_func: "__webdriver_script_func" in document,
                    selenium: document.documentElement.getAttribute("selenium") !== null,
                    webdriver: document.documentElement.getAttribute("webdriver") !== null,
                    driver: document.documentElement.getAttribute("driver") !== null,
                },
                webdriver: {
                    webdriver: "webdriver" in window || navigator.webdriver,
                    __webdriver_script_fn: "__webdriver_script_fn" in document,
                    __driver_evaluate: "__driver_evaluate" in document,
                    __webdriver_evaluate: "__webdriver_evaluate" in document,
                    __fxdriver_evaluate: "__fxdriver_evaluate" in document,
                    __driver_unwrapped: "__driver_unwrapped" in document,
                    __webdriver_unwrapped: "__webdriver_unwrapped" in document,
                    __fxdriver_unwrapped: "__fxdriver_unwrapped" in document,
                    __webdriver_script_func: "__webdriver_script_func" in document,
                    document_webdriver: document.documentElement.getAttribute("webdriver") !== null,
                    document_driver: document.documentElement.getAttribute("driver") !== null,
                    window_document_webdriver: window.document.documentElement.getAttribute("webdriver") !== null,
                },
                headless_chrome: {
                    domAutomation: window.domAutomation,
                    navigator: {
                        user_agent: navigator.userAgent
                            .toLowerCase()
                            .includes("headlesschrome"),
                        missing_window_chrome: getBrownerName()["Chrome"] && window.chrome == null,
                    },
                    $dc_key: (function () {
                        for (const documentKey in window["document"]) {
                            if (
                                documentKey.match(/\$[a-z]dc_/) &&
                                window["document"][documentKey]["cache_"]
                            ) {
                                return true;
                            }
                        }
                    })(window),
                    window_external: window["external"] &&
                        window["external"].toString() &&
                        window["external"].toString()["indexOf"]("Sequentum") != -1,
                },
            },
            userAgent: navigator.userAgent,
            inconsistencyLanguages: (function () {
                if (typeof navigator.languages !== "undefined") {
                    try {
                        var firstLanguages = navigator.languages[0].substr(0, 2);
                        if (firstLanguages !== navigator.language.substr(0, 2)) {
                            return true;
                        }
                    } catch (err) {
                        return true;
                    }
                }
                return false;
            })(),
            inconsistencyResolution: (function () {
                return (
                    window.screen.width < window.screen.availWidth ||
                    window.screen.height < window.screen.availHeight
                );
            })(),
            inconsistencyOs: (function () {
                var userAgent = navigator.userAgent.toLowerCase();
                var oscpu = navigator.oscpu;
                var platform = navigator.platform.toLowerCase();
                var os;
                if (userAgent.indexOf("windows phone") >= 0) {
                    os = "Windows Phone";
                } else if (
                    userAgent.indexOf("windows") >= 0 ||
                    userAgent.indexOf("win16") >= 0 ||
                    userAgent.indexOf("win32") >= 0 ||
                    userAgent.indexOf("win64") >= 0 ||
                    userAgent.indexOf("win95") >= 0 ||
                    userAgent.indexOf("win98") >= 0 ||
                    userAgent.indexOf("winnt") >= 0 ||
                    userAgent.indexOf("wow64") >= 0
                ) {
                    os = "Windows";
                } else if (userAgent.indexOf("android") >= 0) {
                    os = "Android";
                } else if (
                    userAgent.indexOf("linux") >= 0 ||
                    userAgent.indexOf("cros") >= 0 ||
                    userAgent.indexOf("x11") >= 0
                ) {
                    os = "Linux";
                } else if (
                    userAgent.indexOf("iphone") >= 0 ||
                    userAgent.indexOf("ipad") >= 0 ||
                    userAgent.indexOf("ipod") >= 0 ||
                    userAgent.indexOf("crios") >= 0 ||
                    userAgent.indexOf("fxios") >= 0
                ) {
                    os = "iOS";
                } else if (
                    userAgent.indexOf("macintosh") >= 0 ||
                    userAgent.indexOf("mac_powerpc)") >= 0
                ) {
                    os = "Mac";
                } else {
                    os = "Other";
                }
                // We detect if the person uses a touch device
                var mobileDevice =
                    "ontouchstart" in window ||
                    navigator.maxTouchPoints > 0 ||
                    navigator.msMaxTouchPoints > 0;

                if (
                    mobileDevice &&
                    os !== "Windows" &&
                    os !== "Windows Phone" &&
                    os !== "Android" &&
                    os !== "iOS" &&
                    os !== "Other" &&
                    userAgent.indexOf("cros") === -1
                ) {
                    return true;
                }

                // We compare oscpu with the OS extracted from the UA
                if (typeof oscpu !== "undefined") {
                    oscpu = oscpu.toLowerCase();
                    if (
                        oscpu.indexOf("win") >= 0 &&
                        os !== "Windows" &&
                        os !== "Windows Phone"
                    ) {
                        return true;
                    } else if (
                        oscpu.indexOf("linux") >= 0 &&
                        os !== "Linux" &&
                        os !== "Android"
                    ) {
                        return true;
                    } else if (oscpu.indexOf("mac") >= 0 && os !== "Mac" && os !== "iOS") {
                        return true;
                    } else if (
                        (oscpu.indexOf("win") === -1 &&
                            oscpu.indexOf("linux") === -1 &&
                            oscpu.indexOf("mac") === -1) !==
                        (os === "Other")
                    ) {
                        return true;
                    }
                }

                // We compare platform with the OS extracted from the UA
                if (
                    platform.indexOf("win") >= 0 &&
                    os !== "Windows" &&
                    os !== "Windows Phone"
                ) {
                    return true;
                } else if (
                    (platform.indexOf("linux") >= 0 ||
                        platform.indexOf("android") >= 0 ||
                        platform.indexOf("pike") >= 0) &&
                    os !== "Linux" &&
                    os !== "Android"
                ) {
                    return true;
                } else if (
                    (platform.indexOf("mac") >= 0 ||
                        platform.indexOf("ipad") >= 0 ||
                        platform.indexOf("ipod") >= 0 ||
                        platform.indexOf("iphone") >= 0) &&
                    os !== "Mac" &&
                    os !== "iOS"
                ) {
                    return true;
                } else if (platform.indexOf("arm") >= 0 && os === "Windows Phone") {
                    return false;
                } else if (
                    platform.indexOf("pike") >= 0 &&
                    userAgent.indexOf("opera mini") >= 0
                ) {
                    return false;
                } else {
                    var platformIsOther =
                        platform.indexOf("win") < 0 &&
                        platform.indexOf("linux") < 0 &&
                        platform.indexOf("mac") < 0 &&
                        platform.indexOf("iphone") < 0 &&
                        platform.indexOf("ipad") < 0 &&
                        platform.indexOf("ipod") < 0;
                    if (platformIsOther !== (os === "Other")) {
                        return true;
                    }
                }

                return (
                    typeof navigator.plugins === "undefined" &&
                    os !== "Windows" &&
                    os !== "Windows Phone"
                );
            })(),
            inconsistencyBrowser: (function () {
                var userAgent = navigator.userAgent.toLowerCase();
                var productSub = navigator.productSub;
                var browser;
                if (
                    userAgent.indexOf("edge/") >= 0 ||
                    userAgent.indexOf("iemobile/") >= 0
                ) {
                    return false;
                } else if (userAgent.indexOf("opera mini") >= 0) {
                    return false;
                } else if (userAgent.indexOf("firefox/") >= 0) {
                    browser = "Firefox";
                } else if (
                    userAgent.indexOf("opera/") >= 0 ||
                    userAgent.indexOf(" opr/") >= 0
                ) {
                    browser = "Opera";
                } else if (userAgent.indexOf("chrome/") >= 0) {
                    browser = "Chrome";
                } else if (userAgent.indexOf("safari/") >= 0) {
                    if (
                        userAgent.indexOf("android 1.") >= 0 ||
                        userAgent.indexOf("android 2.") >= 0 ||
                        userAgent.indexOf("android 3.") >= 0 ||
                        userAgent.indexOf("android 4.") >= 0
                    ) {
                        browser = "AOSP";
                    } else {
                        browser = "Safari";
                    }
                } else if (userAgent.indexOf("trident/") >= 0) {
                    browser = "Internet Explorer";
                } else {
                    browser = "Other";
                }

                if (
                    (browser === "Chrome" || browser === "Safari" || browser === "Opera") &&
                    productSub !== "20030107"
                ) {
                    return true;
                }

                var tempRes = eval.toString().length;
                if (
                    tempRes === 37 &&
                    browser !== "Safari" &&
                    browser !== "Firefox" &&
                    browser !== "Other"
                ) {
                    return true;
                } else if (
                    tempRes === 39 &&
                    browser !== "Internet Explorer" &&
                    browser !== "Other"
                ) {
                    return true;
                } else if (
                    tempRes === 33 &&
                    browser !== "Chrome" &&
                    browser !== "AOSP" &&
                    browser !== "Opera" &&
                    browser !== "Other"
                ) {
                    return true;
                }

                var errFirefox;
                try {
                    throw "a";
                } catch (err) {
                    try {
                        err.toSource();
                        errFirefox = true;
                    } catch (errOfErr) {
                        errFirefox = false;
                    }
                }
                return errFirefox && browser !== "Firefox" && browser !== "Other";
            })(),
            touchSupport: (function () {
                var maxTouchPoints = 0;
                var touchEvent;
                if (typeof navigator.maxTouchPoints !== "undefined") {
                    maxTouchPoints = navigator.maxTouchPoints;
                } else if (typeof navigator.msMaxTouchPoints !== "undefined") {
                    maxTouchPoints = navigator.msMaxTouchPoints;
                }
                try {
                    document.createEvent("TouchEvent");
                    touchEvent = true;
                } catch (_) {
                    touchEvent = false;
                }
                var touchStart = "ontouchstart" in window;
                return [maxTouchPoints, touchEvent, touchStart];
            })(),
            addBehavior: !!window.HTMLElement.prototype.addBehavior,
            doNotTrack: (function () {
                if (navigator.doNotTrack) {
                    return navigator.doNotTrack;
                } else if (navigator.msDoNotTrack) {
                    return navigator.msDoNotTrack;
                } else if (window.doNotTrack) {
                    return window.doNotTrack;
                }
            })(),
            adBlock: (function () {
                var ads = document.createElement("div");
                ads.innerHTML = "&nbsp;";
                ads.className = "adsbox";
                var result = false;
                try {
                    document.body.appendChild(ads);
                    result = document.getElementsByClassName("adsbox")[0].offsetHeight === 0;
                    document.body.removeChild(ads);
                } catch (e) {
                    result = false;
                }
                return result;
            })(),
            referrer: document.referrer
        };
    };

    function BotDetection(tracking_param_name, data_storage_address) {
        this.data_storage_address = data_storage_address;
        if (data_storage_address[data_storage_address.length - 1] == '/') data_storage_address = data_storage_address.slice(0, -1)
        this.tracking_param_name = tracking_param_name;
    };

    BotDetection.prototype.setIntervalSendMouseEvent = function () {
        sendData(this.tracking_param_name, this.data_storage_address)
    }

    BotDetection.prototype.sendFingerprint = function () {
        console.log(this.data_storage_address)
        var data = flatten(getFingerprint());
        var xhr = new XMLHttpRequest();

        xhr.open("POST", this.data_storage_address + "/data/fingerprint", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(
            JSON.stringify({
                data: {
                    fingerprint: data,
                    tracking_code: get_param(this.tracking_param_name),
                    hash_id: hash_id,
                    path: window.location.origin,
                    predetermined: get_param('predetermined') !== null ? get_param('predetermined') : 'not_predicted',
                    zone_id: get_param('zone_id') !== null ? get_param('zone_id') : Math.floor(Math.random() * 9) + 1,
                },
            })
        );
    }

    return BotDetection;
});