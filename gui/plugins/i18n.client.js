export default defineNuxtPlugin(app => {
    const BODY_ELEMENT = document.body;
    const HTML_ELEMENT = document.documentElement;
    if (app.$i18n.locale.value == "en") {
        BODY_ELEMENT.setAttribute("dir", "ltr");
        HTML_ELEMENT.setAttribute("lang", "en");
    } else if (app.$i18n.locale.value == "ar") {
        BODY_ELEMENT.setAttribute("dir", "rtl");
        HTML_ELEMENT.setAttribute("lang", "ar");
    }


    app.$i18n.onLanguageSwitched = (oldLocale, newLocale) => {
        if (newLocale == "en") {
            BODY_ELEMENT.setAttribute("dir", "ltr");
            HTML_ELEMENT.setAttribute("lang", "en");
        } else if (newLocale == "ar") {
            BODY_ELEMENT.setAttribute("dir", "rtl");
            HTML_ELEMENT.setAttribute("lang", "ar");
        }

        setTimeout(() => window.location.reload(), 300)
    }
})