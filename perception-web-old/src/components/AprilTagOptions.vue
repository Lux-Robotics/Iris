<template>
  <v-card elevation="12" rounded="lg" min-width="350">
    <v-toolbar density="compact" title="Apriltag"> </v-toolbar>
    <div class="px-4 py-4">

      <v-select label="AprilTag Family" :items="['36h11', '25h9', '16h5']" variant="outlined" class="ma-4"></v-select>


      <v-slider v-model="decimate" :max="3" :step="0.5" class="ma-4" hide-details>
        <template v-slot:label>
          <span class="slider-label">Decimate</span>
        </template>
        <template v-slot:append>
          <v-text-field v-model="decimate" density="compact" style="width: 80px" type="number" variant="outlined"
            hide-details></v-text-field>
        </template>
      </v-slider>
      <v-slider v-model="blur" :max="4" :step="1" class="ma-4" hide-details>
        <template v-slot:label>
          <span class="slider-label">Gaussian Blur</span>
        </template>
        <template v-slot:append>
          <v-text-field v-model="blur" density="compact" style="width: 80px" type="number" variant="outlined"
            hide-details></v-text-field>
        </template>
      </v-slider>
      <v-slider v-model="nthreads" :max="8" :step="1" class="ma-4" hide-details>
        <template v-slot:label>
          <span class="slider-label">CPU Threads</span>
        </template>
        <template v-slot:append>
          <v-text-field v-model="nthreads" density="compact" style="width: 80px" type="number" variant="outlined"
            hide-details></v-text-field>
        </template>
      </v-slider>

      <v-switch class="ma-4" hide-details>
        <template v-slot:label>
          <span class="switch-label">Refine Edges</span>
        </template>
      </v-switch>
    </div>
  </v-card>
</template>

<style>
.slider-label {
  display: inline-block;
  width: 200px;
}
</style>

<script>
export default {
  data() {
    return {
      decimate: 1.0, // Initial slider value
      blur: 0, // Initial slider value
      nthreads: 4, // Initial slider value
    };
  },
};
</script>