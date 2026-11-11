<script setup>
import {computed} from 'vue';
import {RotateCcw} from 'lucide-vue-next';
import {storeToRefs} from 'pinia';
import {ROLE_OPTIONS, useSessionStore} from '@/core/stores/session';
import {useSettingsStore} from '@/core/stores/settings';
import {useToastStore} from '@/core/stores/toast';

import UiSegmented from '@/components/Ui/UiSegmented.vue';
import UiSwitch from '@/components/Ui/UiSwitch.vue';

const settingsStore = useSettingsStore();
const sessionStore = useSessionStore();
const toastStore = useToastStore();
const {settings} = storeToRefs(settingsStore);
const {user, isHead} = storeToRefs(sessionStore);

const defaultRole = computed({
    get: () => settings.value.defaultRole,
    set: (value) => {
        settingsStore.update('defaultRole', value);
        sessionStore.setRole(value);
    },
});

function handleReset() {
    settingsStore.reset();
    sessionStore.setRole(settings.value.defaultRole);
    toastStore.show('Настройки сброшены');
}
</script>

<template>
    <div class="settings-page">
        <h1 class="settings-page__title">Настройки</h1>

        <section class="settings-page__card settings-page__profile">
            <span class="settings-page__avatar">{{ user.initials }}</span>
            <div class="settings-page__profile-text">
                <span class="settings-page__name">{{ user.name }}</span>
                <span class="settings-page__position">{{ user.position }}</span>
                <span class="settings-page__note">Данные учётной записи приходят из системы банка и здесь не меняются.</span>
            </div>
        </section>

        <section class="settings-page__card">
            <h2 class="settings-page__section-title">Роль</h2>
            <div class="settings-page__row">
                <span class="settings-page__row-text">
                    <span class="settings-page__row-label">Открывать приложение как</span>
                    <span class="settings-page__row-hint">
                        Руководитель видит статистику команды и спорные ответы на проверку.
                    </span>
                </span>
                <UiSegmented
                    v-model="defaultRole"
                    :options="ROLE_OPTIONS"
                    label="Роль по умолчанию"
                />
            </div>
        </section>

        <section class="settings-page__card">
            <h2 class="settings-page__section-title">Уведомления</h2>
            <UiSwitch
                :model-value="settings.notifyUpdates"
                label="Обновления базы знаний"
                hint="Новые редакции регламентов, письма и записки."
                @update:model-value="settingsStore.update('notifyUpdates', $event)"
            />
            <UiSwitch
                :model-value="settings.notifyOutdated"
                label="Устаревшие ответы"
                hint="Когда новая редакция документа меняет вывод в ваших прошлых ответах."
                @update:model-value="settingsStore.update('notifyOutdated', $event)"
            />
            <UiSwitch
                :model-value="settings.notifyDisputed"
                label="Спорные ответы команды"
                :hint="isHead ? 'Юрист отметил ответ как спорный.' : 'Доступно в роли руководителя.'"
                :is-disabled="!isHead"
                @update:model-value="settingsStore.update('notifyDisputed', $event)"
            />
        </section>

        <section class="settings-page__card">
            <h2 class="settings-page__section-title">Ответы</h2>
            <UiSwitch
                :model-value="settings.isStreaming"
                label="Показывать ответ по мере составления"
                hint="Текст появляется сразу, а не после полной проверки."
                @update:model-value="settingsStore.update('isStreaming', $event)"
            />
            <UiSwitch
                :model-value="settings.isPipelineExpanded"
                label="Не сворачивать ход проверки"
                hint="Шаги поиска и самопроверки остаются открытыми под вопросом."
                @update:model-value="settingsStore.update('isPipelineExpanded', $event)"
            />
        </section>

        <section class="settings-page__card">
            <h2 class="settings-page__section-title">Интерфейс</h2>
            <UiSwitch
                :model-value="settings.isMotionReduced"
                label="Уменьшить анимацию"
                hint="Без плавных появлений, подсветки маркером и нити к источнику."
                @update:model-value="settingsStore.update('isMotionReduced', $event)"
            />
        </section>

        <button
            class="settings-page__reset"
            type="button"
            @click="handleReset"
        >
            <RotateCcw
                :size="16"
                aria-hidden="true"
            />
            Сбросить настройки
        </button>
    </div>
</template>

<style lang="scss">
.settings-page {
    max-width: 760px;
    margin: 0 auto;

    @include column($indent-step * 4);

    &__title {
        @include heading($font-size-3xl);
    }

    &__card {
        @include card($radius-2xl);
        @include column($indent-step * 5);
        @include padding('y', 5);
        @include padding('x', 6);
    }

    &__profile {
        flex-direction: row;
        align-items: center;
    }

    &__avatar {
        @include flex-center;

        flex-shrink: 0;
        width: 64px;
        height: 64px;
        color: $color-white;
        border-radius: $radius-pill;
        background-color: $color-action;
        font-size: $font-size-xl;
        font-weight: $font-weight-extrabold;
    }

    &__profile-text {
        @include column($indent-step * 0.5);
    }

    &__name {
        @include heading($font-size-xl);
    }

    &__position {
        color: $color-ink-soft;
        font-size: $font-size-md;
    }

    &__note {
        color: $color-ink-muted;
        font-size: $font-size-sm;

        @include margin('top', 1);
    }

    &__section-title {
        @include heading($font-size-lg);
    }

    &__row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: $indent-step * 4;
    }

    &__row-text {
        flex: 1;
        min-width: 220px;

        @include column($indent-step * 0.5);
    }

    &__row-label {
        color: $color-ink;
        font-size: $font-size-md;
        font-weight: $font-weight-semibold;
    }

    &__row-hint {
        color: $color-ink-muted;
        font-size: $font-size-sm;
        line-height: 1.45;
    }

    &__reset {
        @include button-reset;
        @include focus-ring;
        @include press;

        display: inline-flex;
        align-items: center;
        align-self: flex-start;
        transition:
            color $duration ease,
            transform $duration-fast $ease-out;
        color: $color-ink-soft;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        gap: $indent-step * 2;

        @include padding('y', 2);

        @include hover {
            color: $color-peach-ink;
        }
    }

    @include mobile {
        &__card {
            @include padding('x', 4);
        }
    }
}
</style>
