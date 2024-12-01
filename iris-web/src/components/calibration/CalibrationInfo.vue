<script setup lang="ts">
  import CalibrationData from '@/components/calibration/CalibrationData.vue'
  import { apiURI } from '@/nt-listener'
  import { computed, ref, watch } from 'vue'

  // Use defineProps to define props in <script setup>
  const props = defineProps<{
    readonly calibrationName: string;
    readonly jsonData: any
  }>()

  // Ensure imageSelection and imgSrc are correctly defined
  const imageSelection = ref('projection_uncertainty.png')

  const imgSrc = computed(() => {
    return `${apiURI}/calibrations/${props.calibrationName}/${imageSelection.value}`
  })

  const calibrationJson = ref(null)

  watch(
    () => props.jsonData,
    newJsonData => {
      if (newJsonData && newJsonData.hasOwnProperty(props.calibrationName)) {
        // Update the reactive data when jsonData or keyName changes
        calibrationJson.value = newJsonData[props.calibrationName]
      } else {
        calibrationJson.value = null // Handle missing key scenario
      }
    },
    { immediate: true } // Run the watcher immediately after initialization
  )

  const images = [
    { title: 'Projection Uncertainty', value: 'projection_uncertainty.png' },
    { title: 'Distortion', value: 'distortion.png' },
    { title: 'Residuals', value: 'residuals.png' },
    { title: 'Valid Intrinsics Region', value: 'valid_intrinsics_region.png' },
  ]
</script>

<template>
  <div v-if="calibrationJson !== null">
    <CalibrationData :calibration-json="calibrationJson" />
    <v-divider />
    <v-card-text>
      <v-select v-model="imageSelection" :items="images" variant="outlined" />
      <v-img class="svg-background" :src="imgSrc" />
    </v-card-text>
  </div>
  <div v-else>
    <v-card-text>
      Unable to load {{ calibrationName }} calibration
    </v-card-text>
  </div>
</template>

<style scoped>
.svg-background {
  background-color: white;
}
</style>
