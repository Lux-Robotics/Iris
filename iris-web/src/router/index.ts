/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

import calibration from '@/pages/calibration.vue'
import index from '@/pages/index.vue'
import logs from '@/pages/logs.vue'
import docs from '@/pages/docs.vue'
import settings from '@/pages/settings.vue'
// Composables
import { createRouter, createWebHistory } from 'vue-router/auto'
import { setupLayouts } from 'virtual:generated-layouts'

const routes = [
  { path: '/', name: 'Dashboard', component: index },
  { path: '/calibration', name: 'Camera Calibration', component: calibration },
  { path: '/logs', name: 'Logs', component: logs },
  { path: '/docs', name: 'Documentation', component: docs },
  { path: '/settings', name: 'Settings', component: settings },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: setupLayouts(routes),
})

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err, to) => {
  if (err?.message?.includes?.('Failed to fetch dynamically imported module')) {
    if (!localStorage.getItem('vuetify:dynamic-reload')) {
      console.log('Reloading page to fix dynamic import error')
      localStorage.setItem('vuetify:dynamic-reload', 'true')
      location.assign(to.fullPath)
    } else {
      console.error('Dynamic import error, reloading page did not fix it', err)
    }
  } else {
    console.error(err)
  }
})

router.isReady().then(() => {
  localStorage.removeItem('vuetify:dynamic-reload')
})

export default router
