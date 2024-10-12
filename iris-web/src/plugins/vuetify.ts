/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";

// Composables
import { createVuetify } from "vuetify";

export default createVuetify({
	theme: {
		defaultTheme: "dark",
		themes: {
			dark: {
				dark: true,
				colors: {
					primary: "#5A4FCF",
					secondary: "#B1ADE8",
					// secondary: '#817F9F',
					// background: '#1C1B1F',
					// surface: '#26252D',
					// background: '#252433',
					background: "#1C1C1D",
					// 'on-background': '#E5E1E9',
					// surface: '#312f40',
					surface: "#282829",
					// 'on-surface': '#E5E1E9',
					error: "#FF5449",
					// info: '#2196F3',
					// success: '#4caf50',
					// warning: '#fb8c00',
				},
			},
			light: {
				dark: false,
				colors: {
					error: "#FF5449",
					primary: "#5A4FCF",
					secondary: "#5A4FcF",
					background: "#F0F0F0",
				},
			},
		},
	},
});
