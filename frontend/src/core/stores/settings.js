import {defineStore} from 'pinia';
import {ref, watch} from 'vue';
import {USER_ROLES} from '@/core/constants';
import {readStored, writeStored} from '@/core/utils/storage';

const STORAGE_KEY = 'legal-assistant:settings';

export const DEFAULT_SETTINGS = Object.freeze({
    defaultRole: USER_ROLES.lawyer,
    notifyUpdates: true,
    notifyOutdated: true,
    notifyDisputed: true,
    isStreaming: true,
    isPipelineExpanded: false,
    isMotionReduced: false,
});

export const useSettingsStore = defineStore('settings', () => {
    const settings = ref(readStored(STORAGE_KEY, {...DEFAULT_SETTINGS}));

    watch(settings, (value) => writeStored(STORAGE_KEY, value), {deep: true});

    /**
     * @param {keyof typeof DEFAULT_SETTINGS} key
     * @param {unknown} value
     */
    function update(key, value) {
        settings.value[key] = value;
    }

    function reset() {
        settings.value = {...DEFAULT_SETTINGS};
    }

    return {settings, update, reset};
});
