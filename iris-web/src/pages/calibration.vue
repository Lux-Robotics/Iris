<script setup lang="ts">
  import { apiPort, backendURI } from '@/nt-listener'
  import axios from 'axios'

  const calibrationDialog = ref(false)
  const page = ref(1)

  async function takeSnapshot () {
    await axios.post('https://' + backendURI + ':' + apiPort + '/api/take-snapshot')
  }

  // async function clearSnapshots () {
  //   await axios.post('https://' + backendURI + ':' + apiPort + '/api/clear-snapshots')
  // }

  async function calibrate () {
    await axios.post('https://' + backendURI + ':' + apiPort + '/api/calibrate')
    page.value += 1
  }
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
          text="Back"
          @click="page--"
        />
        <v-btn
          v-if="page < 3"
          class="text-none"
          color="primary"
          text="Calibrate"
          variant="flat"
          @click="calibrate"
        />
        <v-btn
          v-if="page === 3"
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

<style scoped></style>
