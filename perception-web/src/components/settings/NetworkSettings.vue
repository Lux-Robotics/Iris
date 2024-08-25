<template>
  <h2 class="mb-3">Networking Setup</h2>
  <v-card variant="elevated">
    <template #text>
      <h3>Team Number</h3>
      <span>This is used to determine the address of the NetworkTables instance to publish results to. Alternatively, enter an IP address or hostname if you are not using Perception with a roboRio.</span>
      <v-spacer class="my-2" />
      <v-text-field
        v-model="robotServerIP"
        density="compact"
        :rules="rules"
        variant="outlined"
        @input="validate"
      >
        <template #append-inner>
          <v-slide-y-transition>
            <v-btn
              v-if="robotServerIP !== robotServerIPRef"
              class="text-capitalize"
              color="secondary"
              density="compact"
              :disabled="!backendConnected || !ipValid"
              slim
              text="save"
              variant="tonal"
              @click="updateServerIP"
            />
          </v-slide-y-transition>
        </template>
      </v-text-field>
      <v-divider class="mb-4" />
      <div class="edit-settings">
        <div>
          <h3>Hostname</h3>
          <span>
            PeninsulaPerception is using the hostname "perception.local". This will be the camera name sent to the robot and you can access this dashboard at "http://perception.local:5800"
          </span>
        </div>
        <v-btn class="text-capitalize" color="secondary" text="Edit Hostname" variant="tonal" />
      </div>
      <v-divider class="my-4" />
      <div class="edit-settings">
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
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue'
  import { NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { backendConnected, ntcore } from '@/nt-listener'

  const robotServerIP = ref('')
  const robotServerIPRef = ref('')
  const ipValid = ref(false)

  const robotServerIPTopic: NetworkTablesTopic<number> = ntcore.createTopic('teamNumber', NetworkTablesTypeInfos.kInteger)

  const updateServerIP = () => {
    if (backendConnected.value) {
      robotServerIPTopic.publish()
      robotServerIPTopic.setValue(parseInt(robotServerIP.value))
    }
  }

  const rules = [
    v => !!v || 'Number is required',
    v => (v && !isNaN(v)) || 'Must be a number',
    v => (v && v >= 1 && v <= 25599) || 'Team must be between 1 and 25599',
  ]

  const validate = () => {
    for (const rule of rules) {
      const result = rule(robotServerIP.value)
      if (result !== true) {
        ipValid.value = false
        return
      }
    }
    ipValid.value = true
  }

  onMounted(() => {
    robotServerIPTopic.subscribe(v => {
      if (v !== null && robotServerIPRef.value !== v.toString()) {
        robotServerIP.value = v.toString()
        robotServerIPRef.value = v.toString()
      }
    }, true)
  })

</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active in <2.1.8 */ {
  opacity: 0;
}
</style>
