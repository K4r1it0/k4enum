<template>
  <div>
    <div class="flex items-center justify-between w-[95%] mx-auto p-3">
      <div>
        <!-- <img src="~/assets/images/icons/logo.svg" alt="logo" /> -->
      </div>
 
      <div class="nav-links">
        <NuxtLink to="/">
          <img
            v-show="$route.path == '/'"
            src="~/assets/images/icons/home-active.svg"
            alt="logo"
          />
          <img
            v-show="$route.path !== '/'"
            src="~/assets/images/icons/home.svg"
            alt="logo"
          />
          <span> Home </span>
        </NuxtLink>
     
        <NuxtLink to="/scans">
        <img
            v-show="$route.path == '/scans'"
            src="~/assets/images/icons/scans-active.svg"
            alt="logo"
          />
          <img
            v-show="$route.path !== '/scans'"
            src="~/assets/images/icons/scans.svg"
            alt="logo"
          />

          <span> Scans </span>
        </NuxtLink>
      </div>

      <div>
        <!-- <img
          src="~/assets/images/imgs/avatar.jpg"
          alt="avatar"
          class="size-12 rounded-full object-contain"
        /> -->
      </div>
    </div>
  </div>
</template>

<script setup></script>

<style lang="scss" scoped>
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
