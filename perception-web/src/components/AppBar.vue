<template>
  <v-app-bar density="compact">
    <div class="d-lg-none">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
    </div>
    <v-app-bar-title>Peninsula Perception</v-app-bar-title>
    <v-btn prepend-icon="mdi-power"> Restart Service </v-btn>
    <v-btn prepend-icon="mdi-power"> Restart Device </v-btn>
  </v-app-bar>
  <v-navigation-drawer v-model="drawer">
    <v-list>
      <v-list-item link prepend-icon="mdi-view-dashboard" title="Dashboard" to="/" />
      <v-list-item link prepend-icon="mdi-grid" title="Camera Calibration" to="/calibration" />
      <v-list-item link prepend-icon="mdi-file" title="Logs" to="/logs" />
      <v-list-item link prepend-icon="mdi-book-open" title="Documentation" to="/docs" />
      <v-list-item link prepend-icon="mdi-cog" title="Settings" to="/settings" />
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
  import { ref } from 'vue'

  const drawer = ref(null)
</script>
