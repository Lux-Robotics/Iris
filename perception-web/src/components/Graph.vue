<template>
  <v-card elevation="12" min-width="400" rounded="lg">
    <template #title>
      <span class="font-weight-black">CPU Metrics</span>
    </template>
    <v-divider />
    <v-card-text>
      <canvas id="cpuMetricsChart" height="200" width="400" />
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'CpuMetricsComponent',
  setup() {
    const chartRef = ref(null)
    let cpuMetricsChart: Chart | null = null
    let updateInterval: number | null = null
    let elapsedTime = 0

    const getRandomInt = (min: number, max: number) => {
      return Math.floor(Math.random() * (max - min + 1)) + min
    }

    const addData = () => {
      elapsedTime += 1
      const time = `${elapsedTime}s`
      const newLoad = getRandomInt(10, 100) // Simulate CPU load
      const newTemp = getRandomInt(40, 60) // Simulate CPU temperature

      if (cpuMetricsChart === null) {
        return
      }

      cpuMetricsChart.data.labels.push(time)
      cpuMetricsChart.data.datasets[0].data.push(newLoad)
      cpuMetricsChart.data.datasets[1].data.push(newTemp)

      cpuMetricsChart.update()
    }

    onMounted(() => {
      const ctx = document.getElementById('cpuMetricsChart').getContext('2d')
      cpuMetricsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['0s'],
          datasets: [
            {
              label: 'CPU Load (%)',
              data: [getRandomInt(10, 100)],
              borderColor: 'rgba(255, 159, 64, 1)',
              borderWidth: 1,
              radius: 0,
              yAxisID: 'y-load',
            },
            {
              label: 'CPU Temperature (°C)',
              data: [getRandomInt(40, 60)],
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1,
              radius: 0,
              yAxisID: 'y-temp',
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            intersect: false
          },
          scales: {
            'y-load': {
              type: 'linear',
              position: 'left',
              title: {
                display: true,
                text: 'Load (%)',
              },
            },
            'y-temp': {
              type: 'linear',
              position: 'right',
              title: {
                display: true,
                text: 'Temperature (°C)',
              },
            },
            x: {
              title: {
                display: true,
                text: 'Time (s)',
              },
            },
          },
        },
      })

      updateInterval = setInterval(addData, 100)
    })

    onUnmounted(() => {
      clearInterval(updateInterval)
    })

    return {
      chartRef,
    }
  },
}
</script>

<style scoped>
.px-4 {
  padding-left: 16px;
  padding-right: 16px;
}

.py-4 {
  padding-top: 16px;
  padding-bottom: 16px;
}
</style>
