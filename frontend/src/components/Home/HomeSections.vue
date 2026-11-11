<script setup>
import {computed} from 'vue';
import {ArrowRight, ChevronRight} from 'lucide-vue-next';
import {SECTION_IMAGES} from '@/assets/images';
import {ROUTE_NAMES} from '@/core/constants';
import {pluralize} from '@/core/utils/plural';

/** @typedef {import('@/core/types/knowledgeBase').KnowledgeSection} KnowledgeSection */

const props = defineProps({
    /** @type {import('vue').PropType<KnowledgeSection[]>} */
    sections: {type: Array, required: true},
});

const emit = defineEmits(['unavailable']);

const featured = computed(() => props.sections[0]);
const rest = computed(() => props.sections.slice(1));

/** @param {KnowledgeSection} section */
function getTarget(section) {
    return {name: ROUTE_NAMES.document, params: {documentId: section.documentId}};
}

/** @param {number} count */
function formatCount(count) {
    return `${count} ${pluralize(count, ['документ', 'документа', 'документов'])}`;
}

/** @param {KnowledgeSection} section */
function handleRowClick(section) {
    if (!section.documentId) {
        emit('unavailable', section);
    }
}
</script>

<template>
    <section class="home-sections">
        <h2 class="home-sections__title">Разделы базы знаний</h2>

        <div class="home-sections__layout">
            <RouterLink
                v-if="featured"
                class="home-sections__featured"
                :to="getTarget(featured)"
            >
                <img
                    class="home-sections__featured-image"
                    :src="SECTION_IMAGES[featured.image]"
                    alt=""
                />
                <span class="home-sections__featured-body">
                    <span class="home-sections__featured-name">{{ featured.title }}</span>
                    <span class="home-sections__featured-text">
                        {{ featured.subtitle }}. Чаще всего юристы спрашивают про согласование и сроки оплаты.
                    </span>
                    <span class="home-sections__featured-meta">
                        {{ formatCount(featured.documentCount) }}, {{ featured.updatedLabel }}
                    </span>
                    <span class="home-sections__featured-action">
                        Открыть договор П-17/2024
                        <ArrowRight
                            :size="16"
                            aria-hidden="true"
                        />
                    </span>
                </span>
            </RouterLink>

            <ul class="home-sections__list">
                <li
                    v-for="section in rest"
                    :key="section.id"
                >
                    <component
                        :is="section.documentId ? 'RouterLink' : 'button'"
                        :to="section.documentId ? getTarget(section) : undefined"
                        :type="section.documentId ? undefined : 'button'"
                        class="home-sections__row"
                        @click="handleRowClick(section)"
                    >
                        <img
                            v-if="section.image"
                            class="home-sections__row-image"
                            :src="SECTION_IMAGES[section.image]"
                            alt=""
                        />
                        <span class="home-sections__row-body">
                            <span class="home-sections__row-name">{{ section.title }}</span>
                            <span class="home-sections__row-text">{{ section.subtitle }}</span>
                        </span>
                        <span class="home-sections__row-count">{{ formatCount(section.documentCount) }}</span>
                        <ChevronRight
                            class="home-sections__row-chevron"
                            :size="18"
                            aria-hidden="true"
                        />
                    </component>
                </li>
            </ul>
        </div>
    </section>
</template>

<style lang="scss">
.home-sections {
    $block: &;

    @include column($indent-step * 4);

    &__title {
        @include heading;
    }

    &__layout {
        display: grid;
        align-items: stretch;
        grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
        gap: $indent-step * 5;
    }

    &__featured {
        @include focus-ring;
        @include card($radius-3xl);

        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        overflow: hidden;
        min-height: 360px;
        transition:
            box-shadow $duration ease,
            border-color $duration ease;
        color: $color-ink;
        background-color: $color-icon-tile;
        text-decoration: none;

        @include padding('y', 7);
        @include padding('x', 7);

        @include hover {
            border-color: $color-lavender-line;
            box-shadow: $shadow-card;

            #{$block}__featured-image {
                transform: scale(1.04) rotate(-2deg);
            }
        }
    }

    &__featured-image {
        position: absolute;
        top: $indent-step * 4;
        right: $indent-step * 4;
        width: 210px;
        transition: transform 0.6s $ease-out;
    }

    &__featured-body {
        position: relative;
        max-width: 380px;

        @include column($indent-step * 2);
    }

    &__featured-name {
        line-height: 1.15;

        @include heading($font-size-3xl);
    }

    &__featured-text {
        color: $color-ink-soft;
        font-size: $font-size-base;
        line-height: 1.55;
    }

    &__featured-meta {
        color: $color-ink-muted;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
    }

    &__featured-action {
        display: inline-flex;
        align-items: center;
        align-self: flex-start;
        color: $color-navy;
        font-size: $font-size-md;
        font-weight: $font-weight-bold;
        gap: $indent-step * 2;

        @include margin('top', 2);
    }

    &__list {
        margin: 0;
        padding: 0;
        list-style: none;

        @include card($radius-3xl);
        @include padding('y', 2);
        @include padding('x', 2);
    }

    &__list > li + li {
        border-top: 1px solid $color-line-soft;
    }

    &__row {
        @include button-reset;
        @include focus-ring;

        display: flex;
        align-items: center;
        width: 100%;
        transition: background-color $duration ease;
        color: $color-ink;
        border-radius: $radius-xl;
        text-align: left;
        text-decoration: none;
        gap: $indent-step * 4;

        @include padding('y', 3);
        @include padding('x', 3);

        @include hover {
            background-color: $color-surface-soft;

            #{$block}__row-chevron {
                transform: translateX(2px);
                color: $color-navy;
            }
        }
    }

    &__row-image {
        flex-shrink: 0;
        width: 48px;
        height: 48px;
        object-fit: contain;
    }

    &__row-body {
        flex: 1;
        min-width: 0;

        @include column(0);
    }

    &__row-name {
        font-size: $font-size-base;
        font-weight: $font-weight-bold;
    }

    &__row-text {
        color: $color-ink-muted;
        font-size: $font-size-sm;
    }

    &__row-count {
        flex-shrink: 0;
        color: $color-ink-soft;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        font-variant-numeric: tabular-nums;
    }

    &__row-chevron {
        flex-shrink: 0;
        transition:
            color $duration ease,
            transform $duration $ease-out;
        color: $color-ink-decor;
    }

    @include tablet {
        &__layout {
            grid-template-columns: minmax(0, 1fr);
        }

        &__featured {
            min-height: 300px;
        }
    }

    @include mobile {
        &__featured-image {
            width: 140px;
        }

        &__row-count {
            display: none;
        }
    }
}
</style>
