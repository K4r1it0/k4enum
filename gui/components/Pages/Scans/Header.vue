<template>
  <div
    class="border border-border p-2 rounded-lg bg-[#121214] grid grid-cols-5 header mb-2"
  >
    <h2>#</h2>
    <h2>Domain</h2>
    <h2>Type</h2>
    <h2>Created At</h2>
    <h2 class="text-center">Status</h2>
  </div>
</template>

<script setup></script>

<style lang="scss" scoped>
.header {
  h2 {
    @apply text-sm text-placeholder font-bold;
  }
}
</style>
