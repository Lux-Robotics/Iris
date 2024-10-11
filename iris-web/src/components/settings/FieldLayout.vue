<script setup lang="ts">

</script>

<template>
  <h2 class="my-3">Field Layout</h2>
  <v-card border variant="elevated">
    <template #text>
      <div class="edit-settings">
        <div>
          <h3>Offline Software Update</h3>
          <span>Updates can be found at </span>
          <a href="https://github.com/" target="_blank">https://example.com/updates</a>
        </div>
        <v-spacer />
        <v-btn
          class="text-none"
          color="primary"
          text="Select Update .zip"
          variant="flat"
        />
      </div>
    </template>
  </v-card>
</template>

<style scoped>

</style>
