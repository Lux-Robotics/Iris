<script setup lang="ts"></script>

<template>
  <v-spacer class="my-3" />
  <v-card border variant="elevated">
    <template #text>
      <div class="edit-settings">
        <div>
          <h3>AprilTag Layout</h3>
          <span>Compatible with </span>
          <a
            href="https://github.com/wpilibsuite/allwpilib/tree/main/apriltag/src/main/native/resources/edu/wpi/first/apriltag"
            target="_blank"
            >WPILib .json field maps</a
          >
        </div>
        <v-spacer />
        <v-btn
          class="text-none"
          color="primary"
          text="Manage Layouts"
          variant="flat"
        />
      </div>
    </template>
  </v-card>
</template>

<style scoped></style>
