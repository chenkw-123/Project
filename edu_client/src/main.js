// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

import axios from "axios"
Vue.prototype.$axios = axios

import Element from "element-ui"
import "element-ui/lib/theme-chalk/index.css"
Vue.use(Element)

// 导入极验
import "../static/js/gt.js"

//全局CSS
import "../static/css/global.css"

Vue.config.productionTip = false

import settings from "./settings";
Vue.prototype.$settings = settings;




/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: {App},
  template: '<App/>'
})
