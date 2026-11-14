import {createRouter, createWebHistory} from 'vue-router';
import {setUnauthorizedHandler} from '@/core/api/client';
import {ROUTE_NAMES} from '@/core/constants';
import {useSessionStore} from '@/core/stores/session';

import HomePage from '@/pages/HomePage.vue';

export const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    scrollBehavior(to, from, savedPosition) {
        return savedPosition ?? {top: 0};
    },
    routes: [
        {
            path: '/login',
            name: ROUTE_NAMES.login,
            component: () => import('@/pages/LoginPage.vue'),
            meta: {isPublic: true},
        },
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
        {
            path: '/settings',
            name: ROUTE_NAMES.settings,
            component: () => import('@/pages/SettingsPage.vue'),
        },
        {path: '/:pathMatch(.*)*', redirect: {name: ROUTE_NAMES.home}},
    ],
});

router.beforeEach(async (to) => {
    const session = useSessionStore();
    let isAuthenticated = false;

    try {
        isAuthenticated = await session.ensure();
    } catch {
        // Сервер недоступен: страница сама покажет ошибку запроса, не выкидываем на вход.
        return true;
    }

    if (to.meta.isPublic) {
        return isAuthenticated ? {name: ROUTE_NAMES.home} : true;
    }

    return isAuthenticated ? true : {name: ROUTE_NAMES.login, query: to.fullPath === '/' ? {} : {redirect: to.fullPath}};
});

setUnauthorizedHandler(() => {
    // Сессия истекла во время работы. Полная перезагрузка сбрасывает данные прошлого пользователя.
    const current = router.currentRoute.value;

    if (current.name === ROUTE_NAMES.login) {
        return;
    }

    const redirect = current.fullPath;

    useSessionStore().forget();
    window.location.assign(`${import.meta.env.BASE_URL}login?redirect=${encodeURIComponent(redirect)}`);
});
