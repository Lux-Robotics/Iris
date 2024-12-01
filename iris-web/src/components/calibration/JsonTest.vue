<template>
  <json-display :json-data="exampleData" title="Camera Configuration" />
</template>

<script>
  import JsonDisplay from '@/components/calibration/CalibrationData.vue'
  import { defineComponent } from 'vue'

  export default defineComponent({
    name: 'JsonTest',
    components: {
      JsonDisplay,
    },
    setup () {
      const exampleData = {
        lensmodel: 'LENSMODEL_OPENCV8',
        resolution: [640, 480],
        cameraMatrix: [
          [369.9894827, 0, 340.9537583],
          [0, 444.684046, 232.2065861],
          [0, 0, 1],
        ],
        distCoeffs: [
          -0.1851498102,
          0.04186957023,
          0.0008163433465,
          0.001160433211,
          0.3773219996,
          -0.2963804692,
          0.2419370985,
          0.3086207349,
        ],
        rms_reprojection_error: 0.2,
        worst_residual: 0.9,
      }

      return {
        exampleData,
      }
    },
  })
</script>
