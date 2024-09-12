<script setup lang="ts">
  const calibrationDialog = ref(false)
  const page = ref(1)
</script>

<template>
  <v-btn
    class="text-capitalize"
    color="primary"
    text="New Calibration"
    variant="flat"
    @click="calibrationDialog = true; page = 1"
  />

  <v-dialog v-model="calibrationDialog" max-width="600" min-width="300" opacity="5%">
    <v-card border>
      <template #title>
        <span>Calibrate Camera</span>
      </template>
      <v-divider />
      <div class="ma-2">
        <CameraStream v-if="page < 3" />
        <CameraOptions v-if="page === 1" />
        <div v-if="page === 2" class="my-2">
          <v-btn
            block
            class="text-none"
            color="primary"
            prepend-icon="mdi-camera"
            text="Capture Image"
            variant="flat"
            @click=""
          />
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
          text="Back"
          @click="page--"
        />
        <v-btn
          v-if="page < 3"
          class="text-none"
          color="primary"
          text="Next"
          variant="flat"
          @click="page++"
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
