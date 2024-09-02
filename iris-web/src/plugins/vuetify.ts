/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'

export default createVuetify({
  theme: {
    defaultTheme: 'dark',
    themes: {
      dark: {
        dark: true,
        colors: {
          // primary: '#5A4FCF',
          // secondary: '#817F9F',
          // background: '#1C1B1F',
          // surface: '#26252D',
          // background: '#131318',
          // 'on-background': '#E5E1E9',
          // surface: '#131318',
          // 'on-surface': '#E5E1E9',
          error: '#FF5449',
          // info: '#2196F3',
          // success: '#4caf50',
          // warning: '#fb8c00',
        },
      },
    },
  },
})
