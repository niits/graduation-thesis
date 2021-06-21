var page = require("webpage").create();

page.open("http://localhost:5000/", function (status) {
  console.log(status);
  phantom.exit();
});
