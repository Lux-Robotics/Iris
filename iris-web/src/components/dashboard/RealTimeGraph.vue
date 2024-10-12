<template>
  <ChartLine id="my-chart-id" :data="chartData" :options="chartOptions" />
</template>

<script>
import {
	BarElement,
	CategoryScale,
	Chart as ChartJS,
	Legend,
	LinearScale,
	Title,
	Tooltip,
} from "chart.js";
import { Line as ChartLine } from "vue-chartjs";

ChartJS.register(
	Title,
	Tooltip,
	Legend,
	BarElement,
	CategoryScale,
	LinearScale,
);

export default {
	name: "BarChart",
	components: { ChartLine },
	data() {
		return {
			chartData: {
				labels,
				datasets: [
					{
						label: "Dataset 1",
						data: Utils.numbers(NUMBER_CFG),
						borderColor: Utils.CHART_COLORS.red,
						backgroundColor: Utils.transparentize(Utils.CHART_COLORS.red, 0.5),
					},
					{
						label: "Dataset 2",
						data: Utils.numbers(NUMBER_CFG),
						borderColor: Utils.CHART_COLORS.blue,
						backgroundColor: Utils.transparentize(Utils.CHART_COLORS.blue, 0.5),
					},
				],
			},
			chartOptions: {
				responsive: true,
				maintainAspectRatio: false,
			},
		};
	},
};
</script>
