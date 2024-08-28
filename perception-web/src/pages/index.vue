<template>
  <div class="ma-2">
    <v-row dense>
      <v-col cols="12" md="7">
        <CameraStream />
      </v-col>
      <v-col cols="12" md="5">
        <v-row dense>
          <v-col cols="12">
            <AprilTagOptions />
          </v-col>
          <v-col cols="12">
            <Graph />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts" setup>
//
</script>
