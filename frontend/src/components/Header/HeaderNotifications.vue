<script setup>
import {computed, ref} from 'vue';
import {Bell, BellOff, FileClock, Flag, History} from 'lucide-vue-next';
import {storeToRefs} from 'pinia';
import {useRouter} from 'vue-router';
import {useClickOutside} from '@/core/composables/useClickOutside';
import {NOTIFICATION_KINDS, ROUTE_NAMES} from '@/core/constants';
import {useNotificationsStore} from '@/core/stores/notifications';
import {pluralize} from '@/core/utils/plural';

const KIND_ICONS = Object.freeze({
    [NOTIFICATION_KINDS.update]: FileClock,
    [NOTIFICATION_KINDS.outdated]: History,
    [NOTIFICATION_KINDS.disputed]: Flag,
});

const router = useRouter();
const notificationsStore = useNotificationsStore();
const {visible, unreadCount} = storeToRefs(notificationsStore);

const isOpen = ref(false);
const root = ref(null);

const bellLabel = computed(() =>
    unreadCount.value
        ? `Уведомления: ${unreadCount.value} ${pluralize(unreadCount.value, ['новое', 'новых', 'новых'])}`
        : 'Уведомления',
);

useClickOutside(root, close);

function close() {
    isOpen.value = false;
}

function toggle() {
    isOpen.value = !isOpen.value;
}

function handleReadAll() {
    notificationsStore.markRead(visible.value.map((item) => item.id));
}

/** @param {import('@/core/data/notifications').AppNotification} item */
function handleOpen(item) {
    notificationsStore.markRead([item.id]);

    if (item.target) {
        close();
        router.push(item.target);
    }
}

function handleSettings() {
    close();
    router.push({name: ROUTE_NAMES.settings});
}
</script>

<template>
    <div
        ref="root"
        class="header-notifications"
    >
        <button
            class="header-notifications__bell"
            type="button"
            :aria-label="bellLabel"
            :aria-expanded="isOpen"
            aria-haspopup="dialog"
            @click="toggle"
        >
            <Bell
                :size="20"
                aria-hidden="true"
            />
            <span
                v-if="unreadCount"
                class="header-notifications__count"
            >
                {{ unreadCount }}
            </span>
        </button>

        <Transition name="header-notifications__panel">
            <div
                v-if="isOpen"
                class="header-notifications__panel"
                role="dialog"
                aria-label="Уведомления"
            >
                <div class="header-notifications__head">
                    <h2 class="header-notifications__title">Уведомления</h2>
                    <button
                        v-if="unreadCount"
                        class="header-notifications__link"
                        type="button"
                        @click="handleReadAll"
                    >
                        Прочитать все
                    </button>
                </div>

                <ul
                    v-if="visible.length"
                    class="header-notifications__list"
                >
                    <li
                        v-for="item in visible"
                        :key="item.id"
                    >
                        <button
                            :class="[
                                'header-notifications__item',
                                `header-notifications__item--${item.kind}`,
                                {'header-notifications__item--unread': !notificationsStore.isRead(item.id)},
                            ]"
                            type="button"
                            @click="handleOpen(item)"
                        >
                            <span class="header-notifications__icon">
                                <component
                                    :is="KIND_ICONS[item.kind]"
                                    :size="17"
                                    aria-hidden="true"
                                />
                            </span>
                            <span class="header-notifications__body">
                                <span class="header-notifications__item-title">{{ item.title }}</span>
                                <span class="header-notifications__item-text">{{ item.text }}</span>
                                <span class="header-notifications__date">{{ item.dateLabel }}</span>
                            </span>
                        </button>
                    </li>
                </ul>

                <p
                    v-else
                    class="header-notifications__empty"
                >
                    <BellOff
                        :size="20"
                        aria-hidden="true"
                    />
                    Новых уведомлений нет. Включить типы уведомлений можно в настройках.
                </p>

                <button
                    class="header-notifications__settings"
                    type="button"
                    @click="handleSettings"
                >
                    Настроить уведомления
                </button>
            </div>
        </Transition>
    </div>
</template>

<style lang="scss">
.header-notifications {
    $block: &;

    position: relative;

    &__bell {
        @include button-reset;
        @include flex-center;
        @include focus-ring;

        position: relative;
        width: 40px;
        height: 40px;
        transition: background-color $duration ease;
        color: $color-ink-soft;
        border-radius: $radius-lg;

        @include hover {
            background-color: $color-surface-muted;
        }

        &[aria-expanded='true'] {
            color: $color-navy;
            background-color: $color-lavender-soft;
        }
    }

    &__count {
        @include flex-center;

        position: absolute;
        top: 3px;
        right: 2px;
        min-width: 18px;
        height: 18px;
        color: $color-white;
        border: 2px solid $color-surface;
        border-radius: $radius-pill;
        background-color: $color-orange;
        font-size: $font-size-2xs;
        font-weight: $font-weight-extrabold;
        line-height: 1;

        @include padding('x', 1);
    }

    &__panel {
        position: absolute;
        z-index: $ui-index-popover;
        top: calc(100% + #{$indent-step * 2});
        right: 0;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        width: 380px;
        border: 1px solid $color-line;
        border-radius: $radius-xl;
        background-color: $color-surface;
        box-shadow: 0 24px 48px -20px rgba($color-ink, 35%);
        transform-origin: top right;

        &-enter-active,
        &-leave-active {
            transition:
                opacity $duration-fast ease,
                transform $duration-fast $ease-out;
        }

        &-enter-from,
        &-leave-to {
            transform: scale(0.97) translateY(-4px);
            opacity: 0;
        }
    }

    &__head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid $color-line-soft;

        @include padding('y', 3.5);
        @include padding('x', 4);
    }

    &__title {
        @include heading($font-size-md);
    }

    &__link,
    &__settings {
        @include button-reset;
        @include focus-ring;

        color: $color-violet;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;

        @include hover {
            color: $color-navy;
        }
    }

    &__list {
        overflow-y: auto;
        max-height: 380px;
        margin: 0;
        padding: 0;
        list-style: none;
    }

    &__item {
        @include button-reset;
        @include focus-ring;

        position: relative;
        display: flex;
        align-items: flex-start;
        width: 100%;
        transition: background-color $duration ease;
        text-align: left;
        gap: $indent-step * 3;

        @include padding('y', 3);
        @include padding('x', 4);

        @include hover {
            background-color: $color-surface-soft;
        }

        &--unread::after {
            position: absolute;
            top: $indent-step * 4.5;
            right: $indent-step * 4;
            width: 8px;
            height: 8px;
            border-radius: $radius-pill;
            background-color: $color-orange;
            content: '';
        }

        &--outdated #{$block}__icon {
            color: $color-peach-ink;
            background-color: $color-peach;
        }

        &--disputed #{$block}__icon {
            color: $color-amber-ink;
            background-color: $color-amber;
        }
    }

    &__icon {
        @include flex-center;

        flex-shrink: 0;
        width: 34px;
        height: 34px;
        color: $color-navy;
        border-radius: $radius-md;
        background-color: $color-navy-tint;
    }

    &__body {
        min-width: 0;

        @include column($indent-step * 0.5);
        @include padding('right', 4);
    }

    &__item-title {
        color: $color-ink;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__item-text {
        color: $color-ink-soft;
        font-size: $font-size-sm;
        line-height: 1.45;
    }

    &__date {
        color: $color-ink-muted;
        font-size: $font-size-xs;
    }

    &__empty {
        display: flex;
        align-items: center;
        margin: 0;
        color: $color-ink-muted;
        font-size: $font-size-sm;
        line-height: 1.45;
        gap: $indent-step * 3;

        @include padding('y', 5);
        @include padding('x', 4);
    }

    &__settings {
        border-top: 1px solid $color-line-soft;
        text-align: center;

        @include padding('y', 3);
    }

    @include mobile {
        position: static;

        &__panel {
            top: $header-height;
            right: $indent-step * 2;
            left: $indent-step * 2;
            width: auto;
        }
    }
}
</style>
