<script setup lang="ts">

  import { backendConnected, ntcore } from '@/nt-listener'
  import { NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { onMounted, ref } from 'vue'

  const fps = ref(0)

  const fpsText = computed<string>(() => {
    return backendConnected.value ? fps.value.toFixed(2) + ' FPS' : 'Disconnected'
  })

  const fpsColor = computed<string>(() => {
    if (!backendConnected.value) {
      return 'red'
    } else if (fps.value > 40) {
      return 'green'
    } else if (fps.value > 20) {
      return 'yellow'
    } else {
      return 'red'
    }
  })

  onMounted(() => {
    const fpsTopic: NetworkTablesTopic<number> = ntcore.createTopic('fps', NetworkTablesTypeInfos.kDouble)

    fpsTopic.subscribe(v => {
      if (v === null) {
        v = 0
      }
      fps.value = v
    }, true)
  })

</script>

<template>
  <!--  <v-card color="background" min-width="300" variant="flat">-->
  <v-card border min-width="300">
    <template #title>
      <span class="font-weight-black">Camera</span>
    </template>
    <template #append>
      <v-chip :color="fpsColor">
        {{ fpsText }}
      </v-chip>
    </template>

    <v-divider />

    <v-card-text>
      <CameraStream />
    </v-card-text>
  </v-card>
</template>

<style scoped>
.stream-container {
position: relative;
}
</style>
