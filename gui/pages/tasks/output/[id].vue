<template>
    <SharedScans/>
    <div class="container">
      <div class="flex justify-between items-start mb-8">
        <div>
          <h2 class="mb-5 text-2xl">{{ `${taskname} Output` }}</h2>
        </div>

        <button
          @click="goBack"
          class="bg-white text-black text-xs py-2.5 px-3 rounded-md flex items-center gap-2"
        >
          <span>Scan Tasks</span>
        </button>
      </div></div>
    <div class="container">
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else class="content">
        <pre @dblclick="copyData">{{ data }}</pre>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router';
  import { useRoute, useRuntimeConfig } from '#imports'
  const router = useRouter();
  const config = useRuntimeConfig();
  const route = useRoute();
  const data = ref('');  
  const loading = ref(true);
  const {
  public: { baseURL },
} = useRuntimeConfig();


const path = route.path;
const parts = path.split('_');
const taskname = parts[0].split('/').pop();

const goBack = () => {
  router.go(-1);
};

const copyData = async () => {
  try {
    await navigator.clipboard.writeText(data.value);
    console.log('Data copied to clipboard');
  } catch (err) {
    console.error('Failed to copy data:', err);
  }
};
  const fetchData = async () => {
    try {
      const url = `${baseURL}/download/${route.params.id}`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      data.value = await response.text();
    } catch (error) {
      console.error('Failed to fetch data:', error);
      data.value = `Error: ${error.message}`;
    } finally {
      loading.value = false;
    }
  };
  
  onMounted(fetchData);
</script>