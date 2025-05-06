<template>
  <v-card border min-width="300">
    <!--  <v-card color="background" min-width="300" variant="flat">-->
    <template #title>
      <span class="font-weight-black">AprilTag Options</span>
    </template>
    <v-divider />
    <v-card-text>
      <v-select
        v-model="detector"
        color="secondary"
        item-props
        :items="detectors"
        label="Detector"
        variant="outlined"
      />
      <v-select
        v-model="tagFamily"
        color="secondary"
        item-props
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
        v-model="sharpen"
        class="my-4"
        color="secondary"
        hide-details
        :max="4"
        :step="0.1"
      >
        <template #label>
          <span class="options-label">Decode Sharpening</span>
        </template>
        <template #append>
          <v-text-field
            v-model="sharpen"
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
        v-model="decisionMargin"
        class="my-4"
        color="secondary"
        hide-details
        :max="50"
        :step="1"
      >
        <template #label>
          <span class="options-label">Decision Margin</span>
        </template>
        <template #append>
          <v-text-field
            v-model="decisionMargin"
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
        v-model="enabledTags"
        color="secondary"
        label="Tag ID Filter"
        variant="outlined"
      />
    </v-card-text>
  </v-card>
</template>

<script lang="ts" setup>
import { ntcore } from "@/nt-listener";
import { NetworkTablesTopic, NetworkTablesTypeInfos } from "ntcore-ts-client";
import { onMounted, ref, watch } from "vue";

const detectors = [
  {
    title: "AprilTag 3",
    value: "apriltag",
    subtitle: "More accurate corners, lower framerate",
  },
  {
    title: "Aruco",
    value: "aruco",
    subtitle: "Less accurate corners, higher framerate",
  },
  {
    title: "Disabled",
    value: "disabled",
    subtitle: "Disable AprilTag detection",
  },
];
const tagFamilies = [
  {
    title: "tag36h11",
    subtitle: "Used in FRC 2024 and later",
  },
  "tag25h9",
  {
    title: "tag16h5",
    subtitle: "Used in FRC 2023",
  },
];

const decimate = ref(1.0);
const blur = ref(0.0);
const nThreads = ref(1);
const tagFamily = ref();
const detector = ref();
const sharpen = ref(0);
const decisionMargin = ref(0);
const enabledTags = ref("");

let enabledTagsRef: number[] = [];

const threadsTopic: NetworkTablesTopic<number> = ntcore.createTopic(
  "threads",
  NetworkTablesTypeInfos.kInteger,
);
const blurTopic: NetworkTablesTopic<number> = ntcore.createTopic(
  "blur",
  NetworkTablesTypeInfos.kDouble,
);
const decimateTopic: NetworkTablesTopic<number> = ntcore.createTopic(
  "decimate",
  NetworkTablesTypeInfos.kDouble,
);
const sharpenTopic: NetworkTablesTopic<number> = ntcore.createTopic(
  "decode_sharpen",
  NetworkTablesTypeInfos.kDouble,
);
const decisionMarginTopic: NetworkTablesTopic<number> = ntcore.createTopic(
  "decision_margin",
  NetworkTablesTypeInfos.kInteger,
);
const apriltagFamilyTopic: NetworkTablesTopic<string> = ntcore.createTopic(
  "tagFamily",
  NetworkTablesTypeInfos.kString,
);
const detectorTopic: NetworkTablesTopic<string> = ntcore.createTopic(
  "detector",
  NetworkTablesTypeInfos.kString,
);

const enabledTagsTopic: NetworkTablesTopic<number[]> = ntcore.createTopic(
  "enabled_apriltag_ids",
  NetworkTablesTypeInfos.kIntegerArray,
);

// function parseIDRanges(x: string): number[] {
//   const result: number[] = [];
//
//   const segments = x.split(",").map((segment) => segment.trim());
//
//   segments.forEach((segment) => {
//     if (segment.includes("-")) {
//       const [startStr, endStr] = segment.split("-").map((part) => part.trim());
//       const start = parseInt(startStr, 10);
//       const end = parseInt(endStr, 10);
//
//       for (let i = start; i <= end; i++) {
//         result.push(i);
//       }
//     } else {
//       const number = parseInt(segment, 10);
//       result.push(number);
//     }
//   });
//
//   return result;
// }

function formatRange(numbers: number[]): string {
  if (numbers.length === 0) return "";

  const sortedNumbers = [...numbers].sort((a, b) => a - b);
  const result: string[] = [];

  let start = sortedNumbers[0];
  let end = start;

  for (let i = 1; i < sortedNumbers.length; i++) {
    const current = sortedNumbers[i];

    if (current === end + 1) {
      end = current;
    } else {
      if (start === end) {
        result.push(`${start}`);
      } else {
        result.push(`${start}-${end}`);
      }
      start = current;
      end = current;
    }
  }

  if (start === end) {
    result.push(`${start}`);
  } else {
    result.push(`${start}-${end}`);
  }

  return result.join(", ");
}

onMounted(() => {
  watch(detector, async (newDetector) => {
    detectorTopic.publish();
    detectorTopic.setValue(newDetector);
  });

  watch(nThreads, async (newNThreads) => {
    threadsTopic.publish();
    threadsTopic.setValue(newNThreads);
  });

  watch(blur, async (newBlur) => {
    blurTopic.publish();
    blurTopic.setValue(newBlur);
  });

  watch(decimate, async (newDecimate) => {
    decimateTopic.publish();
    decimateTopic.setValue(newDecimate);
  });

  watch(sharpen, async (newSharpen) => {
    sharpenTopic.publish();
    sharpenTopic.setValue(newSharpen);
  });

  watch(decisionMargin, async (newDecisionMargin) => {
    decisionMarginTopic.publish();
    decisionMarginTopic.setValue(newDecisionMargin);
  });

  watch(tagFamily, async (newTagFamily) => {
    apriltagFamilyTopic.publish();
    apriltagFamilyTopic.setValue(newTagFamily);
  });

  detectorTopic.subscribe((v) => {
    if (v !== null && detector.value !== v) {
      detector.value = v;
    }
  }, true);

  threadsTopic.subscribe((v) => {
    if (v !== null && nThreads.value !== v) {
      nThreads.value = v;
    }
  }, true);

  blurTopic.subscribe((v) => {
    if (v !== null && blur.value !== v) {
      blur.value = v;
    }
  }, true);

  decimateTopic.subscribe((v) => {
    if (v !== null && decimate.value !== v) {
      decimate.value = v;
    }
  }, true);

  sharpenTopic.subscribe((v) => {
    if (v !== null && sharpen.value !== v) {
      sharpen.value = v;
    }
  });

  decisionMarginTopic.subscribe((v) => {
    if (v !== null && decisionMargin.value !== v) {
      decisionMargin.value = v;
    }
  });

  apriltagFamilyTopic.subscribe((v) => {
    if (v !== null && tagFamily.value !== v) {
      tagFamily.value = v;
    }
  }, true);

  enabledTagsTopic.subscribe((v) => {
    if (v !== null && enabledTagsRef != v) {
      enabledTagsRef = v;
      enabledTags.value = formatRange(v);
    }
  });
});
</script>

<style>
.options-label {
  display: inline-block;
  width: 110px;
}
</style>
