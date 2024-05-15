<template>
  <div class="h-[calc(100vh-72px)] flex items-center justify-center">
    <h1 class="text-placeholder">K4enum</h1>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
router.push('/scans')
</script>

<style lang="scss" scoped></style>
