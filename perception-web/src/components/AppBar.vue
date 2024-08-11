<template>
  <v-app-bar
    density="compact">
    <div class="d-lg-none">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
    </div>
    <v-app-bar-title>Peninsula Perception</v-app-bar-title>
    <v-btn prepend-icon="mdi-power"> Restart Service </v-btn>
    <v-btn prepend-icon="mdi-power"> Restart Device </v-btn>
  </v-app-bar>
  <v-navigation-drawer v-model="drawer">
    <v-list-item prepend-icon="mdi-view-dashboard" link title="Dashboard"></v-list-item>
    <v-list-item prepend-icon="mdi-grid" link title="Camera Calibration"></v-list-item>
    <v-list-item prepend-icon="mdi-file" link title="Logs"></v-list-item>
    <v-list-item prepend-icon="mdi-book-open" link title="Documentation"></v-list-item>
    <v-list-item prepend-icon="mdi-cog" link title="Settings"></v-list-item>
  </v-navigation-drawer>
</template>

<script setup>
  import { ref } from 'vue'

  const drawer = ref(null)
</script>

<script>
  export default {
    data: () => ({ drawer: null }),
  }
</script>
