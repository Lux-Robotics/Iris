<script lang="ts" setup>
  import { backendConnected, backendURI } from '@/nt-listener'
  import { onMounted, onUnmounted } from 'vue'

  const logoSrc = new URL('@/assets/loading.jpeg', import.meta.url).href
  const streamSrcURL = 'http://' + backendURI + ':1180/stream.mjpg'

  const streamSrc = computed<string>(() => {
    return backendConnected.value ? streamSrcURL : logoSrc
  })

  onMounted(() => {
    console.log('mounted')
  })
  onUnmounted(() => {
    console.log('unmounted')
  })

</script>

<template>
  <v-img :src="streamSrc" width="100%" />
</template>

<style scoped>
.v-img__img {
  display: block !important;
}
</style>
