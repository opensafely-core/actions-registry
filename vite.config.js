import copy from "rollup-plugin-copy";

/**
 * @type {import('vite').UserConfig}
 */
 const config = {
  base: "/static/",
  build: {
    manifest: true,
    rollupOptions: {
      input: {
        main: "./assets/src/scripts/main.js",
      },
    },
    outDir: "assets/dist",
    emptyOutDir: true,
  },
  clearScreen: false,
  plugins: [
    copy({
      targets: [
        {
          src: "./node_modules/alpinejs/dist/*",
          dest: "./assets/dist/vendor",
        },
      ],
      hook: "writeBundle",
    }),
  ],
};

export default config;
