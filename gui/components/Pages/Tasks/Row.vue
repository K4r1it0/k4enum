<template>
  
  <div 
    v-if="
      item.task_name !== 'MainEnumerationTask' &&
      item.task_name !== 'YieldWrapper' &&
      item.task_name !== 'Miscellaneous'
    "
     class="p-2 rounded-lg bg-[#121214] grid grid-cols-6 row hover:bg-border transition-all"
    @click="navigateToTask(item.task_id)" 
  >
    <p>{{ index + 1 }}</p>

    <p>{{ item.task_name }}</p>

    <p>{{ item.type }}</p>

    <p>
      {{ new Date(item.updatedAt).toLocaleDateString() }}
      {{ new Date(item.updatedAt).toLocaleTimeString() }}
    </p>

    <p
      :class="getStyle(item.status)"
      class="px-2 py-1 rounded w-fit mx-auto !text-xs capitalize min-w-[80px] flex items-center justify-center"
    >
      <span v-if="item.status == 'done'">Completed</span>
      <span v-else>{{ item.status }}</span>
    </p>

    <p class="ms-4 text-center">
      <NuxtLink
        v-if="available"
        target="_blank"
        :to="`${baseURL}/download/${item.task_id}`"
        type="button"
      >
        <i class="fal fa-cloud-download"></i>
      </NuxtLink>
      <span v-else class="text-gray-500">
        <i class="fal fa-cloud-download"></i>
      </span>
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
const available = ref(false);
const router = useRouter();


const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  index: {
    type: Number,
    required: true,
  },
});

const checkContentAvailability = async () => {
  try {
    const response = await fetch(`${baseURL}download/${props.item.task_id}`, { method: 'HEAD' });
    if (response.ok && parseInt(response.headers.get('Content-Length')) > 0) {
      available.value = true;
    }
  } catch (error) {
    console.error('Error checking content availability:', error);
  }
};


const navigateToTask  = (taskId) => {
  if (available) {
    router.push(`/tasks/output/${taskId}`);
  }
};
onMounted(checkContentAvailability);

const {
  public: { baseURL },
} = useRuntimeConfig();

const getStyle = (status) => {
  switch (status) {
    case "pending":
      return "!text-placeholder bg-[#71717a33]";
    case "running":
      return "!text-[#f59e0b] !bg-[#f59e0b33]";
    case "done":
      return "!text-[#22c55e] bg-[#22c55e33]";
    case "failed":
      return "!text-[#f43f5e] bg-[#f43f5e33]";
    default:
      return "text-gray-400";
  }
};
</script>

<style lang="scss" scoped>
.row {
  p {
    @apply text-sm text-placeholder font-light;
  }
}
</style>
