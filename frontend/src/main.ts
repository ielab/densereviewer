import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Axios
import axios from 'axios'
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL // Setup base URL for API calls

// Tailwind
import './assets/tailwind.css'

import 'highlight.js/styles/github.min.css'

// Font Awesome
import '@fortawesome/fontawesome-free/js/all'

// PrimeVue
import PrimeVue from 'primevue/config'
import 'primevue/resources/themes/lara-light-purple/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'

// PrimeVue Components
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'
import ConfirmationService from 'primevue/confirmationservice'
import FocusTrap from 'primevue/focustrap'

// Custom CSS
import './assets/style.css'

createApp(App)
  .use(router)
  .use(PrimeVue)
  .use(ToastService)
  .use(ConfirmationService)
  .directive('tooltip', Tooltip)
  .directive('focustrap', FocusTrap)
  .mount('#app')
