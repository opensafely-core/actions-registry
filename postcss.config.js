const autoprefixer = require("autoprefixer");
const path = require("node:path");
const postcssColorRgbaFallback = require("postcss-color-rgba-fallback");
const postcssUrl = require("postcss-url");
const tailwindCss = require("tailwindcss");

module.exports = ({ env }) => ({
  plugins: [
    tailwindCss,
    postcssColorRgbaFallback,
    autoprefixer,
    postcssUrl(
      env !== "production"
        ? {
            url: "inline",
            basePath: path.resolve("assets/src/styles"),
          }
        : false
    ),
  ],
});
