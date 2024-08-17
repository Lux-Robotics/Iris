<template>
  <v-card elevation="12" min-width="350" rounded="lg">
    <v-toolbar density="compact" title="Apriltag" />
    <div class="px-4 py-4">

      <v-select class="ma-4" :items="['36h11', '25h9', '16h5']" label="AprilTag Family" variant="outlined" />

      <v-slider
        v-model="decimate"
        class="ma-4"
        hide-details
        :max="3"
        :step="0.5"
      >
        <template #label>
          <span class="slider-label">Decimate</span>
        </template>
        <template #append>
          <v-text-field
            v-model="decimate"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>
      <v-slider
        v-model="blur"
        class="ma-4"
        hide-details
        :max="4"
        :step="1"
      >
        <template #label>
          <span class="slider-label">Gaussian Blur</span>
        </template>
        <template #append>
          <v-text-field
            v-model="blur"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>
      <v-slider
        v-model="nthreads"
        class="ma-4"
        hide-details
        :max="8"
        :step="1"
      >
        <template #label>
          <span class="slider-label">CPU Threads</span>
        </template>
        <template #append>
          <v-text-field
            v-model="nthreads"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>

      <v-switch class="ma-4" hide-details>
        <template #label>
          <span class="switch-label">Refine Edges</span>
        </template>
      </v-switch>
    </div>
  </v-card>
</template>

<script>
  export default {
    data () {
      return {
        decimate: 1.0, // Initial slider value
        blur: 0, // Initial slider value
        nthreads: 4, // Initial slider value
      }
    },
  }
</script>

<style>
.slider-label {
  display: inline-block;
  width: 200px;
}
</style>
