<script setup>
import {onBeforeUnmount, onMounted, ref} from 'vue';
import {Search} from 'lucide-vue-next';
import {storeToRefs} from 'pinia';
import {ROUTE_NAMES} from '@/core/constants';
import {useSessionStore} from '@/core/stores/session';

import HeaderNotifications from '@/components/Header/HeaderNotifications.vue';
import SearchPalette from '@/components/Search/SearchPalette.vue';
import UiBrandMark from '@/components/Ui/UiBrandMark.vue';
import UiSegmented from '@/components/Ui/UiSegmented.vue';

const EDITABLE_TAGS = Object.freeze(['INPUT', 'TEXTAREA', 'SELECT']);

const sessionStore = useSessionStore();
const {role, user, roleOptions, canSwitchRole} = storeToRefs(sessionStore);

const isSearchOpen = ref(false);

onMounted(() => window.addEventListener('keydown', handleShortcut));

onBeforeUnmount(() => window.removeEventListener('keydown', handleShortcut));

/** @param {KeyboardEvent} event */
function handleShortcut(event) {
    const isEditing = EDITABLE_TAGS.includes(event.target?.tagName) || event.target?.isContentEditable;
    const isPaletteShortcut = (event.metaKey || event.ctrlKey) && event.code === 'KeyK';

    if (isPaletteShortcut || (event.key === '/' && !isEditing)) {
        event.preventDefault();
        isSearchOpen.value = true;
    }
}
</script>

<template>
    <header class="the-header">
        <RouterLink
            class="the-header__brand"
            :to="{name: ROUTE_NAMES.home}"
        >
            <UiBrandMark :size="38" />
            <span class="the-header__brand-text">
                <span class="the-header__brand-name">Юрассистент</span>
                <span class="the-header__brand-caption">база знаний юристов</span>
            </span>
        </RouterLink>

        <button
            class="the-header__search"
            type="button"
            aria-label="Поиск по базе знаний"
            aria-haspopup="dialog"
            @click="isSearchOpen = true"
        >
            <Search
                class="the-header__search-icon"
                :size="18"
                aria-hidden="true"
            />
            <span class="the-header__search-placeholder">Найти пункт, документ или задать вопрос</span>
        </button>

        <div class="the-header__actions">
            <div
                v-if="canSwitchRole"
                class="the-header__roles"
            >
                <UiSegmented
                    v-model="role"
                    :options="roleOptions"
                    label="Роль"
                />
            </div>
            <HeaderNotifications />
            <RouterLink
                class="the-header__user"
                :to="{name: ROUTE_NAMES.settings}"
                aria-label="Профиль и настройки"
            >
                <span class="the-header__avatar">{{ user.initials }}</span>
                <span class="the-header__user-text">
                    <span class="the-header__user-name">{{ user.name }}</span>
                    <span class="the-header__user-position">{{ user.position }}</span>
                </span>
            </RouterLink>
        </div>

        <SearchPalette v-model:open="isSearchOpen" />
    </header>
</template>

<style lang="scss">
.the-header {
    position: sticky;
    z-index: $ui-index-header;
    top: 0;
    display: flex;
    align-items: center;
    height: $header-height;
    border-bottom: 1px solid $color-line;
    background: rgba($color-surface, 88%);
    backdrop-filter: blur(14px);
    gap: $indent-step * 6;

    @include padding('x', 6);

    &__brand {
        display: flex;
        align-items: center;
        color: $color-ink;
        text-decoration: none;
        gap: $indent-step * 3;

        @include focus-ring;
    }

    &__brand-text {
        @include column(0);
    }

    &__brand-name {
        font-size: $font-size-lg;
        font-weight: $font-weight-extrabold;
        letter-spacing: $letter-spacing-tight;
    }

    &__brand-caption {
        color: $color-ink-muted;
        font-size: $font-size-xs;
        font-weight: $font-weight-medium;
    }

    &__search {
        @include button-reset;
        @include focus-ring;

        display: flex;
        flex: 1;
        align-items: center;
        min-width: 0;
        max-width: 520px;
        height: 42px;
        transition:
            border-color $duration ease,
            background-color $duration ease;
        border: 1px solid $color-line;
        border-radius: $radius-pill;
        background-color: $color-surface-soft;
        text-align: left;
        gap: $indent-step * 2;

        @include padding('x', 4);

        @include hover {
            border-color: $color-lavender-line;
            background-color: $color-surface;
        }
    }

    &__search-placeholder {
        overflow: hidden;
        color: $color-ink-faint;
        font-size: $font-size-md;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    &__search-icon {
        flex-shrink: 0;
        color: $color-ink-faint;
    }

    &__actions {
        display: flex;
        align-items: center;
        margin-left: auto;
        gap: $indent-step * 4;
    }

    &__user {
        @include focus-ring;

        display: flex;
        align-items: center;
        color: $color-ink;
        border-radius: $radius-pill;
        text-decoration: none;
        gap: $indent-step * 2.5;

        @include hover {
            color: $color-navy;
        }
    }

    &__avatar {
        @include flex-center;

        width: 38px;
        height: 38px;
        color: $color-white;
        border-radius: $radius-pill;
        background: $color-action;
        font-size: $font-size-sm;
        font-weight: $font-weight-extrabold;
    }

    &__user-text {
        @include column(0);
    }

    &__user-name {
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__user-position {
        color: $color-ink-muted;
        font-size: $font-size-xs;
    }

    @include tablet {
        gap: $indent-step * 3;

        @include padding('x', 4);

        &__brand-text,
        &__user-text {
            display: none;
        }
    }

    @include mobile {
        gap: $indent-step * 2;

        @include padding('x', 3);

        &__roles {
            display: none;
        }

        &__actions {
            gap: $indent-step;
        }
    }
}
</style>
