<template>
  <div class="shell">
    <RouterView />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>

<style scoped>
.shell {
  min-height: 100vh;
  background: #02103a;
}
</style>
