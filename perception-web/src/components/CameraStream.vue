<template>
  <v-card elevation="12" min-width="400" rounded="lg" width="100%">
    <v-toolbar density="compact">
      <v-toolbar-title class="font-weight-bold">Camera</v-toolbar-title>
      <v-spacer />
      <v-chip class="ma-2" :color="fpsColor">
        {{ fpsText }}
      </v-chip>
    </v-toolbar>
    <div class="px-4 py-4">
      <v-img :src="streamSrc" width="100%" />

      <v-select
        class="ma-4"
        :items="['Normal', '90°', '180°', '270°']"
        label="Orientation"
        variant="outlined"
      />

      <v-slider
        v-model="brightness"
        class="ma-4"
        hide-details
        :max="255"
        :step="1"
      >
        <template #label>
          <span class="slider-label">Brightness</span>
        </template>
        <template #append>
          <v-text-field
            v-model="brightness"
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
        class="ma-4"
        hide-details
        :max="255"
        :step="1"
      >
        <template #label>
          <span class="slider-label">Exposure</span>
        </template>
        <template #append>
          <v-text-field
            v-model="exposure"
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
        class="ma-4"
        hide-details
        :max="255"
        :step="1"
      >
        <template #label>
          <span class="slider-label">Sensor Gain</span>
        </template>
        <template #append>
          <v-text-field
            v-model="gain"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>
    </div>
  </v-card>
</template>

<script lang="ts" setup>
  import { NetworkTables, NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { computed, onMounted, ref } from 'vue'

  const brightness = ref(50) // Initial slider value
  const exposure = ref(50) // Initial slider value
  const gain = ref(50) // Initial slider value
  const fps = ref(0) // Initial slider value
  const logoSrc = new URL('@/assets/loading.jpeg', import.meta.url).href
  const streamSrcURL = 'http://localhost:5801/stream.mjpg'
  const backendConnected = ref(false)

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
    const ntcore = NetworkTables.getInstanceByURI('127.0.0.1')
    ntcore.addRobotConnectionListener(v => {
      backendConnected.value = v
    }, true)

    const fpsTopic: NetworkTablesTopic<number> = ntcore.createTopic('fps', NetworkTablesTypeInfos.kDouble)
    fpsTopic.subscribe(v => {
      if (v === null) {
        v = 0
      }
      fps.value = v
    }, true)
  })
</script>

<style>
.slider-label {
  display: inline-block;
  width: 100px;
}
</style>
