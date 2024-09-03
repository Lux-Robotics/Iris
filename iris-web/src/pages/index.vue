<template>
  <v-container fluid max-width="1600">
    <v-row dense>
      <v-col lg="8" md="12" sm="12">
        <CameraStream />
      </v-col>
      <v-col lg="4" md="12" sm="12">
        <AprilTagOptions />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
//
</script>

<style>
.constant-width {
  max-width: 1800px; /* Set a constant width here, adjust as needed */
  flex: 0 0 auto;
}
</style>
