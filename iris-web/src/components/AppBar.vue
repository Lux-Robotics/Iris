<template>
  <v-app-bar border color="surface" density="compact" elevation="0">
    <template #prepend>
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-icon icon="mdi-camera-iris" />
      <span class="mx-2 font-weight-black">Iris</span>
      <span class="text-grey-lighten-1">v2024.4.3</span>
    </template>
    <v-btn color="red" prepend-icon="mdi-restart">Restart Service</v-btn>
    <v-btn color="red" prepend-icon="mdi-power" variant="outlined">Restart Device</v-btn>
  </v-app-bar>
  <v-navigation-drawer v-model="drawer" color="background" mobile-breakpoint="md" width="250">
    <v-list>
      <v-list-item link prepend-icon="mdi-camera" title="Dashboard" to="/" />
      <v-list-item link prepend-icon="mdi-grid" title="Camera Calibration" to="/calibration" />
      <v-list-item link prepend-icon="mdi-file" title="Logs" to="/logs" />
      <!--      <v-list-item link prepend-icon="mdi-book-open" title="Documentation" to="/docs" />-->
      <v-list-item link prepend-icon="mdi-cog" title="Settings" to="/settings" />
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue'
  import { useDisplay } from 'vuetify'

  const drawer = ref(false)

  onMounted(() => {
    drawer.value = useDisplay().mdAndUp.value
  })
</script>

<style scoped>
.v-list-item--active {
  background-color: #5A4FCF !important; /* Your accent color */
  color: white !important;
}
</style>
