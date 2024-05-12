<template>
  <NuxtLink
    class="p-2 rounded-lg bg-[#121214] grid grid-cols-5 row cursor-pointer hover:bg-border transition-all items-center"
    :to="`/tasks/${item.scan_id}`"
  >
    <p>{{ index + 1 }}</p>
    <p>{{ item.domain }}</p>
    <p>{{ item.scan_type }}</p>
    <p>
      {{ new Date(item.createdAt).toLocaleDateString() }}
      {{ new Date(item.createdAt).toLocaleTimeString() }}
    </p>
    <p
      :class="getStyle(item.status)"
      class="px-2 py-1 rounded w-fit mx-auto !text-xs capitalize min-w-[80px] flex items-center justify-center"
    >
      <span v-if="item.status == 'done'">Completed</span>
      <span v-else>{{ item.status }}</span>
    </p>
  </NuxtLink>
</template>

<script setup>
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

const getStyle = (status) => {
  switch (status) {
    case "pending":
      return "!text-placeholder bg-[#71717a33]";
    case "running":
      return "!text-[#f59e0b] !bg-[#f59e0b33]";
    case "done":
      return "!text-[#22c55e] bg-[#22c55e33]";
    case "failed":
      return "text-[#f43f5e] bg-[#f43f5e33]";
    default:
      return "text-gray-400";
  }
};
</script>


