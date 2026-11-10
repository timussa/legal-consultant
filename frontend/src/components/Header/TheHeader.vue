<script setup>
import {onBeforeUnmount, onMounted, ref} from 'vue';
import {Bell, Search} from 'lucide-vue-next';
import {storeToRefs} from 'pinia';
import {useRouter} from 'vue-router';
import {ROUTE_NAMES} from '@/core/constants';
import {useDialogsStore} from '@/core/stores/dialogs';
import {ROLE_OPTIONS, useSessionStore} from '@/core/stores/session';

import UiBrandMark from '@/components/Ui/UiBrandMark.vue';
import UiSegmented from '@/components/Ui/UiSegmented.vue';

const router = useRouter();
const dialogsStore = useDialogsStore();
const sessionStore = useSessionStore();
const {role, user} = storeToRefs(sessionStore);

const query = ref('');
const searchInput = ref(null);

onMounted(() => window.addEventListener('keydown', handleShortcut));

onBeforeUnmount(() => window.removeEventListener('keydown', handleShortcut));

/** @param {KeyboardEvent} event */
function handleShortcut(event) {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        searchInput.value?.focus();
    }
}

async function handleSearchSubmit() {
    const question = query.value.trim();

    if (!question) {
        return;
    }

    query.value = '';
    searchInput.value?.blur();

    const dialogId = await dialogsStore.ask(question);

    router.push({name: ROUTE_NAMES.dialogs, params: {dialogId}});
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

        <form
            class="the-header__search"
            role="search"
            @submit.prevent="handleSearchSubmit"
        >
            <Search
                class="the-header__search-icon"
                :size="18"
                aria-hidden="true"
            />
            <input
                ref="searchInput"
                v-model="query"
                class="the-header__search-input"
                type="search"
                placeholder="Спросите или найдите документ"
                aria-label="Вопрос или поиск по базе"
            />
            <kbd class="the-header__search-key">⌘K</kbd>
        </form>

        <div class="the-header__actions">
            <div class="the-header__roles">
                <UiSegmented
                    v-model="role"
                    :options="ROLE_OPTIONS"
                    label="Роль"
                />
            </div>
            <button
                class="the-header__bell"
                type="button"
                aria-label="Уведомления: 2 новых"
            >
                <Bell
                    :size="20"
                    aria-hidden="true"
                />
                <span class="the-header__bell-dot" />
            </button>
            <div class="the-header__user">
                <span class="the-header__avatar">{{ user.initials }}</span>
                <span class="the-header__user-text">
                    <span class="the-header__user-name">{{ user.name }}</span>
                    <span class="the-header__user-position">{{ user.position }}</span>
                </span>
            </div>
        </div>
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
        position: relative;
        display: flex;
        flex: 1;
        align-items: center;
        min-width: 0;
        max-width: 520px;
        transition:
            border-color $duration ease,
            box-shadow $duration ease;
        border: 1px solid $color-line;
        border-radius: $radius-pill;
        background: $color-surface-soft;
        gap: $indent-step * 2;

        @include padding('x', 4);

        &:focus-within {
            border-color: $color-lavender-line;
            box-shadow: 0 0 0 4px rgba($color-violet-bright, 12%);
        }
    }

    &__search-icon {
        flex-shrink: 0;
        color: $color-ink-faint;
    }

    &__search-input {
        flex: 1;
        min-width: 0;
        height: 40px;
        color: $color-ink;
        border: none;
        outline: none;
        background: transparent;
        font: inherit;
        font-size: $font-size-md;

        &::placeholder {
            color: $color-ink-faint;
        }
    }

    &__search-key {
        color: $color-ink-muted;
        border: 1px solid $color-line;
        border-radius: $radius-xs;
        background: $color-surface;
        font-family: $font-primary;
        font-size: $font-size-2xs;
        font-weight: $font-weight-bold;

        @include padding('y', 0.5);
        @include padding('x', 1.5);
    }

    &__actions {
        display: flex;
        align-items: center;
        margin-left: auto;
        gap: $indent-step * 4;
    }

    &__bell {
        @include button-reset;
        @include flex-center;
        @include focus-ring;

        position: relative;
        width: 40px;
        height: 40px;
        transition: background $duration ease;
        color: $color-ink-soft;
        border-radius: $radius-lg;

        @include hover {
            background: $color-surface-muted;
        }
    }

    &__bell-dot {
        position: absolute;
        top: 9px;
        right: 10px;
        width: 8px;
        height: 8px;
        border: 2px solid $color-surface;
        border-radius: $radius-pill;
        background: $color-orange;
    }

    &__user {
        display: flex;
        align-items: center;
        gap: $indent-step * 2.5;
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
        &__user-text,
        &__search-key {
            display: none;
        }
    }

    @include mobile {
        gap: $indent-step * 2;

        @include padding('x', 3);

        &__roles,
        &__bell {
            display: none;
        }
    }
}
</style>
