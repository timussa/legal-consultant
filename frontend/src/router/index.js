import {createRouter, createWebHistory} from 'vue-router';
import {ROUTE_NAMES} from '@/core/constants';

import HomePage from '@/pages/HomePage.vue';

export const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    scrollBehavior(to, from, savedPosition) {
        return savedPosition ?? {top: 0};
    },
    routes: [
        {path: '/', name: ROUTE_NAMES.home, component: HomePage},
        {
            path: '/dialogs/:dialogId?',
            name: ROUTE_NAMES.dialogs,
            component: () => import('@/pages/DialogsPage.vue'),
        },
        {
            path: '/documents/:documentId',
            name: ROUTE_NAMES.document,
            component: () => import('@/pages/DocumentPage.vue'),
        },
        {
            path: '/verification',
            name: ROUTE_NAMES.verification,
            component: () => import('@/pages/VerificationPage.vue'),
        },
        {path: '/:pathMatch(.*)*', redirect: {name: ROUTE_NAMES.home}},
    ],
});
