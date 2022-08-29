// prettier-ignore

const colors = require('tailwindcss/colors')
const customColors = {
    gray: {
        50: '#f8fafc',
        75: '#f4f7fa',
        100: '#f1f5f9',
        150: '#e9eef4',
        200: '#e2e8f0',
        300: '#cbd5e1',
        350: '#afbccc',
        400: '#94a3b8',
        500: '#64748b',
        600: '#475569',
        700: '#334155',
        750: '#283548',
        800: '#1e293b',
        850: '#162032',
        900: '#0f172a',
        950: '#0B111F',
    },

    red: colors.red,
    green: colors.green,
    yellow: colors.yellow,

    blue: {
        50: '#DCEEFB',
        75: '#c9e7fc',
        100: '#B6E0FE',
        150: '#9DD2F9',
        200: '#84C5F4',
        300: '#62B0E8',
        400: '#4098D7',
        500: '#2680C2',
        600: '#186FAF',
        700: '#0F609B',
        800: '#0A558C',
        900: '#003E6B',
    },

    teal: {
        50: '#f0fdfa',
        75: '#defcf5',
        100: '#ccfbf1',
        200: '#99f6e4',
        300: '#5eead4',
        400: '#2dd4bf',
        500: '#14b8a6',
        600: '#0d9488',
        700: '#0f766e',
        800: '#115e59',
        900: '#134e4a',
        950: '#092725',
    },
};

module.exports = {
    content: ['./src/**/*.{js,jsx,ts,tsx}', './docs/**/*.{md,mdx}'],
    theme: {
        extend: {
            colors: customColors,
            fill: customColors,
        },
    },
    plugins: [],
    prefix: 'tw-',
};
