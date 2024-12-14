<script setup lang="ts"></script>

<template>
  <v-card border min-width="300">
    <!--  <v-card color="background" min-width="300" variant="flat">-->
    <template #title>
      <span class="font-weight-black">Camera Options</span>
    </template>
    <v-divider />
    <v-card-text>
      <CameraOptions />
    </v-card-text>
  </v-card>
</template>

<style scoped></style>
