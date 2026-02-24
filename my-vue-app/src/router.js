import { createRouter, createWebHistory } from 'vue-router'
import MonitorView from './views/MonitorView.vue'
import SenderView from './views/SenderView.vue'
import IPSettingView from './views/IPSettingView.vue'
import HealthDashboard from './views/HealthDashboard.vue'

const routes = [
  { 
    path: '/', 
    name: 'Monitor',
    component: MonitorView 
  },
  { 
    path: '/send', 
    name: 'Sender',
    component: SenderView 
  },
  {
    path: '/ip',
    name: 'IPSetting',
    component: IPSettingView
  },
  {
    path: '/health',
    name: 'HealthDashboard',
    component: HealthDashboard
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router