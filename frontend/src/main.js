import { createApp } from 'vue'
import App from './AppShell.vue'
import router from './router'
import './styles/base.css'

createApp(App).use(router).mount('#app')
