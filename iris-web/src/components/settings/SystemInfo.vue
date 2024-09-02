<template>
  <div>
    <h2 class="my-3">About</h2>
    <v-card border variant="elevated">
      <v-table>
        <tbody>
          <tr>
            <td>Hardware Model</td>
            <td>{{ hardwareInfo }}</td>
          </tr>
          <tr>
            <td>Uptime</td>
            <td>{{ uptime }}</td>
          </tr>
          <tr>
            <td>Version</td>
            <td>{{ version }}</td>
          </tr>
          <tr>
            <td>Git Commit Hash</td>
            <td>{{ commitHash }}</td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-spacer class="my-3" />
    <v-card border variant="elevated">
      <template #text>
        <div class="edit-settings">
          <div>
            <h3>Offline Software Update</h3>
            <span>Updates can be found at </span>
            <a href="https://github.com" target="_blank">https://example.com/updates</a>
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
  </div>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue'
  import { NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { ntcore } from '@/nt-listener'

  const hardwareInfo = ref('Unknown')
  const version = ref('Unknown')
  const commitHash = ref('Unknown')
  const uptime = ref('00:00')

  function formatTime (numSeconds: number) {
    const days = Math.floor(numSeconds / 86400)
    const hours = Math.floor((numSeconds % 86400) / 3600)
    const minutes = Math.floor((numSeconds % 3600) / 60)
    const seconds = numSeconds % 60
    let result = ''
    if (days > 0) {
      result += days + ':'
    }
    if (days > 0 || hours > 0) {
      result += (hours < 10 ? '0' : '') + hours + ':'
    }
    result += (minutes < 10 ? '0' : '') + minutes + ':'
    result += (seconds < 10 ? '0' : '') + seconds
    return result
  }

  onMounted(() => {
    ntcore.createTopic<string>('hardwareInfo', NetworkTablesTypeInfos.kString).subscribe(
      v => {
        if (v !== null) {
          hardwareInfo.value = v
        }
      }
    )
    ntcore.createTopic<string>('version', NetworkTablesTypeInfos.kString).subscribe(
      v => {
        if (v !== null) {
          version.value = v
        }
      }
    )
    ntcore.createTopic<string>('gitCommitHash', NetworkTablesTypeInfos.kString).subscribe(
      v => {
        if (v !== null) {
          commitHash.value = v
        }
      }
    )
    ntcore.createTopic<number>('uptime', NetworkTablesTypeInfos.kInteger).subscribe(
      v => {
        if (v !== null) {
          uptime.value = formatTime(v)
        }
      }
    )
  })

</script>
