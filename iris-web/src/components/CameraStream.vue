<script lang="ts" setup>
  import { backendConnected, backendURI, ntcore } from '@/nt-listener'
  import { NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { onMounted, ref } from 'vue'

  const brightness = ref(0)
  const exposure = ref(0)
  const gain = ref(0)
  const cameraOrientation = ref('Normal')

  const fps = ref(0)
  const logoSrc = new URL('@/assets/loading.jpeg', import.meta.url).href
  const streamSrcURL = 'http://' + backendURI + ':1180/stream.mjpg'

  const streamSrc = computed<string>(() => {
    return backendConnected.value ? streamSrcURL : logoSrc
  })

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
      <v-img :src="streamSrc" width="100%" />

      <v-select
        v-model="cameraOrientation"
        class="mt-4"
        color="secondary"
        :items="['Normal', '90°', '180°', '270°']"
        label="Display Orientation"
        variant="outlined"
      />

      <v-slider
        v-model="brightness"
        color="secondary"
        hide-details
        :max="288"
        :min="1"
        :step="1"
      >
        <template #label>
          <span class="slider-label">Brightness</span>
        </template>
        <template #append>
          <v-text-field
            v-model="brightness"
            color="secondary"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>
      <v-slider
        v-model="exposure"
        class="my-4"
        color="secondary"
        hide-details
        :max="910"
        :min="4"
        :step="1"
      >
        <template #label>
          <span class="slider-label">Exposure</span>
        </template>
        <template #append>
          <v-text-field
            v-model="exposure"
            color="secondary"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>
      <v-slider
        v-model="gain"
        color="secondary"
        hide-details
        :max="248"
        :min="16"
        :step="1"
      >
        <template #label>
          <span class="slider-label">Sensor Gain</span>
        </template>
        <template #append>
          <v-text-field
            v-model="gain"
            color="secondary"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.slider-label {
  display: inline-block;
  width: 100px;
}
</style>
