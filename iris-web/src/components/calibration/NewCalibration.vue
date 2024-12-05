<script setup lang="ts">
  import { ntcore } from '@/nt-listener'
  import axios from 'axios'
  import { NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { onMounted } from 'vue'

  const calibrationDialog = ref(false)
  const page = ref(1)
  const progress = ref(0)
  const failed = ref(false)
  const numSnapshots = ref(0)

  function takeSnapshot () {
    axios
      .post('/api/take-snapshot', {})
      .then(response => {
        console.log(response.data)
      })
      .catch(error => {
        console.error('Error occurred:', error)
      })
  }

  function clearSnapshots () {
    axios
      .post('/api/clear-snapshots', {})
      .then(response => {
        console.log(response.data)
      })
      .catch(error => {
        console.error('Error occurred:', error)
      })
  }

  function calibrate () {
    axios
      .post('/api/calibrate', {})
      .then(response => {
        console.log(response.data)
      })
      .catch(error => {
        console.error('Error occurred:', error)
      })
    page.value += 1
  }

  function cancelCalibration () {
    clearSnapshots()
    calibrationDialog.value = false
  }

  function saveCalibration () {
    clearSnapshots()
    axios.post('/api/save-calibration')
    calibrationDialog.value = false
  }

  onMounted(() => {
    const progressTopic: NetworkTablesTopic<number> = ntcore.createTopic(
      'calibrationProgress',
      NetworkTablesTypeInfos.kInteger,
    )
    const failProgressTopic: NetworkTablesTopic<boolean> = ntcore.createTopic(
      'calibrationFailed',
      NetworkTablesTypeInfos.kInteger,
    )
    const snapshotsTopic: NetworkTablesTopic<string[]> = ntcore.createTopic(
      'snapshots',
      NetworkTablesTypeInfos.kStringArray,
    )

    progressTopic.subscribe(v => {
      if (v !== null) {
        progress.value = v
      }
    })
    failProgressTopic.subscribe(v => {
      if (v !== null) {
        failed.value = v
      }
    })
    snapshotsTopic.subscribe(v => {
      if (v !== null) {
        numSnapshots.value = v.length
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
      <v-window v-model="page">
        <v-progress-linear
          v-if="page===2"
          :bg-opacity="0"
          color="primary"
          height="6"
          :indeterminate="progress !== 4 && !failed"
        />
        <div class="ma-2">
          <v-window-item :value="1">
            <v-row dense>
              <v-col cols="12" md="8" sm="12">
                <CameraStream />
              </v-col>
              <v-col cols="12" md="4" sm="12">
                <v-btn
                  block
                  class="text-none"
                  color="primary"
                  prepend-icon="mdi-camera"
                  :text="'Take Snapshot [' + numSnapshots.toString() + '/12]'"
                  variant="flat"
                  @click="takeSnapshot"
                />
                <v-spacer class="py-2" />
                <CameraOptions />
              </v-col>
            </v-row>
          </v-window-item>
          <v-window-item :value="2">
            <v-stepper
              elevation="0"
              :model-value="progress"
            >
              <v-stepper-header v-if="$vuetify.display.mdAndUp">
                <v-stepper-item
                  color="primary"
                  :complete="progress>0"
                  :error="progress === 0 && failed"
                  title="Compute Corners"
                  value="1"
                />

                <v-divider />

                <v-stepper-item
                  color="primary"
                  :complete="progress>1"
                  :error="progress === 1 && failed"
                  title="Solve"
                  value="2"
                />

                <v-divider />

                <v-stepper-item
                  color="primary"
                  :complete="progress>2"
                  :error="progress === 2 && failed"
                  title="Convert Calibration"
                  value="3"
                />

                <v-divider />

                <v-stepper-item
                  color="primary"
                  :complete="progress>3"
                  :error="progress === 3 && failed"
                  title="Generate Graphs"
                  value="4"
                />
              </v-stepper-header>
              <div v-if="$vuetify.display.smAndDown">
                <v-stepper-item
                  color="primary"
                  :complete="progress>0"
                  :error="progress === 0 && failed"
                  title="Compute Corners"
                  value="1"
                />

                <v-divider />

                <v-stepper-item
                  color="primary"
                  :complete="progress>1"
                  :error="progress === 1 && failed"
                  title="Solve"
                  value="2"
                />

                <v-divider />

                <v-stepper-item
                  color="primary"
                  :complete="progress>2"
                  :error="progress === 2 && failed"
                  title="Convert Calibration"
                  value="3"
                />

                <v-divider />

                <v-stepper-item
                  color="primary"
                  :complete="progress>3"
                  :error="progress === 3 && failed"
                  title="Generate Graphs"
                  value="4"
                />
              </div>
            </v-stepper>
          </v-window-item>
        </div>
      </v-window>
      <v-divider />
      <template #actions>
        <v-btn
          v-if="page === 1"
          class="text-none"
          color="error"
          text="Cancel"
          @click="cancelCalibration"
        />
        <v-btn
          v-if="page > 1"
          class="text-none"
          color="error"
          :disabled="progress < 4"
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
          :disabled="progress < 4"
          text="Save"
          variant="flat"
          @click="saveCalibration"
        />
      </template>
    </v-card>
  </v-dialog>
</template>

<style scoped>
</style>
