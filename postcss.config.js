module.exports = {
  plugins: [
    require('tailwindcss'),
    require("postcss-color-rgba-fallback"),
    require('autoprefixer'),
    require('cssnano')({
      preset: [
        "default",
        {
          colormin: false,
          discardComments: { removeAll: true },
        },
      ],
    }),
  ],
};
