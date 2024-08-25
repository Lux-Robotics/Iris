import { NetworkTables } from 'ntcore-ts-client'
import { ref } from 'vue'
const backendConnected = ref(false)

const ntcore = NetworkTables.getInstanceByURI('127.0.0.1')
ntcore.addRobotConnectionListener(v => {
  backendConnected.value = v
}, true)

export { ntcore, backendConnected }
