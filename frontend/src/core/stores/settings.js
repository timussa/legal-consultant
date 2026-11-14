import {defineStore} from 'pinia';
import {ref, watch} from 'vue';
import {getServerSettings, saveServerSettings} from '@/core/api/settings';
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

const SAVE_DELAY_MS = 400;

export const useSettingsStore = defineStore('settings', () => {
    const settings = ref(readStored(STORAGE_KEY, {...DEFAULT_SETTINGS}));
    let isSynced = false;
    let saveTimer = null;

    watch(
        settings,
        (value) => {
            writeStored(STORAGE_KEY, value);

            // Настройки привязаны к учётной записи: после входа уходят на сервер.
            if (isSynced) {
                clearTimeout(saveTimer);
                saveTimer = setTimeout(() => saveServerSettings({...value}).catch(() => {}), SAVE_DELAY_MS);
            }
        },
        {deep: true},
    );

    /** Загружает настройки пользователя с сервера. Ошибка не мешает работе: остаются локальные. */
    async function sync() {
        try {
            const remote = await getServerSettings();

            if (remote) {
                settings.value = {...DEFAULT_SETTINGS, ...remote};
            }
        } catch {
            // Сервер недоступен — работаем с локальной копией.
        } finally {
            isSynced = true;
        }
    }

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

    return {settings, update, reset, sync};
});
