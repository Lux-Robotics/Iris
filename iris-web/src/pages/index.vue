<template>
  <div class="scrollable-area pa-2">
    <v-row dense>
      <v-col lg="8" md="12" sm="12">
        <CameraCard />
      </v-col>
      <v-col lg="4" md="12" sm="12">
        <CameraOptionsCard />
        <v-spacer class="py-1" />
        <AprilTagOptions />
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts" setup>
</script>

<style scoped>
</style>
