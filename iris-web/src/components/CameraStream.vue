<script lang="ts" setup>
  import { backendConnected, backendURI } from '@/nt-listener'

  const logoSrc = new URL('@/assets/loading.jpeg', import.meta.url).href
  const streamSrcURL = 'http://' + backendURI + ':1180/stream.mjpg'

  const streamSrc = computed<string>(() => {
    return backendConnected.value ? streamSrcURL : logoSrc
  })

  const mjpgStream: any = ref(null)
  onBeforeUnmount(() => {
    if (!mjpgStream.value) return
    mjpgStream.value.src = null
  })
</script>

<template>
  <img ref="mjpgStream" class="responsive-image" :src="streamSrc">
</template>

<style scoped>
.responsive-image {
  width: 100%;
  height: 100%;
  object-fit: contain; /* Image will be fully visible, keeping its aspect ratio */
}
</style>
