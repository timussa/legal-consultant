import {defineStore, storeToRefs} from 'pinia';
import {computed, ref} from 'vue';
import {getNotifications, markNotificationsRead} from '@/core/api/notifications';
import {NOTIFICATION_KINDS} from '@/core/constants';
import {getErrorMessage} from '@/core/helpers/getErrorMessage';
import {useSessionStore} from '@/core/stores/session';
import {useSettingsStore} from '@/core/stores/settings';
import {readStored, writeStored} from '@/core/utils/storage';

const STORAGE_KEY = 'legal-assistant:read-notifications';

const KIND_SETTINGS = Object.freeze({
    [NOTIFICATION_KINDS.update]: 'notifyUpdates',
    [NOTIFICATION_KINDS.outdated]: 'notifyOutdated',
    [NOTIFICATION_KINDS.disputed]: 'notifyDisputed',
});

export const useNotificationsStore = defineStore('notifications', () => {
    const {isHead} = storeToRefs(useSessionStore());
    const {settings} = storeToRefs(useSettingsStore());

    const items = ref(/** @type {import('@/core/data/notifications').AppNotification[]} */ ([]));
    const readIds = ref(readStored(STORAGE_KEY, {ids: []}).ids);
    const error = ref(/** @type {string | null} */ (null));

    const visible = computed(() =>
        items.value.filter((item) => (isHead.value || !item.isHeadOnly) && settings.value[KIND_SETTINGS[item.kind]]),
    );
    const unreadCount = computed(() => visible.value.filter((item) => !readIds.value.includes(item.id)).length);

    async function load() {
        error.value = null;

        try {
            items.value = await getNotifications();

            // Прочитанность хранится на сервере; локальный список — запасной вариант для старых данных.
            const serverRead = items.value.filter((item) => item.isRead).map((item) => item.id);

            readIds.value = [...new Set([...readIds.value, ...serverRead])];
        } catch (loadError) {
            error.value = getErrorMessage(loadError);
        }
    }

    /** @param {string[]} ids */
    async function markRead(ids) {
        const fresh = ids.filter((id) => !readIds.value.includes(id));

        if (!fresh.length) {
            return;
        }

        readIds.value = [...readIds.value, ...fresh];
        writeStored(STORAGE_KEY, {ids: readIds.value});

        try {
            await markNotificationsRead(fresh);
        } catch (markError) {
            error.value = getErrorMessage(markError);
        }
    }

    /** @param {string} id */
    function isRead(id) {
        return readIds.value.includes(id);
    }

    return {visible, unreadCount, error, load, markRead, isRead};
});
