<script setup>
import {Paperclip} from 'lucide-vue-next';
import {SECTION_IMAGES} from '@/assets/images';

defineProps({
    /** @type {import('vue').PropType<import('@/core/types/document').LegalDocument>} */
    document: {type: Object, required: true},
});
</script>

<template>
    <header class="document-band">
        <div class="document-band__main">
            <span class="document-band__kind">{{ document.kindLabel }}</span>
            <h1 class="document-band__title">{{ document.title }}</h1>
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
    @include light-band;
    @include padding('y', 6);
    @include padding('x', 7);

    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: $radius-3xl;
    gap: $indent-step * 6;

    &__main {
        position: relative;
        z-index: $ui-index-base;
        min-width: 0;

        @include column($indent-step * 3);
    }

    &__kind {
        color: $color-ink-muted;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__title {
        @include heading($font-size-3xl);
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
        color: $color-ink-soft;
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
            }

    @include tablet {
        &__art {
            width: 88px;
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
