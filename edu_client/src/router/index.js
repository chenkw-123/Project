import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

import Home from "../components/Home";
import Login from "../components/Login";
import Register from "../components/Register";
export default new Router({
  routes: [
      {
            path: '/',
            name:"home",
            component: Home
        },
        {
            path: '/home',
            name:"home",
            component: Home
        },
      {
            path: '/home/login',
            name:"Login",
            component: Login
        },
      {
            path: '/user/register',
            name:"Register",
            component: Register
        },

  ]
})
