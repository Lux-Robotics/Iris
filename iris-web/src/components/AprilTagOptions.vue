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

const decimateRef = ref(1.0);
const blurRef = ref(0.0);
const nThreadsRef = ref(1);
const tagFamilyRef = ref();
const detectorRef = ref();
const sharpenRef = ref(0);
const decisionMarginRef = ref(0);

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

onMounted(() => {
	watch(detector, async (newDetector) => {
		detectorRef.value = newDetector;
		detectorTopic.publish();
		detectorTopic.setValue(newDetector);
	});

	watch(nThreads, async (newNThreads) => {
		nThreadsRef.value = newNThreads;
		threadsTopic.publish();
		threadsTopic.setValue(newNThreads);
	});

	watch(blur, async (newBlur) => {
		blurRef.value = newBlur;
		blurTopic.publish();
		blurTopic.setValue(newBlur);
	});

	watch(decimate, async (newDecimate) => {
		decimateRef.value = newDecimate;
		decimateTopic.publish();
		decimateTopic.setValue(newDecimate);
	});

	watch(sharpen, async (newSharpen) => {
		sharpenRef.value = newSharpen;
		sharpenTopic.publish();
		sharpenTopic.setValue(newSharpen);
	});

	watch(decisionMargin, async (newDecisionMargin) => {
		decisionMarginRef.value = newDecisionMargin;
		decisionMarginTopic.publish();
		decisionMarginTopic.setValue(newDecisionMargin);
	});

	watch(tagFamily, async (newTagFamily) => {
		tagFamilyRef.value = newTagFamily;
		apriltagFamilyTopic.publish();
		apriltagFamilyTopic.setValue(newTagFamily);
	});

	detectorTopic.subscribe((v) => {
		if (v !== null && detectorRef.value !== v) {
			detector.value = v;
			detectorRef.value = v;
		}
	}, true);

	threadsTopic.subscribe((v) => {
		if (v !== null && nThreadsRef.value !== v) {
			nThreads.value = v;
			nThreadsRef.value = v;
		}
	}, true);

	blurTopic.subscribe((v) => {
		if (v !== null && blurRef.value !== v) {
			blur.value = v;
			blurRef.value = v;
		}
	}, true);

	decimateTopic.subscribe((v) => {
		if (v !== null && decimateRef.value !== v) {
			decimate.value = v;
			decimateRef.value = v;
		}
	}, true);

	sharpenTopic.subscribe((v) => {
		if (v !== null && sharpenRef.value !== v) {
			sharpen.value = v;
			sharpenRef.value = v;
		}
	});

	decisionMarginTopic.subscribe((v) => {
		if (v !== null && decisionMarginRef.value !== v) {
			decisionMargin.value = v;
			decisionMarginRef.value = v;
		}
	});

	apriltagFamilyTopic.subscribe((v) => {
		if (v !== null && tagFamilyRef.value !== v) {
			tagFamily.value = v;
			tagFamilyRef.value = v;
		}
	}, true);
});
</script>

<style>
.options-label {
  display: inline-block;
  width: 110px;
}
</style>
