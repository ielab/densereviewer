import { createRouter, createWebHistory } from 'vue-router'

import { getAccountInfo } from '@/utils/auth'
import { accountAuthStore } from './stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('./templates/Main.vue'),
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('./views/home/Home.vue'),
        },
        {
          path: 'preview',
          name: 'preview',
          component: () => import('./views/preview/Preview.vue'),
        },
        {
          path: 'upload',
          name: 'upload',
          component: () => import('./views/upload/Upload.vue'),
        },
        {
          path: 'mydataset',
          name: 'mydataset',
          component: () => import('./views/mydataset/MyDataset.vue'),
        },
        {
          path: 'login',
          name: 'login',
          component: () => import('./views/login/Login.vue'),
        },
        {
          path: 'review/:id',
          name: 'review',
          component: () => import('./views/review/Review.vue'),
        },
        {
          path: 'progress/:id',
          name: 'progress',
          component: () => import('./views/progress/Progress.vue'),
        },
        {
          path: 'summary/:id',
          name: 'summary',
          component: () => import('./views/summary/Summary.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: { name: 'home' },
    },
  ],
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

router.beforeEach(async (to, _, next) => {
  // Check authentication
  const accountInfo = await getAccountInfo()
  if (accountInfo) Object.assign(accountAuthStore, accountInfo)

  // For Page that not need to authenticate.
  const PUBLIC_PATH_NAMES = ['home', 'signUp']
  if (PUBLIC_PATH_NAMES.includes(to.name as string)) return next()

  const destination = to.path === '/' ? undefined : to.fullPath
  if (!accountInfo && !['login'].includes(to.name as string)) {
    return next({ name: 'login', query: { next: destination } })
  }
  if (accountInfo && ['login'].includes(to.name as string)) {
    return next({ name: 'home' })
  }
  next()
})

export default router
