<template>
  <SharedScans />
  <div>
    <!-- <div class="sub-nav mb-8">
      <div class="w-[95%] mx-auto flex items-center gap-3">
        <button>
          <img src="~/assets/images/icons/scans-active.svg" alt="logo" />

          <span>Scans</span>
        </button>
      </div>
    </div> -->

    <div class="container">
      <div class="flex justify-between items-start mb-8">
        <div>
          <h2 class="mb-5 text-2xl">Your Scans</h2>

          <p class="text-placeholder text-xs">
            Browse scans, delve into their details, or initiate a new scan.
          </p>
        </div>

        <button
          @click="visible = true"
          class="bg-white text-black text-xs py-2.5 px-3 rounded-md flex items-center gap-2"
        >
          <span>New Scan</span>
        </button>
      </div>

      <div class="grid grid-cols-5 gap-2 mb-7">
        <div
          v-for="item in status"
          :key="item.id"
          class="border rounded-lg border-border p-3 hover:border-active-border transition-all cursor-pointer"
          :class="
            activeStatus.id == item.id ? 'bg-border !border-active-border' : ''
          "
          @click="
            activeStatus = item;
            page = 1;
            router.push({
              path: '',
              query: Object.assign({}, route.query, {
                status: activeStatus.id,
              }),
            });
            getScans();
          "
        >
          <div class="flex items-center gap-2 mb-5">
            <div
              class="flex items-center justify-center size-8 rounded-lg"
              :style="{ 'background-color': item.bgIconColor }"
            >
              <img :src="item.img" :alt="item.title" class="size-4" />
            </div>

            <span class="text-xs text-placeholder uppercase">{{
              item.title
            }}</span>
          </div>

          <i v-if="loadingCounts" class="fal fa-sync fa-spin"></i>
          <span v-else class="text-xl"> {{ item.value?.count }} </span>
        </div>
      </div>

      <div class="flex items-stretch gap-3 mb-7">
        <form
          @submit.prevent="submitSearch"
          class="flex items-stretch flex-grow"
        >
          <input
            type="text"
            class="search-input"
            placeholder=""
            v-model="searchValue"
          />

          <button
            class="bg-active-bg w-[50px] border-border border rounded-e-md hover:bg-border transition-all"
            type="submit"
          >
            <i class="fal fa-search"></i>
          </button>
        </form>

        <!-- <div class="custom-prime-vue">
          <Dropdown
            v-model="selectedCity"
            :options="cities"
            optionLabel="name"
            placeholder="Select a Status"
            class="w-full"
          />
        </div> -->

        <button
          @click="reload()"
          type="button"
          class="w-10 border border-border rounded-md text-sm"
        >
          <i class="fal fa-redo"></i>
        </button>
      </div>

      <div class="mb-2">
        <PagesScansHeader />

        <template v-if="loading">
          <Skeleton
            v-for="i in 6"
            :key="i"
            height="2rem"
            class="mb-2"
          ></Skeleton>
        </template>

        <template v-else-if="scans.length">
          <PagesScansRow
            v-for="(scan, i) in scans"
            :key="scan.scan_id"
            :item="scan"
            :index="i"
            class="mb-2 last:mb-0"
          />
        </template>

        <template v-else>
          <div
            class="h-[300px] flex items-center justify-center flex-col gap-2"
          >
            <img src="/icons/file.svg" alt="" />
            <p class="text-sm">Run your first scan</p>
            <span class="text-placeholder text-xs">
              Begin your first scan now to uncover vulnerabilities.
            </span>
            <button
              @click="visible = true"
              class="bg-white text-black text-xs py-2.5 px-3 rounded-md flex items-center"
            >
              <br>
              <span>Start Scan</span>
            </button>
          </div>
        </template>

        <div v-if="paginator && scans.length" class="mt-12">
          <VPagination
            v-model="page"
            :pages="+paginator.total_pages"
            :rageSize="+paginator.per_page"
            activeColor="#fff"
            @update:modelValue="
              router.push({
                path: '',
                query: Object.assign({}, route.query, {
                  page,
                }),
              });
              getScans();
            "
          />
        </div>
      </div>
    </div>

    <Dialog
      v-model:visible="visible"
      modal
      header="Create New Scan"
      :style="{ width: '25rem' }"
    >
      <form @submit.prevent="submit">
        <div class="mb-2">
          <Dropdown
            v-model="selectedType"
            :options="scanTypes"
            optionLabel="name"
            placeholder="Select Scan Type"
            class="w-full !border !border-active-border focus:!outline-none"
            inputClass=""
          />
        </div>

        <div v-if="selectedType.value == 'passive'">
          <textarea
            v-if="selectedType.id == 'multiple_passive'"
            v-model="target"
            class="w-full border border-active-border rounded-lg bg-transparent p-2 placeholder:text-xs text-xs focus:outline-none min-h-[100px]"
            placeholder=""
          ></textarea>

          <input
            v-if="selectedType.id == 'single_passive'"
            v-model="target"
            type="text"
            placeholder="Example.com"
            class="w-full border border-active-border rounded-lg bg-transparent p-2 px-3 placeholder:text-xs text-xs focus:outline-none h-[34px] mb-2"
          />
        </div>

        <div v-else>
          <input
            type="text"
            v-model="target"
            placeholder="Example.com"
            class="w-full border border-active-border rounded-lg bg-transparent p-2 px-3 placeholder:text-xs text-xs focus:outline-none h-[34px] mb-2"
          />
        </div>

        <div class="flex items-center justify-center mt-3">
          <button
            type="submit"
            class="btn-reverse bg-white text-black text-xs py-2.5 px-3 rounded-md flex items-center justify-center gap-2 w-[90px]">Start Scan</button>
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup>
import Dialog from "primevue/dialog";
import Dropdown from "primevue/dropdown";
import Skeleton from "primevue/skeleton";
import MultiSelect from "primevue/multiselect";

const {
  public: { baseURL },
} = useRuntimeConfig();
const route = useRoute();
const router = useRouter();

const visible = ref(false);

const status = ref([
  {
    id: "all",
    title: "TOTAL SCANS",
    img: "/icons/shield.svg",
    bgIconColor: "#6366f133",
    value: 0,
  },
  {
    id: "running",
    title: "RUNNING SCANS",
    img: "/icons/reload.svg",
    bgIconColor: "#f59e0b33",
    value: 0,
  },
  {
    id: "pending",
    title: "Pending SCANS",
    img: "/icons/clock.svg",
    bgIconColor: "#71717a33",
    value: 0,
  },
  {
    id: "done",
    title: "Complete Scans",
    img: "/icons/checked.svg",
    bgIconColor: "#22c55e33",
    value: 0,
  },
  {
    id: "failed",
    title: "Failed Scans",
    img: "/icons/close.svg",
    bgIconColor: "#f43f5e33",
    value: 0,
  },
]);

const activeStatus = ref(
  status.value.find((el) => el.id == route?.query?.status) || {
    id: "all",
    title: "TOTAL SCANS",
    img: "/icons/shield.svg",
    bgIconColor: "#6366f133",
    value: 0,
  }
);

const searchValue = ref(route.query.search || "");
const submitSearch = () => {
  page.value = 1;
  router.push({ query: { search: searchValue.value } });

  getScans();
};

const reload = () => {
  page.value = 1;
  searchValue.value = "";
  (activeStatus.value = {
    id: "all",
    title: "TOTAL SCANS",
    img: "/icons/shield.svg",
    bgIconColor: "#6366f133",
    value: 0,
  }),
    router.push({ query: {} });
  getScans();
};

const selectedCity = ref();
const cities = ref([
  { name: "New York", code: "NY" },
  { name: "Rome", code: "RM" },
  { name: "London", code: "LDN" },
  { name: "Istanbul", code: "IST" },
  { name: "Paris", code: "PRS" },
]);

const selectedType = ref({
  id: "hybrid",
  value: "hybrid",
  name: "Single Hybrid",
});
const scanTypes = ref([
  {
    id: "hybrid",
    value: "hybrid",
    name: "Single Hybrid",
  },
  {
    id: "single_passive",
    value: "passive",
    name: "Single Passive",
  },
  {
    id: "multiple_passive",
    value: "passive",
    name: "Multiple Passive",
  },
]);

const products = ref([
  {
    code: "1234",
    name: "Istanbul",
    category: "London",
    quantity: 1,
  },
]);

const loading = ref(false);

const target = ref("");

const submit = async () => {
  try {
    const frmData = new FormData();
    // frmData.append("scan_type", selectedType.value.value);
    // frmData.append("target", target.value);

    const data = await $fetch(`scans`, {
      method: "POST",
      baseURL,
      body: {
        type: selectedType.value.value,
        target: target.value,
      },
    });

    console.log(data);
    visible.value = false;
    getScans();
  } catch (error) {
    console.log(error);
  }
};

const scans = ref([]);
const paginator = ref(null);
const page = ref(+route.query.page || +1);

const getScans = async () => {
  loading.value = true;
  try {
    const data = await $fetch("scans", {
      method: "GET",
      baseURL,
      params: {
        page: page.value,
        search: searchValue.value,
        status: activeStatus.value.id == "all" ? null : activeStatus.value.id,
      },
    });
    scans.value = data.data;
    paginator.value = data.pagination;
  } catch (err) {
    console.log(err);
  }
  loading.value = false;
};
getScans();

const loadingCounts = ref(false);
const counts = ref(null);
const getCounts = async () => {
  loadingCounts.value = true;
  try {
    const data = await $fetch(`scans/count`, {
      method: "GET",
      baseURL,
    });

    counts.value = data;

    status.value.forEach((item) => {
      item.value = data.status_counts.find((el) => el.status == item.id);
    });
  } catch (err) {
    console.log(err);
  }
  loadingCounts.value = false;
};
getCounts();
</script>

<style lang="scss" scoped>
.sub-nav {
  @apply border-b border-border;
  button {
    @apply flex items-center justify-center gap-2 text-xs w-[80px] py-2 border-b-2 border-active;
  }
}
.search-input {
  @apply bg-transparent block border border-e-0 border-border focus:outline-none placeholder:text-placeholder placeholder:text-xs w-full px-2 min-h-[35px] rounded-s-md text-xs bg-active-bg hover:bg-border transition-[background] focus-within:outline-none;
}
</style>
