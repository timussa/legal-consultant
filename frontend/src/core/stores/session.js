import {defineStore} from 'pinia';
import {computed, ref} from 'vue';
import {USER_ROLES} from '@/core/constants';
import {useSettingsStore} from '@/core/stores/settings';

export const ROLE_OPTIONS = Object.freeze([
    {value: USER_ROLES.lawyer, label: 'Юрист'},
    {value: USER_ROLES.head, label: 'Руководитель'},
]);

export const useSessionStore = defineStore('session', () => {
    const settingsStore = useSettingsStore();

    const role = ref(settingsStore.settings.defaultRole);
    const user = ref({name: 'Анна Корнеева', initials: 'АК', position: 'Юрист, договорная работа'});

    const isHead = computed(() => role.value === USER_ROLES.head);

    /** @param {string} nextRole */
    function setRole(nextRole) {
        role.value = nextRole;
    }

    return {role, user, isHead, setRole};
});
