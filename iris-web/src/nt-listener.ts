import { NetworkTables } from "ntcore-ts-client";
import { ref } from "vue";
const backendConnected = ref(false);

// TODO: make this based on backend ip
const backendURI: string = window.location.hostname;
const apiURI: string = window.location.origin;
// const apiPort: number = parseInt(window.location.port)
const ntcore = NetworkTables.getInstanceByURI(backendURI);
ntcore.addRobotConnectionListener((v) => {
  backendConnected.value = v;
}, true);

export { ntcore, backendConnected, backendURI, apiURI };
