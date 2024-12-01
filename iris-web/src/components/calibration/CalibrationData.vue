<template>
  <v-table>
    <tbody>
      <tr>
        <td>Lens Model</td>
        <td>{{ props.calibrationJson.lensmodel }}</td>
      </tr>
      <tr>
        <td>Reprojection Error</td>
        <td>{{ props.calibrationJson.rms_reprojection_error }}px</td>
      </tr>
      <tr>
        <td>Worst Residual</td>
        <td>{{ props.calibrationJson.worst_residual }}px</td>
      </tr>
    </tbody>
  </v-table>
</template>

<script setup lang="ts">
  const props = defineProps<{
    readonly calibrationJson: any
  }>()

</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
