<template>
  <h2 class="mb-3">Networking Setup</h2>
  <v-card border variant="elevated">
    <template #text>
      <h3>Team Number</h3>
      <span
        >This is used to determine the address of the NetworkTables instance to
        publish results to. Alternatively, enter an IP address or hostname if
        you are not using Iris with a roboRio.</span
      >
      <v-spacer class="my-2" />
      <v-text-field
        v-model="robotServerIP"
        density="compact"
        :rules="rules"
        variant="outlined"
        @blur="robotServerIP = robotServerIPRef"
        @input="validate"
      >
        <template #append-inner>
          <v-slide-y-transition>
            <div
              v-if="robotServerIP !== robotServerIPRef"
              class="edit-settings"
            >
              <v-btn
                class="text-capitalize"
                color="error"
                density="compact"
                slim
                text="undo"
                variant="elevated"
                @click="robotServerIP = robotServerIPRef"
              />
              <v-btn
                v-if="robotServerIP !== robotServerIPRef"
                class="text-capitalize"
                color="primary"
                density="compact"
                :disabled="!backendConnected || !ipValid"
                slim
                text="save"
                variant="elevated"
                @click="updateServerIP"
              />
            </div>
          </v-slide-y-transition>
        </template>
      </v-text-field>
      <v-divider class="mb-4" />
      <div class="edit-settings">
        <div>
          <h3>Hostname</h3>
          <span>
            Iris is using the hostname "iris.local". This will be the camera
            name sent to the robot and you can access this dashboard at
            "http://iris.local"
          </span>
        </div>
        <v-btn
          class="text-capitalize"
          color="primary"
          text="Edit Hostname"
          variant="flat"
          @click="hostnameDialog = true"
        />
      </div>
      <v-dialog v-model="hostnameDialog" opacity="15%" width="auto">
        <v-card
          max-width="300"
          min-width="300"
          prepend-icon="mdi-router-network"
          subtitle="Applied after device restart"
          title="Hostname"
        >
          <template #default>
            <v-text-field
              v-model="hostname"
              class="mx-6"
              label="New hostname"
              placeholder="iris"
              suffix=".local"
              variant="underlined"
            />
          </template>
          <template #actions>
            <v-btn
              class="text-none"
              color="error"
              text="Cancel"
              @click="hostnameDialog = false"
            />
            <v-btn
              class="text-none"
              color="primary"
              text="Save"
              variant="flat"
              @click="
                hostnameDialog = false;
                requestHostnameUpdate();
              "
            />
          </template>
        </v-card>
      </v-dialog>
      <v-divider class="my-4" />
      <div class="edit-settings">
        <div>
          <h3>IP Configuration</h3>
          <span>
            Iris uses a dynamic IP address by default. However, a static IP
            address reduces boot time and leads to more stable connections.
          </span>
        </div>
        <v-btn
          class="text-capitalize"
          color="primary"
          text="Edit IP configuration"
          variant="flat"
          @click="IPDialog = true"
        />
      </div>
      <v-dialog v-model="IPDialog" opacity="15%" width="auto">
        <v-card
          max-width="300"
          min-width="300"
          prepend-icon="mdi-router-network"
          subtitle="Applied after device restart"
          title="Update IP Configuration"
        >
          <template #default>
            <v-select
              v-model="ipAssignmentMethod"
              class="mx-6"
              :items="[
                { title: 'DHCP', value: 'dhcp' },
                { title: 'Static', value: 'static' },
                { title: 'Static (Advanced)', value: 'static-advanced' },
              ]"
              label="IP Assignment Mode"
              variant="underlined"
            />
            <v-text-field
              class="mx-6"
              :disabled="ipAssignmentMethod === 'dhcp'"
              label="IP address"
              :prefix="ipPrefix"
              variant="underlined"
            />
            <v-text-field
              v-if="ipAssignmentMethod === 'static-advanced'"
              class="mx-6"
              label="Gateway"
              :prefix="ipPrefix"
              variant="underlined"
            />
            <v-text-field
              v-if="ipAssignmentMethod === 'static-advanced'"
              class="mx-6"
              label="Subnet mask"
              variant="underlined"
            />
          </template>
          <template #actions>
            <v-btn
              class="text-none"
              color="error"
              text="Cancel"
              @click="IPDialog = false"
            />
            <v-btn
              class="text-none"
              color="primary"
              text="Save"
              variant="flat"
              @click="IPDialog = false"
            />
          </template>
        </v-card>
      </v-dialog>
    </template>
  </v-card>
</template>

<script lang="ts" setup>
import axios from "axios";
import { computed, onMounted, ref } from "vue";
import { NetworkTablesTopic, NetworkTablesTypeInfos } from "ntcore-ts-client";
import { apiURI, backendConnected, ntcore } from "@/nt-listener";

const robotServerIP = ref("");
const robotServerIPRef = ref("");
const ipValid = ref(false);

const robotServerIPTopic: NetworkTablesTopic<number> = ntcore.createTopic(
  "teamNumber",
  NetworkTablesTypeInfos.kInteger,
);

const hostnameDialog = ref(false);
const IPDialog = ref(false);

const hostname = ref("");

const ipAssignmentMethod = ref("dhcp");

const ipPrefix = computed<string>(() => {
  const teamNum = parseInt(robotServerIPRef.value, 10);
  if (isNaN(teamNum)) {
    return "";
  }
  const p1 = Math.floor(teamNum / 100);
  const p2 = teamNum % 100;
  return `10.${p1}.${p2}.`;
});

const updateServerIP = () => {
  if (backendConnected.value) {
    robotServerIPTopic.publish();
    robotServerIPTopic.setValue(parseInt(robotServerIP.value));
  }
};

const rules = [
  (v: any) => !!v || "Number is required",
  (v: any) => (v && !isNaN(v)) || "Must be a number",
  (v: any) => (v && v >= 1 && v <= 25599) || "Team must be between 1 and 25599",
];

const validate = () => {
  for (const rule of rules) {
    const result = rule(robotServerIP.value);
    if (result !== true) {
      ipValid.value = false;
      return;
    }
  }
  ipValid.value = true;
};

async function requestHostnameUpdate() {
  const message: string = hostname.value;
  try {
    const response = await axios.post(apiURI + "/api/hostname", message);
    console.log("Success:", response.data);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        console.error("Error:", error.response.data);
      } else {
        console.error("Error:", error.message);
      }
    } else {
      console.error("Unexpected error:", error);
    }
  }
}

onMounted(() => {
  robotServerIPTopic.subscribe((v) => {
    if (v !== null && robotServerIPRef.value !== v.toString()) {
      robotServerIP.value = v.toString();
      robotServerIPRef.value = v.toString();
    }
  }, true);
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter,
.fade-leave-to

/* .fade-leave-active in <2.1.8 */ {
  opacity: 0;
}
</style>
