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
    setup () {
      const chartRef = ref(null)
      let cpuMetricsChart = null
      let updateInterval = null
      let elapsedTime = 0

      const getRandomInt = (min, max) => {
        return Math.floor(Math.random() * (max - min + 1)) + min
      }

      const addData = () => {
        elapsedTime += 15
        const time = `${elapsedTime}s`
        const newLoad = getRandomInt(10, 100) // Simulate CPU load
        const newTemp = getRandomInt(40, 60) // Simulate CPU temperature

        if (cpuMetricsChart.data.labels.length > 10) {
          cpuMetricsChart.data.labels.shift()
          cpuMetricsChart.data.datasets[0].data.shift()
          cpuMetricsChart.data.datasets[1].data.shift()
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
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1,
                fill: false,
                tension: 0.1,
                yAxisID: 'y-load',
              },
              {
                label: 'CPU Temperature (°C)',
                data: [getRandomInt(40, 60)],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: false,
                tension: 0.1,
                yAxisID: 'y-temp',
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              'y-load': {
                type: 'linear',
                position: 'left',
                beginAtZero: true,
                max: 100,
                title: {
                  display: true,
                  text: 'Load (%)',
                },
              },
              'y-temp': {
                type: 'linear',
                position: 'right',
                beginAtZero: false,
                min: 40,
                max: 60,
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

        updateInterval = setInterval(addData, 15000)
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
