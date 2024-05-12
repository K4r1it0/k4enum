import VPagination from "@hennge/vue3-pagination";
import "@hennge/vue3-pagination/dist/vue3-pagination.css";
export default defineNuxtPlugin((nuxtApp) => {
    nuxtApp.vueApp.component("VPagination", VPagination);
});