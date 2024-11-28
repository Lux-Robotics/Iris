<script setup lang="ts">
  import { apiURI, ntcore } from '@/nt-listener'
  import axios from 'axios'
  import { NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { onMounted, watch } from 'vue'

  const currentCalibration = ref(0)
  const text = ref('No calibrations loaded')
  const imageSelection = ref('projection_uncertainty.png')
  const imgSrc = computed<string>(() => {
    return apiURI + '/calibrations/slot' + currentCalibration.value + '/' + imageSelection.value
  })

  const images = [
    { title: 'Projection Uncertainty', value: 'projection_uncertainty.png' },
    { title: 'Distortion', value: 'distortion.png' },
    { title: 'Residuals', value: 'residuals.png' },
    { title: 'Valid Intrinsics Region', value: 'valid_intrinsics_region.png' },
  ]

  async function updateText () {
    try {
      const response = await axios.get(apiURI + '/calibrations/slot' + currentCalibration.value + '/calibration.toml', {
        responseType: 'text', // Ensure the response is treated as text
      })
      text.value = response.data
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  }

  onMounted(() => {
    const currentCalibrationTopic: NetworkTablesTopic<number> = ntcore.createTopic('current_calibration', NetworkTablesTypeInfos.kInteger)
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
  <div class="pa-2 scrollable-area">
    <v-row dense>
      <v-col cols="12" md="6" sm="12">
        <v-card border>
          <template #title>
            <span class="font-weight-black">Current Calibration (Applied)</span>
          </template>
          <template #append>
            <v-btn
              class="text-capitalize"
              color="primary"
              text="Swap with latest"
              variant="flat"
            />
          </template>
          <v-divider />
          <v-card-text>
            <pre class="scrollable-text my-2">{{ text }}</pre>
            <v-select v-model="imageSelection" :items="images" variant="outlined" />
            <v-img class="svg-background" :src="imgSrc" />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" sm="12">
        <v-card border>
          <template #title>
            <span class="font-weight-black">Latest Calibration</span>
          </template>
          <template #append>
            <new-calibration />
          </template>
          <v-divider />
          <v-card-text>
            <pre class="scrollable-text my-2">{{ text }}</pre>
            <v-select v-model="imageSelection" :items="images" variant="outlined" />
            <v-img class="svg-background" :src="imgSrc" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<style scoped>
.scrollable-text {
  overflow-x: auto;
}
.svg-background {
  background-color: white;
}
</style>
