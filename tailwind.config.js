/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./bloggr/templates/**/*.html",
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"Source Serif 4"', 'Georgia', 'Cambria', '"Times New Roman"', 'serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('flowbite/plugin')
  ],
}
