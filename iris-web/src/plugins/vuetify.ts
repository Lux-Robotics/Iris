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
					background: "#1C1C1D",
					surface: "#282829",
					error: "#FF5449",
				},
			},
			light: {
				dark: false,
				colors: {
					error: "#FF5449",
					primary: "#5A4FCF",
					secondary: "#5A4FCF",
					background: "#F0F0F0",
				},
			},
		},
	},
});
