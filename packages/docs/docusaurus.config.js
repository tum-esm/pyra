// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer/themes/github");
const darkCodeTheme = require("prism-react-renderer/themes/dracula");

async function createConfig() {
  const mdxMermaid = await import("mdx-mermaid");

  /** @type {import('@docusaurus/types').Config} */
  return {
    title: "PYRA 4",
    tagline: "operate an EM27 station autonomously",
    staticDirectories: ["static"],
    url: "https://your-docusaurus-test-site.com",
    baseUrl: "/",
    onBrokenLinks: "throw",
    onBrokenMarkdownLinks: "throw",
    favicon: "img/favicon.ico",

    // GitHub pages deployment config.
    organizationName: "tum-esm",
    projectName: "pyra",

    // Even if you don't use internalization, you can use this field to set useful
    // metadata like html lang.
    i18n: {
      defaultLocale: "en",
      locales: ["en"],
    },

    plugins: ["docusaurus-plugin-sass"],

    presets: [
      [
        "classic",
        /** @type {import('@docusaurus/preset-classic').Options} */
        ({
          docs: {
            sidebarPath: require.resolve("./sidebars.js"),
            // Remove this to remove the "edit this page" links.
            editUrl: "https://github.com/tum-esm/pyra/tree/main/website/",
            remarkPlugins: [mdxMermaid.default],
          },
          theme: {
            customCss: [
              require.resolve("./src/css/fonts.css"),
              require.resolve("./src/css/custom.scss"),
            ],
          },
        }),
      ],
    ],

    themeConfig:
      /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
      ({
        colorMode: {
          defaultMode: "light",
          disableSwitch: true,
          respectPrefersColorScheme: false,
        },
        navbar: {
          title: "PYRA 4",
          logo: {
            alt: "PYRA 4 Logo",
            src: "img/logo.svg",
            width: 32,
            height: 32,
          },
          items: [
            {
              href: "https://github.com/tum-esm/pyra",
              position: "right",
              className: "header-github-link",
            },
          ],
          hideOnScroll: true,
        },
        footer: {
          style: "dark",
          copyright: `© ${new Date().getFullYear()} - Associate Professorship of Environmental Sensing and Modeling - Technical University of Munich`,
        },
        prism: {
          theme: require("prism-react-renderer/themes/github"),
          additionalLanguages: ["python"],
        },
        algolia: {
          appId: "HVYNW5V940",
          apiKey: "6f156c973f748938883016d17df0fbf7", // public API key
          indexName: "pyra-4",
          searchPagePath: false,
        },
      }),
  };
}

module.exports = createConfig;
