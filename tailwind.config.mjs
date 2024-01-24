import { fontFamily } from "tailwindcss/defaultTheme";
import tailwindTypography from "@tailwindcss/typography";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./actions/templates/**/*.html"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Public Sans", ...fontFamily.sans],
      },
      colors: {
        oxford: {
          DEFAULT: "#002147",
          50: "#f1f7ff",
          100: "#cfe5ff",
          200: "#9ccaff",
          300: "#69afff",
          400: "#3693ff",
          500: "#0378ff",
          600: "#0058be",
          700: "#00397a",
          800: "#002147",
          900: "#001936",
        },
      },
      typography: ({ theme }) => ({
        oxford: {
          css: {
            "--tw-prose-body": theme("colors.gray[800]"),
            "--tw-prose-headings": theme("colors.oxford[900]"),
            "--tw-prose-lead": theme("colors.oxford[700]"),
            "--tw-prose-links": theme("colors.oxford[600]"),
            "--tw-prose-bold": theme("colors.oxford[900]"),
            "--tw-prose-counters": theme("colors.oxford[600]"),
            "--tw-prose-bullets": theme("colors.gray[800]"),
            "--tw-prose-hr": theme("colors.oxford[300]"),
            "--tw-prose-quotes": theme("colors.oxford[900]"),
            "--tw-prose-quote-borders": theme("colors.oxford[300]"),
            "--tw-prose-captions": theme("colors.oxford[700]"),
            "--tw-prose-code": theme("colors.oxford[900]"),
            "--tw-prose-pre-code": theme("colors.oxford[100]"),
            "--tw-prose-pre-bg": theme("colors.oxford[900]"),
            "--tw-prose-th-borders": theme("colors.oxford[300]"),
            "--tw-prose-td-borders": theme("colors.oxford[200]"),
            "--tw-prose-invert-body": theme("colors.oxford[200]"),
            "--tw-prose-invert-headings": theme("colors.white"),
            "--tw-prose-invert-lead": theme("colors.oxford[300]"),
            "--tw-prose-invert-links": theme("colors.white"),
            "--tw-prose-invert-bold": theme("colors.white"),
            "--tw-prose-invert-counters": theme("colors.oxford[400]"),
            "--tw-prose-invert-bullets": theme("colors.oxford[600]"),
            "--tw-prose-invert-hr": theme("colors.oxford[700]"),
            "--tw-prose-invert-quotes": theme("colors.oxford[100]"),
            "--tw-prose-invert-quote-borders": theme("colors.oxford[700]"),
            "--tw-prose-invert-captions": theme("colors.oxford[400]"),
            "--tw-prose-invert-code": theme("colors.white"),
            "--tw-prose-invert-pre-code": theme("colors.oxford[300]"),
            "--tw-prose-invert-pre-bg": "rgb(0 0 0 / 50%)",
            "--tw-prose-invert-th-borders": theme("colors.oxford[600]"),
            "--tw-prose-invert-td-borders": theme("colors.oxford[700]"),
          },
        },
      }),
    },
  },
  plugins: [tailwindTypography],
}
