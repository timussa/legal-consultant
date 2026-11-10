<script setup>
import {computed} from 'vue';
import {GitCompareArrows, Paperclip, TriangleAlert} from 'lucide-vue-next';
import {SECTION_IMAGES} from '@/assets/images';

import UiSegmented from '@/components/Ui/UiSegmented.vue';

const props = defineProps({
    /** @type {import('vue').PropType<import('@/core/types/document').LegalDocument>} */
    document: {type: Object, required: true},
    changedCount: {type: Number, default: 0},
    canCompare: {type: Boolean, default: false},
});

const editionId = defineModel('editionId', {type: String, required: true});
const isCompare = defineModel('isCompare', {type: Boolean, default: false});

const editionOptions = computed(() =>
    props.document.editions.map((edition) => ({value: edition.id, label: edition.label, hint: edition.date})),
);
const edition = computed(() => props.document.editions.find((item) => item.id === editionId.value));
</script>

<template>
    <header class="document-band">
        <div class="document-band__main">
            <span class="document-band__kind">{{ document.kindLabel }}</span>
            <h1 class="document-band__title">{{ document.title }}</h1>
            <div class="document-band__controls">
                <UiSegmented
                    v-model="editionId"
                    :options="editionOptions"
                    label="Редакция документа"
                    is-on-brand
                />
                <button
                    v-if="canCompare"
                    :class="['document-band__compare', {'document-band__compare--active': isCompare}]"
                    type="button"
                    :aria-pressed="isCompare"
                    @click="isCompare = !isCompare"
                >
                    <GitCompareArrows
                        :size="16"
                        aria-hidden="true"
                    />
                    Было / стало
                    <span
                        v-if="changedCount"
                        class="document-band__compare-count"
                    >
                        {{ changedCount }}
                    </span>
                </button>
            </div>
            <p
                v-if="edition?.note"
                class="document-band__note"
            >
                <TriangleAlert
                    :size="15"
                    aria-hidden="true"
                />
                Редакция {{ edition.note }}. Ответы по ней верны только для событий до этой даты.
            </p>
            <ul class="document-band__files">
                <li
                    v-for="file in document.files"
                    :key="file"
                    class="document-band__file"
                >
                    <Paperclip
                        :size="13"
                        aria-hidden="true"
                    />
                    {{ file }}
                </li>
            </ul>
        </div>
        <img
            v-if="SECTION_IMAGES[document.image]"
            class="document-band__art"
            :src="SECTION_IMAGES[document.image]"
            alt=""
        />
    </header>
</template>

<style lang="scss">
.document-band {
    @include brand-band;
    @include padding('y', 6);
    @include padding('x', 7);

    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: $radius-3xl;
    box-shadow: $shadow-raised;
    gap: $indent-step * 6;

    &__main {
        position: relative;
        z-index: $ui-index-base;
        min-width: 0;

        @include column($indent-step * 3);
    }

    &__kind {
        color: $color-on-brand-soft;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__title {
        @include heading($font-size-3xl);
    }

    &__controls {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: $indent-step * 3;
    }

    &__compare {
        @include button-reset;
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        transition: background $duration ease;
        border-radius: $radius-pill;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        backdrop-filter: blur(10px);
        gap: $indent-step * 2;

        @include glass;
        @include padding('y', 2);
        @include padding('x', 3.5);

        @include hover {
            background: rgba($color-white, 24%);
        }

        &--active {
            color: $color-navy;
            background: $color-white;

            @include hover {
                background: $color-white;
            }
        }
    }

    &__compare-count {
        @include pill($color-orange, $color-white);

        font-size: $font-size-2xs;

        @include padding('y', 0);
        @include padding('x', 1.5);
    }

    &__note {
        display: inline-flex;
        align-items: center;
        align-self: flex-start;
        margin: 0;
        color: $color-amber-ink;
        border-radius: $radius-lg;
        background: $color-amber;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
        gap: $indent-step * 2;

        @include padding('y', 1.5);
        @include padding('x', 3);
    }

    &__files {
        display: flex;
        flex-wrap: wrap;
        margin: 0;
        padding: 0;
        list-style: none;
        gap: $indent-step * 2;
    }

    &__file {
        display: inline-flex;
        align-items: center;
        color: $color-on-brand-muted;
        font-size: $font-size-xs;
        font-weight: $font-weight-semibold;
        gap: $indent-step;
    }

    &__art {
        position: relative;
        z-index: $ui-index-base;
        flex-shrink: 0;
        width: 148px;
        border-radius: $radius-2xl;
        filter: drop-shadow(0 24px 30px rgba($color-ink, 35%));
    }

    @include tablet {
        &__art {
            display: none;
        }
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
