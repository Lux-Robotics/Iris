<template>
  <v-card elevation="12" rounded="lg" min-width="400" max-width="700">
    <v-toolbar density="compact" title="Camera Options"> </v-toolbar>
    <div class="px-4 py-4">

      <v-select label="Orientation" :items="['Normal', '90°', '180°', '270°']" variant="outlined"
        class="ma-4"></v-select>

      <v-slider v-model="brightness" :max="255" :step="1" class="ma-4" label="Brightness" hide-details>
        <template v-slot:append>
          <v-text-field v-model="brightness" density="compact" style="width: 80px" type="number" variant="outlined"
            hide-details></v-text-field>
        </template>
      </v-slider>
      <v-slider v-model="exposure" :max="255" :step="1" class="ma-4" label="Exposure" hide-details>
        <template v-slot:append>
          <v-text-field v-model="exposure" density="compact" style="width: 80px" type="number" variant="outlined"
            hide-details></v-text-field>
        </template>
      </v-slider>
      <v-slider v-model="gain" :max="255" :step="1" class="ma-4" label="Sensor Gain" hide-details>
        <template v-slot:append>
          <v-text-field v-model="gain" density="compact" style="width: 80px" type="number" variant="outlined"
            hide-details></v-text-field>
        </template>
      </v-slider>
    </div>
  </v-card>
</template>

<script>
export default {
  data() {
    return {
      brightness: 50, // Initial slider value
      exposure: 50, // Initial slider value
      gain: 50, // Initial slider value
    };
  },
};
</script>