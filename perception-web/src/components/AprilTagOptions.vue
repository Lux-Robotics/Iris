<template>
  <v-card
    elevation="12"
    rounded="lg"
    min-width="350"
    >
    <v-toolbar
      density="compact"
      title="Apriltag"
      > </v-toolbar>
    <div
      class="px-4 py-4"
      >

      <v-select
        label="AprilTag Family"
        :items="['36h11', '25h9', '16h5']"
        variant="outlined"
        class="ma-4"
      ></v-select>


      <v-slider
        v-model="decimate"
        :max="3"
        :step="0.5"
        class="ma-4"
        label="Decimate"
        hide-details
      >
        <template v-slot:append>
          <v-text-field
            v-model="decimate"
            density="compact"
            style="width: 80px"
            type="number"
            variant="outlined"
            hide-details
          ></v-text-field>
        </template>
      </v-slider>
      <v-slider
        v-model="blur"
        :max="4"
        :step="1"
        class="ma-4"
        label="Gaussian Blur"
        hide-details
      >
        <template v-slot:append>
          <v-text-field
            v-model="blur"
            density="compact"
            style="width: 80px"
            type="number"
            variant="outlined"
            hide-details
          ></v-text-field>
        </template>
      </v-slider>
      <v-slider
        v-model="nthreads"
        :max="8"
        :step="1"
        class="ma-4"
        label="CPU Threads"
        hide-details
      >
        <template v-slot:append>
          <v-text-field
            v-model="nthreads"
            density="compact"
            style="width: 80px"
            type="number"
            variant="outlined"
            hide-details
          ></v-text-field>
        </template>
      </v-slider>

      <v-switch 
        label="Refine Edges"
        class="ma-4"
        hide-details
      ></v-switch>
      </div>
  </v-card>
</template>

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