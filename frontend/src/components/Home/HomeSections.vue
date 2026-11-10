<script setup>
import {ArrowUpRight} from 'lucide-vue-next';
import {SECTION_IMAGES} from '@/assets/images';
import {ROUTE_NAMES} from '@/core/constants';

defineProps({
    /** @type {import('vue').PropType<import('@/core/types/knowledgeBase').KnowledgeSection[]>} */
    sections: {type: Array, required: true},
});

const emit = defineEmits(['unavailable']);

/** @param {import('@/core/types/knowledgeBase').KnowledgeSection} section */
function getTarget(section) {
    return {name: ROUTE_NAMES.document, params: {documentId: section.documentId}};
}

/** @param {import('@/core/types/knowledgeBase').KnowledgeSection} section */
function handleCardClick(section) {
    if (!section.documentId) {
        emit('unavailable', section);
    }
}
</script>

<template>
    <section class="home-sections">
        <div class="home-sections__head">
            <h2 class="home-sections__title">Разделы базы знаний</h2>
            <span class="home-sections__caption">
                Законы — в действующей редакции, договоры — с учётом допсоглашений
            </span>
        </div>

        <ul class="home-sections__grid">
            <li
                v-for="section in sections"
                :key="section.id"
            >
                <component
                    :is="section.documentId ? 'RouterLink' : 'button'"
                    :to="section.documentId ? getTarget(section) : undefined"
                    :type="section.documentId ? undefined : 'button'"
                    class="home-sections__card"
                    @click="handleCardClick(section)"
                >
                    <span
                        :class="['home-sections__art', {'home-sections__art--initials': !section.image}]"
                        aria-hidden="true"
                    >
                        <img
                            v-if="section.image"
                            class="home-sections__image"
                            :src="SECTION_IMAGES[section.image]"
                            alt=""
                        />
                        <template v-else>{{ section.initials }}</template>
                    </span>
                    <span class="home-sections__body">
                        <span class="home-sections__name">{{ section.title }}</span>
                        <span class="home-sections__subtitle">{{ section.subtitle }}</span>
                        <span class="home-sections__meta">
                            {{ section.documentCount }} док. · {{ section.updatedLabel }}
                        </span>
                    </span>
                    <ArrowUpRight
                        class="home-sections__arrow"
                        :size="18"
                        aria-hidden="true"
                    />
                </component>
            </li>
        </ul>
    </section>
</template>

<style lang="scss">
.home-sections {
    $block: &;

    @include column($indent-step * 4);

    &__head {
        display: flex;
        flex-wrap: wrap;
        align-items: baseline;
        justify-content: space-between;
        gap: $indent-step * 2;
    }

    &__title {
        @include heading;
    }

    &__caption {
        color: $color-ink-muted;
        font-size: $font-size-sm;
    }

    &__grid {
        display: grid;
        margin: 0;
        padding: 0;
        list-style: none;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: $indent-step * 4;
    }

    &__card {
        @include button-reset;
        @include card($radius-2xl);
        @include focus-ring;

        position: relative;
        display: flex;
        align-items: center;
        width: 100%;
        height: 100%;
        transition:
            transform $duration $ease-out,
            box-shadow $duration ease,
            border-color $duration ease;
        color: $color-ink;
        text-align: left;
        text-decoration: none;
        gap: $indent-step * 4;

        @include padding('y', 4);
        @include padding('left', 4);
        @include padding('right', 10);

        @include hover {
            transform: translateY(-2px);
            border-color: $color-lavender-line;
            box-shadow: $shadow-card;

            #{$block}__arrow {
                color: $color-violet;
                transform: translate(2px, -2px);
            }
        }
    }

    &__art {
        @include flex-center;

        flex-shrink: 0;
        width: 76px;
        height: 76px;
        border-radius: $radius-xl;
        background: $color-icon-tile;

        &--initials {
            color: $color-navy;
            background: $gradient-selected;
            font-size: $font-size-xl;
            font-weight: $font-weight-extrabold;
        }
    }

    &__image {
        width: 72px;
        height: 72px;
        object-fit: contain;
    }

    &__body {
        @include column($indent-step);
    }

    &__name {
        font-size: $font-size-base;
        font-weight: $font-weight-extrabold;
    }

    &__subtitle {
        color: $color-ink-soft;
        font-size: $font-size-sm;
    }

    &__meta {
        color: $color-ink-faint;
        font-size: $font-size-xs;
        font-weight: $font-weight-semibold;
    }

    &__arrow {
        position: absolute;
        top: $indent-step * 4;
        right: $indent-step * 4;
        transition:
            color $duration ease,
            transform $duration $ease-out;
        color: $color-ink-faint;
    }

    @include tablet {
        &__grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @include mobile {
        &__grid {
            grid-template-columns: 1fr;
        }
    }
}
</style>
