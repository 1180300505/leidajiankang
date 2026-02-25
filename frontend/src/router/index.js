import { createRouter, createWebHistory } from 'vue-router'
import RealtimeView from '../views/RealtimeView.vue'
import HealthView from '../views/HealthView.vue'
import HealthHistoryView from '../views/HealthHistoryView.vue'
import AlertsView from '../views/AlertsView.vue'
import SystemView from '../views/SystemView.vue'
import BackendDemoShell from '../views/demo/BackendDemoShell.vue'
import DemoMonitorView from '../views/demo/MonitorView.vue'
import DemoSenderView from '../views/demo/SenderView.vue'
import DemoHealthDashboardView from '../views/demo/HealthDashboard.vue'
import IPSettingIndustrialView from '../views/IPSettingIndustrialView.vue'

const routes = [
  { path: '/', redirect: '/health' },
  { path: '/realtime', name: 'realtime', component: RealtimeView },
  { path: '/health', name: 'health', component: HealthView },
  { path: '/health-history', name: 'health-history', component: HealthHistoryView },
  { path: '/alerts', name: 'alerts', component: AlertsView },
  { path: '/system', name: 'system', component: SystemView },
  {
    path: '/demo',
    component: BackendDemoShell,
    children: [
      { path: '', redirect: '/demo/monitor' },
      { path: 'monitor', name: 'demo-monitor', component: DemoMonitorView },
      { path: 'send', name: 'demo-send', component: DemoSenderView },
      { path: 'ip', name: 'demo-ip', component: IPSettingIndustrialView },
      {
        path: 'health-dashboard',
        name: 'demo-health-dashboard',
        component: DemoHealthDashboardView
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
