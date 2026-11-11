<script setup>
import {LoaderCircle, SquarePen} from 'lucide-vue-next';
import {ROUTE_NAMES} from '@/core/constants';

import UiStatusPill from '@/components/Ui/UiStatusPill.vue';

defineProps({
    /** @type {import('vue').PropType<import('@/core/types/assistant').Dialog[]>} */
    dialogs: {type: Array, required: true},
    activeDialogId: {type: String, default: null},
    askingDialogId: {type: String, default: null},
});
</script>

<template>
    <aside class="dialog-list">
        <RouterLink
            class="dialog-list__new"
            :to="{name: ROUTE_NAMES.dialogs}"
        >
            <SquarePen
                :size="18"
                aria-hidden="true"
            />
            Новый вопрос
        </RouterLink>

        <h2 class="dialog-list__title">Диалоги</h2>

        <ul class="dialog-list__items">
            <li
                v-for="dialog in dialogs"
                :key="dialog.id"
            >
                <RouterLink
                    :class="['dialog-list__item', {'dialog-list__item--active': dialog.id === activeDialogId}]"
                    :to="{name: ROUTE_NAMES.dialogs, params: {dialogId: dialog.id}}"
                    :aria-current="dialog.id === activeDialogId ? 'page' : undefined"
                >
                    <span class="dialog-list__row">
                        <span class="dialog-list__number">{{ dialog.number }}</span>
                        <span class="dialog-list__time">{{ dialog.timeLabel }}</span>
                    </span>
                    <span class="dialog-list__name">{{ dialog.title }}</span>
                    <span class="dialog-list__row">
                        <span class="dialog-list__document">{{ dialog.documentLabel }}</span>
                        <LoaderCircle
                            v-if="dialog.id === askingDialogId"
                            class="dialog-list__spinner"
                            :size="16"
                            aria-label="Ищу ответ"
                        />
                        <UiStatusPill
                            v-else-if="dialog.answer"
                            :status="dialog.status"
                        />
                    </span>
                </RouterLink>
            </li>
        </ul>
    </aside>
</template>

<style lang="scss">
.dialog-list {
    $block: &;

    @include column($indent-step * 3);

    &__new {
        @include focus-ring;
        @include sheen;
        @include press;

        display: flex;
        flex-shrink: 0;
        align-items: center;
        justify-content: center;
        transition:
            transform $duration-fast $ease-out,
            box-shadow $duration ease;
        color: $color-white;
        border-radius: $radius-xl;
        background-color: $color-cta;
        box-shadow: 0 10px 22px -14px rgba($color-cta, 80%);
        font-size: $font-size-md;
        font-weight: $font-weight-bold;
        text-decoration: none;
        gap: $indent-step * 2;

        @include padding('y', 3);

        @include hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 26px -14px rgba($color-cta, 85%);
        }
    }

    &__title {
        color: $color-ink-muted;
        font-size: $font-size-xs;

        @include heading($font-size-xs);
        @include margin('top', 2);
    }

    &__items {
        margin: 0;
        padding: 0;
        list-style: none;

        @include column($indent-step * 2);
    }

    &__item {
        @include focus-ring;
        @include column($indent-step * 1.5);
        @include padding('y', 3);
        @include padding('x', 3.5);

        transition:
            border-color $duration ease,
            background-color $duration ease,
            box-shadow $duration ease,
            transform $duration $ease-out;
        color: $color-ink;
        border: 1px solid $color-line;
        border-radius: $radius-xl;
        background-color: $color-surface;
        box-shadow: $shadow-soft;
        text-decoration: none;

        @include hover {
            transform: translateY(-1px);
            border-color: $color-lavender-line;
            box-shadow: $shadow-card;
        }

        &--active {
            border-color: $color-lavender-line;
            background: $color-selected;
            box-shadow: $shadow-card;

            #{$block}__number {
                color: $color-violet;
            }
        }
    }

    &__row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: $indent-step * 2;
    }

    &__number {
        color: $color-ink-muted;
        font-size: $font-size-xs;
        font-weight: $font-weight-extrabold;
    }

    &__time,
    &__document {
        color: $color-ink-faint;
        font-size: $font-size-xs;
        font-weight: $font-weight-semibold;
    }

    &__name {
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        line-height: 1.35;
    }

    &__spinner {
        color: $color-violet;
        animation: spin 0.9s linear infinite;
    }

    @include tablet {
        &__items {
            flex-direction: row;
            overflow-x: auto;

            @include padding('bottom', 1);
        }

        &__items > li {
            flex: 0 0 220px;
        }
    }
}
</style>
