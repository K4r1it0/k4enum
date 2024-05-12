<template>
    <div>
      <div class="flex-container">
        <div>
          <!-- Optional: Logo could go here -->
          <!-- <img src="~/assets/images/icons/logo.svg" alt="logo" /> -->
        </div>
        <div class="nav-links">
          <!-- Navigation links would go here -->
        </div>
        <div>
          <!-- Optional: Avatar could go here -->
          <!-- <img src="~/assets/images/imgs/avatar.jpg" alt="avatar" class="size-12 rounded-full object-contain" /> -->
        </div>
      </div>
    </div>
  </template>
  
  <style lang="scss" scoped>
  .flex-container {
    @apply flex items-center justify-end w-[95%] mx-auto p-3; /* This line sets the alignment */
  }
  
  .nav-links {
    @apply flex items-center justify-between gap-2 border border-border p-1 rounded-lg;
    a {
      @apply text-placeholder flex items-center justify-center gap-2 text-xs  p-2 w-[70px] rounded-md transition-all;
      &:hover {
        @apply bg-border;
      }
    }
    .router-link-active {
      &.router-link-exact-active {
        @apply text-white bg-border;
      }
    }
  }
  </style>
  