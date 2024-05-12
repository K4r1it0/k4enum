// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: false },
  ssr: true,
  app: {
    head: {
      meta: [
        { charset: "utf-8" },
        {
          name: "viewport",
          content: "width=device-width, initial-scale=1",
        },
      ],
      link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
      title: "k4enum",
      style: [],
      script: [],
    },
  },
  css: [
    "~/assets/style/main.scss",
    "primevue/resources/themes/aura-light-green/theme.css",
    "primevue/resources/primevue.css",
    "~/assets/style/fontAwesome.css",
  ],
  plugins: [
    "~/plugins/i18n.client.js",
    "~/plugins/vue3-toastify.client.js",
    "~/plugins/primevue.ts",
    "~/plugins/v-pagination.ts",
  ],
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },
  modules: [
    "@pinia/nuxt",
    "nuxt-headlessui",
    [
      "@nuxtjs/i18n",
      {
        locales: [
          {
            name: "EN",
            code: "en",
            iso: "en-US",
            file: "en.json",
            dir: "ltr",
          },
          {
            name: "AR",
            code: "ar",
            iso: "ar-AR",
            file: "ar.json",
            dir: "rtl",
          },
        ],
        lazy: true,
        langDir: "locales/",
        defaultLocale: "en",
        detectBrowserLanguage: false,
        vueI18nLoader: true,
      },
    ],
    [
      "@vee-validate/nuxt",
      {
        autoImports: true,
        componentNames: {
          Form: "VeeForm",
          Field: "VeeField",
          ErrorMessage: "VeeErrorMessage",
        },
      },
    ],
    // "@nuxtjs/color-mode",
  ],
  // colorMode: {
  //   preference: "system", // default value of $colorMode.preference
  //   fallback: "light", // fallback value if not system preference found
  //   classSuffix: "",
  //   classPrefix: "",
  //   storageKey: "nuxt-color-mode",
  //   hid: "nuxt-color-mode-script",
  //   globalName: "__NUXT_COLOR_MODE__",
  //   componentName: "ColorScheme",
  // },
  build: {
    transpile: ["primevue"],
  },
  runtimeConfig: {
    public: {
      baseURL: "http://159.203.129.22:1234/",
    },
  },
  spaLoadingTemplate: false,
});
