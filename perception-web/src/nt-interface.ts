import { NetworkTables, NetworkTablesTypeInfos } from 'ntcore-ts-client'

// Get or create the NT client instance
const ntcore = NetworkTables.getInstanceByURI('127.0.0.1')

// Create the gyro topic
const gyroTopic = ntcore.createTopic<number>('/', NetworkTablesTypeInfos.kDouble)

// Subscribe and immediately call the callback with the current value
gyroTopic.subscribe(value => {
  console.log(`Got Gyro Value: ${value}`)
}, true)
