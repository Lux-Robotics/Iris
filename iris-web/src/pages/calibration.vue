<script setup lang="ts">
  import { apiURI, ntcore } from '@/nt-listener'
  import axios from 'axios'
  import { NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { onMounted, watch } from 'vue'

  const currentCalibration = ref('')
  const text = ref('No calibrations loaded')
  const imageSelection = ref('projection_uncertainty.png')
  const imgSrc = computed<string>(() => {
    return apiURI + '/calibrations/' + currentCalibration.value + '/' + imageSelection.value
  })

  const images = [
    { title: 'Projection Uncertainty', value: 'projection_uncertainty.png' },
    { title: 'Distortion', value: 'distortion.png' },
    { title: 'Residuals', value: 'residuals.png' },
    { title: 'Valid Intrinsics Region', value: 'valid_intrinsics_region.png' },
  ]

  async function updateText () {
    try {
      const response = await axios.get(apiURI + '/calibrations/' + currentCalibration.value + '/calibration.toml', {
        responseType: 'text', // Ensure the response is treated as text
      })
      text.value = response.data
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  }

  onMounted(() => {
    const currentCalibrationTopic: NetworkTablesTopic<string> = ntcore.createTopic('current_calibration', NetworkTablesTypeInfos.kString)
    currentCalibrationTopic.subscribe(v => {
      if (v !== null) {
        currentCalibration.value = v
        console.log('new calib: ' + v)
      }
    }, true)
    updateText()
    watch(currentCalibration, updateText)
  })
</script>

<template>
  <v-card border class="ma-2">
    <template #title>
      <span class="font-weight-black">Calibration</span>
    </template>
    <template #append>
      <new-calibration />
    </template>
    <v-divider />
    <v-card-text>
      <v-row dense>
        <v-col cols="12" md="6" sm="12">
          <h2>Current Calibration (Applied)</h2>
          <pre class="scrollable-text my-2">{{ text }}</pre>
          <v-select v-model="imageSelection" :items="images" variant="outlined" />
          <v-img class="svg-background" :src="imgSrc" />
        </v-col>
        <!--        <v-col cols="12" md="8" sm="12" />-->
      </v-row>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.scrollable-text {
  overflow-x: auto;
}
.svg-background {
  background-color: white;
}
</style>
