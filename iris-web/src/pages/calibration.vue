<script setup lang="ts">
  import axios from 'axios'
  import { onMounted } from 'vue'

  const data = ref({})

  const reload = function () {
    axios.get('/api/get-calibrations').then(response => { data.value = response.data }).catch(error => { console.log(error) })
  }

  const swapCalibration = async () => {
    await axios.post('/api/swap-calibrations')
    reload()
  }

  onMounted(() => {
    reload()
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
              text="Swap with staged"
              variant="flat"
              @click="swapCalibration"
            />
          </template>
          <v-divider />
          <calibration-info calibration-name="current" :json-data="data" />
        </v-card>
      </v-col>
      <v-col cols="12" md="6" sm="12">
        <v-card border>
          <template #title>
            <span class="font-weight-black">Staged Calibration</span>
          </template>
          <template #append>
            <new-calibration />
          </template>
          <v-divider />
          <calibration-info calibration-name="staged" :json-data="data" />
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<style scoped>
</style>
