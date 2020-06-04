import Vue from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify';

import JsonTree from '@/components/json-tree.vue';
Vue.component('json-tree', JsonTree);

import './main.scss';
import './util';

declare var VueSpaBackend: any;
Vue.use(VueSpaBackend);

// Nice, but slows down UI a lot, and the Vue extension for FF/Chrome shows
// similar information. Instead, put Vue on window and allow user to toggle.
//Vue.config.performance = true
(window as any).Vue = Vue;
Vue.config.productionTip = false

new Vue({
  router,
  vuetify,
  render: (h: any) => h(App)
} as any).$mount('#app')
