<template>
  <v-card border min-width="400">
    <template #title>
      <span class="font-weight-black">AprilTag Options</span>
    </template>
    <v-divider />
    <v-card-text>
      <v-select
        color="secondary"
        :items="['AprilTag 3','Aruco']"
        label="Detector"
        variant="outlined"
      />
      <v-select
        v-model="tagFamily"
        color="secondary"
        :items="tagFamilies"
        label="AprilTag Family"
        variant="outlined"
      />
      <v-slider
        v-model="decimate"
        color="secondary"
        hide-details
        :max="6"
        :min="1"
        :step="1"
      >
        <template #label>
          <span class="options-label">Decimate</span>
        </template>
        <template #append>
          <v-text-field
            v-model="decimate"
            color="secondary"
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
        class="my-4"
        color="secondary"
        hide-details
        :max="4"
        :step="0.1"
      >
        <template #label>
          <span class="options-label">Gaussian Blur</span>
        </template>
        <template #append>
          <v-text-field
            v-model="blur"
            color="secondary"
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
        class="my-4"
        color="secondary"
        hide-details
        :max="8"
        :min="1"
        :step="1"
      >
        <template #label>
          <span class="options-label">CPU Threads</span>
        </template>
        <template #append>
          <v-text-field
            v-model="nThreads"
            color="secondary"
            density="compact"
            hide-details
            style="width: 80px"
            type="number"
            variant="outlined"
          />
        </template>
      </v-slider>
      <v-text-field
        color="secondary"
        label="Tag ID Filter"
        variant="outlined"
      />
    </v-card-text>
  </v-card>
</template>

<script lang="ts" setup>
  import { ntcore } from '@/nt-listener'
  import { NetworkTablesTopic, NetworkTablesTypeInfos } from 'ntcore-ts-client'
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
.options-label {
  display: inline-block;
  width: 110px;
}
</style>
