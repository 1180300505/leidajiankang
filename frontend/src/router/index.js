import { createRouter, createWebHistory } from 'vue-router'
import RealtimeView from '../views/RealtimeView.vue'
import HealthView from '../views/HealthView.vue'
import HealthHistoryView from '../views/HealthHistoryView.vue'
import AlertsView from '../views/AlertsView.vue'
import SystemView from '../views/SystemView.vue'

const routes = [
  { path: '/', redirect: '/health' },
  { path: '/realtime', name: 'realtime', component: RealtimeView },
  { path: '/health', name: 'health', component: HealthView },
  { path: '/health-history', name: 'health-history', component: HealthHistoryView },
  { path: '/alerts', name: 'alerts', component: AlertsView },
  { path: '/system', name: 'system', component: SystemView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
