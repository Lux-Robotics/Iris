<script lang="ts" setup>
//
</script>

<template>
  <div>
    <v-container max-width="800px" min-width="400">
      <h2>Networking Setup</h2>
      <v-card variant="elevated">
        <template #text>
          <h3>Team number</h3>
          <span>This is used to determine the address of the NetworkTables instance to publish results to. Alternatively, enter an IP address or hostname if you are not using Perception with a roboRio.</span>
          <v-spacer class="my-2" />
          <v-text-field density="compact" variant="outlined">
            <template #append-inner>
              <v-btn
                class="text-capitalize"
                color="secondary"
                density="compact"
                slim
                text="save"
                variant="tonal"
              />
            </template>
          </v-text-field>
          <v-divider class="mb-4" />
          <div class="settings-button">
            <div>
              <h3>Hostname</h3>
              <span>
                PeninsulaPerception is using the hostname "perception.local". This will be the camera name sent to the robot and you can access this dashboard at "http://perception.local:5800"
              </span>
            </div>
            <v-btn class="text-capitalize" color="secondary" text="Edit Hostname" variant="tonal" />
          </div>
          <v-divider class="my-4" />
          <div class="settings-button">
            <div>
              <h3>IP Configuration</h3>
              <span>
                PeninsulaPerception uses a dynamic IP address by default. However, a static IP address reduces boot time and leads to more stable connections.
              </span>
            </div>
            <v-btn class="text-capitalize" color="secondary" text="Edit IP configuration" variant="tonal" />
          </div>
        </template>
      </v-card>

      <v-spacer class="my-3" />

      <h2>About</h2>
      <v-card variant="elevated">
        <v-table>
          <tbody>
            <tr>
              <td>Hardware Model</td>
              <td>Unknown</td>
            </tr>
            <tr>
              <td>Uptime</td>
              <td>Unknown</td>
            </tr>
            <tr>
              <td>Hardware Model</td>
              <td>Unknown</td>
            </tr>
            <tr>
              <td>Version</td>
              <td>v2024.4.3</td> </tr>
            <tr>
              <td>Git Commit Hash</td>
              <td>40034ee</td>
            </tr>
          </tbody>
        </v-table>
      </v-card>

      <v-spacer class="my-3" />

      <v-card>
        <template #text>
          <div class="settings-button">
            <div>
              <h3>Offline Software Update</h3>
              <span>Updates can be found at </span>
              <a href="https://github.com" target="_blank">https://example.com/updates</a>
            </div>
            <v-spacer />
            <v-btn
              class="text-none"
              color="secondary"
              text="Select Update .zip"
              variant="tonal"
            />
          </div>
        </template>
      </v-card>

    </v-container>
  </div>
</template>

<style scoped>
.settings-button {
  display: flex;
  align-items: center;
  gap: 10px; /* optional: space between components */
}
</style>
