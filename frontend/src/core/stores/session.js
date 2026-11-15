import {defineStore} from 'pinia';
import {computed, ref} from 'vue';
import {ApiError} from '@/core/api/client';
import {getMe, login as loginRequest, logout as logoutRequest} from '@/core/api/auth';
import {USER_ROLES} from '@/core/constants';
import {useSettingsStore} from '@/core/stores/settings';

export const ROLE_OPTIONS = Object.freeze([
    {value: USER_ROLES.lawyer, label: 'Юрист'},
    {value: USER_ROLES.head, label: 'Руководитель'},
]);

const UNAUTHORIZED_STATUS = 401;
const GUEST = Object.freeze({name: '', initials: '', position: ''});

export const useSessionStore = defineStore('session', () => {
    const settingsStore = useSettingsStore();

    /** @type {import('vue').Ref<import('@/core/api/auth').SessionUser | null>} */
    const account = ref(null);
    const isChecked = ref(false);
    /** Режим просмотра. Руководитель может посмотреть интерфейс юриста; юрист — только свой. */
    const viewRole = ref(settingsStore.settings.defaultRole);

    const isAuthenticated = computed(() => account.value !== null);
    const canSwitchRole = computed(() => account.value?.role === USER_ROLES.head);
    const role = computed({
        get: () => (canSwitchRole.value ? viewRole.value : USER_ROLES.lawyer),
        set: (value) => setRole(value),
    });
    const isHead = computed(() => role.value === USER_ROLES.head);
    const user = computed(() => account.value ?? GUEST);
    const roleOptions = computed(() => (canSwitchRole.value ? ROLE_OPTIONS : ROLE_OPTIONS.slice(0, 1)));

    /** @param {string} nextRole */
    function setRole(nextRole) {
        viewRole.value = nextRole;
    }

    let checkPromise = null;

    /**
     * Проверяет сессию один раз за загрузку страницы.
     * @returns {Promise<boolean>} вошёл ли пользователь
     */
    function ensure() {
        if (isChecked.value) {
            return Promise.resolve(isAuthenticated.value);
        }

        checkPromise ??= getMe()
            .then((me) => {
                account.value = me;
                return true;
            })
            .catch((error) => {
                if (!(error instanceof ApiError) || error.status !== UNAUTHORIZED_STATUS) {
                    throw error;
                }

                account.value = null;
                return false;
            })
            .finally(() => {
                isChecked.value = true;
                checkPromise = null;
            });

        return checkPromise;
    }

    /**
     * @param {string} loginValue
     * @param {string} password
     */
    async function login(loginValue, password) {
        const result = await loginRequest(loginValue, password);

        account.value = result.user;
        isChecked.value = true;
        viewRole.value = result.user.role === USER_ROLES.head ? settingsStore.settings.defaultRole : USER_ROLES.lawyer;
    }

    async function logout() {
        try {
            await logoutRequest();
        } finally {
            forget();
        }
    }

    /** Сбрасывает сессию локально, например когда сервер ответил 401. */
    function forget() {
        account.value = null;
        isChecked.value = true;
    }

    return {
        role,
        user,
        isHead,
        isAuthenticated,
        isChecked,
        canSwitchRole,
        roleOptions,
        setRole,
        ensure,
        login,
        logout,
        forget,
    };
});
