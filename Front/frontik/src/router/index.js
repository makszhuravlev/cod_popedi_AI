import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import HomeView from '../views/HomeView.vue'
import NoAuthMainView from '../views/NoAuthMainView.vue'
import HistoryView from '../views/HistoryView.vue'
const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  { path: '/home', component: HomeView },
  { path: '/noauth', component: NoAuthMainView },
  { path: '/history', component: HistoryView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})

