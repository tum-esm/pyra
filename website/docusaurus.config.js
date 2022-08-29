// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
    title: 'PYRA 4',
    tagline: 'operate an EM27 station autonomously',
    url: 'https://your-docusaurus-test-site.com',
    baseUrl: '/',
    onBrokenLinks: 'throw',
    onBrokenMarkdownLinks: 'throw',
    favicon: 'img/favicon.ico',

    // GitHub pages deployment config.
    organizationName: 'tum-esm',
    projectName: 'pyra',

    // Even if you don't use internalization, you can use this field to set useful
    // metadata like html lang.
    i18n: {
        defaultLocale: 'en',
        locales: ['en'],
    },

    presets: [
        [
            'classic',
            /** @type {import('@docusaurus/preset-classic').Options} */
            ({
                docs: {
                    sidebarPath: require.resolve('./sidebars.js'),
                    // Remove this to remove the "edit this page" links.
                    editUrl:
                        'https://github.com/tum-esm/pyra/tree/main/website/',
                },
                theme: {
                    customCss: [
                        require.resolve('./src/css/custom.css'),
                        require.resolve('./src/css/tailwind.css'),
                    ],
                },
            }),
        ],
    ],

    themeConfig:
        /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
        ({
            colorMode: {
                defaultMode: 'light',
                disableSwitch: true,
                respectPrefersColorScheme: false,
            },
            navbar: {
                title: 'PYRA 4 Documentation',
                logo: {
                    alt: 'PYRA 4 Logo',
                    src: 'img/logo.svg',
                    width: 32,
                    height: 32,
                },
                items: [
                    {
                        href: 'https://github.com/tum-esm/pyra',
                        position: 'right',
                        className: 'header-github-link',
                        ariaLabel: 'GitHub repository',
                    },
                ],
            },
            footer: {
                style: 'dark',
                copyright: `© ${new Date().getFullYear()} - Associate Professorship of Environmental Sensing and Modeling - Technical University of Munich`,
            },
            prism: {
                theme: lightCodeTheme,
                darkTheme: darkCodeTheme,
            },
        }),
};

module.exports = config;
