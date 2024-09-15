<script setup lang="ts">
  import { apiURI, ntcore } from '@/nt-listener'
  import axios from 'axios'
  import { NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { onMounted } from 'vue'

  const calibrationDialog = ref(false)
  const page = ref(1)
  const progress = ref(0)

  function takeSnapshot () {
    axios.post(apiURI + '/api/take-snapshot', {})
      .then(response => {
        console.log(response.data)
      })
      .catch(error => {
        console.error('Error occurred:', error)
      })
  }

  // async function clearSnapshots () {
  //   await axios.post('http://' + backendURI + ':' + apiPort + '/api/clear-snapshots')
  // }

  function calibrate () {
    axios.post(apiURI + '/api/calibrate', {})
      .then(response => {
        console.log(response.data)
      })
      .catch(error => {
        console.error('Error occurred:', error)
      })
    page.value += 1
  }

  onMounted(() => {
    const progressTopic: NetworkTablesTopic<number> = ntcore.createTopic('calibrationProgress', NetworkTablesTypeInfos.kInteger)
    progressTopic.subscribe(v => {
      if (v !== null) {
        progress.value = v
      }
    })
  })
</script>

<template>
  <v-btn
    class="text-capitalize"
    color="primary"
    text="New Calibration"
    variant="flat"
    @click="calibrationDialog = true; page = 1"
  />

  <v-dialog v-model="calibrationDialog" max-width="1200" min-width="300" opacity="5%">
    <v-card border>
      <template #title>
        <span>Calibrate Camera</span>
      </template>
      <v-divider />
      <div class="ma-2">
        <v-row v-if="page === 1" dense>
          <v-col cols="12" md="8" sm="12">
            <CameraStream />
          </v-col>
          <v-col cols="12" md="4" sm="12">
            <v-btn
              block
              class="text-none"
              color="primary"
              prepend-icon="mdi-camera"
              text="Take Snapshot"
              variant="flat"
              @click="takeSnapshot"
            />
            <v-spacer class="py-2" />
            <CameraOptions />
          </v-col>
        </v-row>
        <div v-if="page === 2">
          <v-stepper elevation="0" :model-value="progress">
            <v-stepper-header v-if="$vuetify.display.mdAndUp">
              <v-stepper-item
                color="primary"
                :complete="progress>0"
                title="Compute Corners"
                value="1"
              />

              <v-divider />

              <v-stepper-item
                color="primary"
                :complete="progress>1"
                title="Solve"
                value="2"
              />

              <v-divider />

              <v-stepper-item
                color="primary"
                :complete="progress>2"
                title="Convert Calibration"
                value="3"
              />

              <v-divider />

              <v-stepper-item
                color="primary"
                :complete="progress>3"
                title="Generate Graphs"
                value="4"
              />
            </v-stepper-header>
            <div v-if="$vuetify.display.smAndDown">
              <v-stepper-item
                color="primary"
                :complete="progress>0"
                title="Compute Corners"
                value="1"
              />

              <v-divider />

              <v-stepper-item
                color="primary"
                :complete="progress>1"
                title="Solve"
                value="2"
              />

              <v-divider />

              <v-stepper-item
                color="primary"
                :complete="progress>2"
                title="Convert Calibration"
                value="3"
              />

              <v-divider />

              <v-stepper-item
                color="primary"
                :complete="progress>3"
                title="Generate Graphs"
                value="4"
              />
            </div>
          </v-stepper>
          <v-container v-if="progress === 4" max-width="800">
            <v-img
              class="svg-background"
              :src="apiURI + '/processed-calibration/projection_uncertainty.svg'"
            />
          </v-container>
        </div>
      </div>
      <v-divider />
      <template #actions>
        <v-btn
          v-if="page === 1"
          class="text-none"
          color="error"
          text="Cancel"
          @click="calibrationDialog = false"
        />
        <v-btn
          v-if="page > 1"
          class="text-none"
          color="error"
          text="Restart Calibration"
          @click="page--"
        />
        <v-btn
          v-if="page === 1"
          class="text-none"
          color="primary"
          text="Calibrate"
          variant="flat"
          @click="calibrate"
        />
        <v-btn
          v-if="page === 2"
          class="text-none"
          color="primary"
          text="Save"
          variant="flat"
          @click="calibrationDialog = false"
        />
      </template>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.svg-background {
  background-color: white;
}
</style>
