<script lang="ts" setup>
  import { ntcore } from '@/nt-listener'
  import { NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { onMounted, ref, watch } from 'vue'

  const brightness = ref(0)
  const exposure = ref(0)
  const gain = ref(0)
  const cameraOrientation = ref('Normal')

  const brightnessRef = ref(0)
  const exposureRef = ref(0)
  const gainRef = ref(0)

  onMounted(() => {
    const brightnessTopic: NetworkTablesTopic<number> = ntcore.createTopic('brightness', NetworkTablesTypeInfos.kInteger)
    const exposureTopic: NetworkTablesTopic<number> = ntcore.createTopic('exposure', NetworkTablesTypeInfos.kInteger)
    const gainTopic: NetworkTablesTopic<number> = ntcore.createTopic('gain', NetworkTablesTypeInfos.kInteger)

    brightnessTopic.subscribe(v => {
      if (v !== null && brightnessRef.value !== v) {
        brightness.value = v
        brightnessRef.value = v
      }
    }, true)

    gainTopic.subscribe(v => {
      if (v !== null && gainRef.value !== v) {
        gain.value = v
        gainRef.value = v
      }
    }, true)

    exposureTopic.subscribe(v => {
      if (v !== null && exposureRef.value !== v) {
        exposure.value = v
        exposureRef.value = v
      }
    }, true)

    watch(brightness, async newBrightness => {
      brightnessRef.value = newBrightness
      brightnessTopic.publish()
      brightnessTopic.setValue(newBrightness)
    })

    watch(exposure, async newExposure => {
      brightnessRef.value = newExposure
      exposureTopic.publish()
      exposureTopic.setValue(newExposure)
    })

    watch(gain, async newGain => {
      gainRef.value = newGain
      gainTopic.publish()
      gainTopic.setValue(newGain)
    })
  })
</script>

<template>
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
</template>

<style scoped>
.slider-label {
  display: inline-block;
  width: 100px;
}
</style>
