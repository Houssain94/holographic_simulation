// Copies ../site into ./site so the packaged app contains the same files as the website.
const fs = require("fs"), path = require("path");
const src = path.join(__dirname, "..", "site"), dst = path.join(__dirname, "site");
fs.rmSync(dst, { recursive: true, force: true });
fs.cpSync(src, dst, { recursive: true });
console.log("copied", src, "->", dst);
