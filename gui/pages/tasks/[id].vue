<template>

<SharedScans />

<div>
    <!-- <div class="sub-nav mb-8">
      <div class="w-[95%] mx-auto flex items-center gap-3">
        <button>
          <img src="~/assets/images/icons/scans-active.svg" alt="logo" />

          <span>Tasks</span>
        </button>
      </div>
    </div> -->

   
    <div class="container">
      <div class="flex justify-between items-start mb-8">
        <div>
          <h2 v-if="!domain">
            <Skeleton height="2rem" class="mb-2"></Skeleton>
          </h2>
          <h2 v-else class="mb-5 text-2xl">{{ domain }}</h2>

          <p class="text-placeholder text-xs">
            Browse scans, delve into their details, or initiate a new scan.
          </p>
        </div>
        <button
    @click="goToScans"
    class="bg-white text-black text-xs py-2.5 px-3 rounded-md flex items-center gap-2"
  >
    <span>My Scans</span>
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
            getTasks();
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
            class="w-full md:w-14rem"
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
        <PagesTasksHeader />

        <template v-if="loading">
          <Skeleton
            v-for="i in 6"
            :key="i"
            height="2rem"
            class="mb-2"
          ></Skeleton>
        </template>

        <template v-else>
          <PagesTasksRow
            v-for="(task, i) in tasks"
            :index="i"
            :item="task"
            :key="task.task_id"
            class="mb-2 last:mb-0"
          />
        </template>

        <div v-if="paginator && tasks.length" class="mt-12">
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
              getTasks();
            "
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Dropdown from "primevue/dropdown";
import Skeleton from "primevue/skeleton";

const {
  public: { baseURL },
} = useRuntimeConfig();
const router = useRouter();
const route = useRoute();

const visible = ref(false);

const status = ref([
  {
    id: "all",
    title: "TOTAL TASKS",
    img: "/icons/shield.svg",
    bgIconColor: "#6366f133",
    value: 0,
  },
  {
    id: "running",
    title: "RUNNING TASKS",
    img: "/icons/reload.svg",
    bgIconColor: "#f59e0b33",
    value: 0,
  },
  {
    id: "pending",
    title: "Pending TASKS",
    img: "/icons/clock.svg",
    bgIconColor: "#71717a33",
    value: 0,
  },
  {
    id: "done",
    title: "Complete TASKS",
    img: "/icons/checked.svg",
    bgIconColor: "#22c55e33",
    value: 0,
  },
  {
    id: "failed",
    title: "Failed TASKS",
    img: "/icons/close.svg",
    bgIconColor: "#f43f5e33",
    value: 0,
  },
]);

function goToScans() {
  router.push('/scans')
}

const activeStatus = ref(
  status.value.find((el) => el.id == route?.query?.status) || {
    id: "all",
    title: "TOTAL TASKS",
    img: "/icons/shield.svg",
    bgIconColor: "#6366f133",
    value: 0,
  }
);


function convertToDefaultSearchValue(searchParam) {
  const tasks = searchParam.split('|').map(task => `Task = '${task}'`);
  return tasks.join(' & ');
}

function convertToSearchParam(defaultSearchValue) {
  const tasks = defaultSearchValue.match(/'([^']+)'/g).map(task => task.replace(/'/g, ''));
  return tasks.join('|');
}

const searchValue = ref(convertToDefaultSearchValue(route.query.search) || "Task = 'TaskA' & Task = 'TaskB' & Task = 'TaskC' & Task = 'TaskD'");
const submitSearch = () => {
  page.value = 1;
  router.push({ query: { search: convertToSearchParam(searchValue.value) } });

  getTasks();
};
const reload = () => {
  page.value = 1;
  searchValue.value = "";
  (activeStatus.value = {
    id: "all",
    title: "TOTAL TASKS",
    img: "/icons/shield.svg",
    bgIconColor: "#6366f133",
    value: 0,
  }),
    router.push({ query: {} });
  getTasks();
};

const selectedCity = ref();
const cities = ref([
  { name: "New York", code: "NY" },
  { name: "Rome", code: "RM" },
  { name: "London", code: "LDN" },
  { name: "Istanbul", code: "IST" },
  { name: "Paris", code: "PRS" },
]);

const loading = ref(false);

const domain = ref("");
const tasks = ref([]);
const paginator = ref(null);
const page = ref(+route.query.page || +1);

const getTasks = async () => {
  loading.value = true;
  try {
    const data = await $fetch(`scans/${route.params.id}/tasks`, {
      method: "GET",
      baseURL,
      params: {
        page: page.value,
        search: convertToSearchParam(searchValue.value),
        status: activeStatus.value.id == "all" ? null : activeStatus.value.id,
      },
    });
    domain.value = data.domain;
    tasks.value = data.data;
    paginator.value = data.pagination;
  } catch (err) {
    console.log(err);
  }
  loading.value = false;
};
getTasks();

const loadingCounts = ref(false);
const counts = ref(null);
const getCounts = async () => {
  loadingCounts.value = true;
  try {
    const data = await $fetch(`scans/${route.params.id}/tasks/count`, {
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
setInterval(getCounts, 10000);
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
