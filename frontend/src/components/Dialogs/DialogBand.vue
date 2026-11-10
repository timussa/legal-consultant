<script setup>
import {computed} from 'vue';
import {CalendarDays, Timer} from 'lucide-vue-next';

import UiSegmented from '@/components/Ui/UiSegmented.vue';
import UiStatusPill from '@/components/Ui/UiStatusPill.vue';

const props = defineProps({
    /** @type {import('vue').PropType<import('@/core/types/assistant').Dialog>} */
    dialog: {type: Object, required: true},
    isAsking: {type: Boolean, default: false},
});

const emit = defineEmits(['change-date']);

const eventDate = computed({
    get: () => props.dialog.eventDate ?? '',
    set: (value) => emit('change-date', value),
});
const dateOptions = computed(() => (props.dialog.eventDates ?? []).map(({value, label}) => ({value, label})));
const context = computed(() => props.dialog.answer?.context ?? []);
</script>

<template>
    <header class="dialog-band">
        <div class="dialog-band__top">
            <span class="dialog-band__number">Диалог {{ dialog.number }}</span>
            <UiStatusPill
                v-if="dialog.answer && !isAsking"
                :status="dialog.answer.status"
                :label="dialog.answer.verdict"
                is-on-brand
            />
        </div>

        <h1 class="dialog-band__title">{{ dialog.title }}</h1>

        <div class="dialog-band__bottom">
            <ul
                v-if="context.length"
                class="dialog-band__context"
            >
                <li
                    v-for="item in context"
                    :key="item.label"
                    class="dialog-band__chip"
                >
                    <span class="dialog-band__chip-label">{{ item.label }}</span>
                    {{ item.value }}
                </li>
                <li
                    v-if="dialog.answer && !isAsking"
                    class="dialog-band__chip"
                >
                    <Timer
                        :size="14"
                        aria-hidden="true"
                    />
                    {{ dialog.answer.totalDurationLabel }}
                </li>
            </ul>

            <div
                v-if="dateOptions.length"
                class="dialog-band__date"
            >
                <span class="dialog-band__date-label">
                    <CalendarDays
                        :size="15"
                        aria-hidden="true"
                    />
                    Дата события
                </span>
                <UiSegmented
                    v-model="eventDate"
                    :options="dateOptions"
                    label="Дата события"
                    :is-disabled="isAsking"
                    is-on-brand
                />
            </div>
        </div>
    </header>
</template>

<style lang="scss">
.dialog-band {
    @include brand-band;
    @include column($indent-step * 3);
    @include padding('y', 6);
    @include padding('x', 7);

    border-radius: $radius-3xl;
    box-shadow: $shadow-raised;

    &::after {
        position: absolute;
        top: -120px;
        right: -80px;
        width: 360px;
        height: 360px;
        border-radius: $radius-pill;
        background: radial-gradient(circle, rgba($color-orange-soft, 45%), transparent 65%);
        content: '';
        pointer-events: none;
    }

    &__top,
    &__bottom,
    &__title {
        position: relative;
        z-index: $ui-index-base;
    }

    &__top {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: $indent-step * 3;
    }

    &__number {
        color: $color-on-brand-soft;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__title {
        line-height: 1.2;

        @include heading($font-size-3xl);
    }

    &__bottom {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: $indent-step * 4;
    }

    &__context {
        display: flex;
        flex-wrap: wrap;
        margin: 0;
        padding: 0;
        list-style: none;
        gap: $indent-step * 2;
    }

    &__chip {
        backdrop-filter: blur(8px);

        @include glass;
        @include pill(rgba($color-white, 14%), $color-white);
    }

    &__chip-label {
        color: $color-on-brand-soft;
        font-weight: $font-weight-semibold;
    }

    &__date {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: $indent-step * 3;
    }

    &__date-label {
        display: inline-flex;
        align-items: center;
        color: $color-on-brand-soft;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
        gap: $indent-step * 1.5;
    }

    @include mobile {
        @include padding('y', 5);
        @include padding('x', 4);

        border-radius: $radius-2xl;

        &__title {
            font-size: $font-size-xl;
        }
    }
}
</style>
