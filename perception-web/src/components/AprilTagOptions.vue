<template>
  <v-card elevation="12" min-width="400" rounded="lg">
    <template #title>
      <span class="font-weight-black">AprilTag</span>
    </template>
    <v-divider />
    <v-card-text>
      <v-select
        v-model="tagFamily"
        class="ma-4"
        :items="tagFamilies"
        label="AprilTag Family"
        variant="outlined"
      />

      <v-slider
        v-model="decimate"
        class="ma-4"
        hide-details
        :max="3"
        :min="1"
        :step="0.5"
      >
        <template #label>
          <span class="slider-label">Decimate</span>
        </template>
        <template #append>
          <v-text-field
            v-model="decimate"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>
      <v-slider
        v-model="blur"
        class="ma-4"
        hide-details
        :max="4"
        :step="1"
      >
        <template #label>
          <span class="slider-label">Gaussian Blur</span>
        </template>
        <template #append>
          <v-text-field
            v-model="blur"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>
      <v-slider
        v-model="nThreads"
        class="ma-4"
        hide-details
        :max="8"
        :min="1"
        :step="1"
      >
        <template #label>
          <span class="slider-label">CPU Threads</span>
        </template>
        <template #append>
          <v-text-field
            v-model="nThreads"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>

      <v-switch class="ma-4" hide-details>
        <template #label>
          <span class="switch-label">Refine Edges</span>
        </template>
      </v-switch>
    </v-card-text>
  </v-card>
</template>

<script lang="ts" setup>
  import { NetworkTables, NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
  import { onMounted, ref, watch } from 'vue'

  const tagFamilies = ['tag36h11', 'tag25h9', 'tag16h5']

  const decimate = ref(1.0)
  const blur = ref(0.0)
  const nThreads = ref(1)
  const tagFamily = ref()

  const decimateRef = ref(1.0)
  const blurRef = ref(0.0)
  const nThreadsRef = ref(1)
  const tagFamilyRef = ref()

  onMounted(() => {
    const ntcore = NetworkTables.getInstanceByURI('127.0.0.1')

    const threadsTopic: NetworkTablesTopic<number> = ntcore.createTopic('threads', NetworkTablesTypeInfos.kInteger)
    const blurTopic: NetworkTablesTopic<number> = ntcore.createTopic('blur', NetworkTablesTypeInfos.kDouble)
    const decimateTopic: NetworkTablesTopic<number> = ntcore.createTopic('decimate', NetworkTablesTypeInfos.kDouble)
    const apriltagFamilyTopic: NetworkTablesTopic<string> = ntcore.createTopic('tagFamily', NetworkTablesTypeInfos.kString)

    watch(nThreads, async newNThreads => {
      nThreadsRef.value = newNThreads
      threadsTopic.publish()
      threadsTopic.setValue(newNThreads)
    })

    watch(blur, async newBlur => {
      blurRef.value = newBlur
      blurTopic.publish()
      blurTopic.setValue(newBlur)
    })

    watch(decimate, async newDecimate => {
      decimateRef.value = newDecimate
      decimateTopic.publish()
      decimateTopic.setValue(newDecimate)
    })

    watch(tagFamily, async newTagFamily => {
      tagFamilyRef.value = newTagFamily
      apriltagFamilyTopic.publish()
      apriltagFamilyTopic.setValue(newTagFamily)
    })

    threadsTopic.subscribe(v => {
      if (v !== null && nThreadsRef.value !== v) {
        nThreads.value = v
        nThreadsRef.value = v
      }
    }, true)

    blurTopic.subscribe(v => {
      if (v !== null && blurRef.value !== v) {
        blur.value = v
        blurRef.value = v
      }
    }, true)

    decimateTopic.subscribe(v => {
      if (v !== null && decimateRef.value !== v) {
        decimate.value = v
        decimateRef.value = v
      }
    }, true)

    apriltagFamilyTopic.subscribe(v => {
      if (v !== null && tagFamilyRef.value !== v) {
        tagFamily.value = v
        tagFamilyRef.value = v
      }
    }, true)
  })
</script>

<style>
.slider-label {
  display: inline-block;
  width: 200px;
}
</style>
