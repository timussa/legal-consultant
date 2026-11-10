<script setup>
import {computed} from 'vue';
import {Timer} from 'lucide-vue-next';
import {formatLongDate} from '@/core/utils/date';

import UiSegmented from '@/components/Ui/UiSegmented.vue';
import UiStatusPill from '@/components/Ui/UiStatusPill.vue';

const EDITION_LABEL = 'Регламент';

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
const dateOptions = computed(() =>
    (props.dialog.eventDates ?? []).map(({value, label, hint}) => ({value, label: hint ? `${label}, ${hint}` : label})),
);
const hasDates = computed(() => dateOptions.value.length > 0 && Boolean(props.dialog.eventDate));
const context = computed(() => props.dialog.answer?.context ?? []);
const chips = computed(() =>
    hasDates.value ? context.value.filter((item) => item.label !== EDITION_LABEL) : context.value,
);
const editionNote = computed(() => {
    if (props.isAsking) {
        return 'Подбираю редакцию документов…';
    }

    const edition = context.value.find((item) => item.label === EDITION_LABEL);

    return edition ? `Применяется регламент ${edition.value}` : '';
});
</script>

<template>
    <header :class="['dialog-band', {'dialog-band--dated': hasDates}]">
        <div class="dialog-band__main">
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

            <ul
                v-if="chips.length || (dialog.answer && !isAsking)"
                class="dialog-band__context"
            >
                <li
                    v-for="item in chips"
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
        </div>

        <div
            v-if="hasDates"
            class="dialog-band__date"
        >
            <span class="dialog-band__date-label">Дата события</span>
            <Transition
                name="dialog-band__date-value"
                mode="out-in"
            >
                <span
                    :key="eventDate"
                    class="dialog-band__date-value"
                >
                    {{ formatLongDate(eventDate) }}
                </span>
            </Transition>
            <span class="dialog-band__date-edition">{{ editionNote }}</span>
            <UiSegmented
                v-model="eventDate"
                class="dialog-band__date-switch"
                :options="dateOptions"
                label="Дата события"
                :is-disabled="isAsking"
                is-on-brand
            />
        </div>
    </header>
</template>

<style lang="scss">
.dialog-band {
    @include brand-band;
    @include padding('y', 6);
    @include padding('x', 7);

    display: grid;
    align-items: center;
    border-radius: $radius-3xl;
    grid-template-columns: minmax(0, 1fr);
    gap: $indent-step * 8;

    &--dated {
        grid-template-columns: minmax(0, 1fr) auto;
    }

    &__main {
        min-width: 0;

        @include column($indent-step * 3);
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
        flex-direction: column;
        align-items: flex-end;
        text-align: right;
        gap: $indent-step;
    }

    &__date-label {
        color: $color-on-brand-soft;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
    }

    &__date-value {
        font-family: $font-document;
        font-size: $font-size-display;
        font-weight: $font-weight-regular;
        line-height: 1.1;
        white-space: nowrap;

        &-enter-active,
        &-leave-active {
            transition:
                opacity $duration ease,
                transform $duration $ease-out;
        }

        &-enter-from {
            transform: translateY(6px);
            opacity: 0;
        }

        &-leave-to {
            transform: translateY(-6px);
            opacity: 0;
        }
    }

    &__date-edition {
        min-height: 1.5em;
        color: $color-on-brand-muted;
        font-family: $font-document;
        font-size: $font-size-base;
        font-style: italic;
    }

    &__date-switch {
        @include margin('top', 2);
    }

    @include laptop {
        &--dated {
            grid-template-columns: minmax(0, 1fr);
        }

        &__date {
            align-items: flex-start;
            text-align: left;
        }
    }

    @include mobile {
        @include padding('y', 5);
        @include padding('x', 4);

        border-radius: $radius-2xl;

        &__title {
            font-size: $font-size-xl;
        }

        &__date-value {
            font-size: $font-size-4xl;
            white-space: normal;
        }
    }
}
</style>
