<script setup>
import {computed} from 'vue';
import {STAT_IMAGES} from '@/assets/images';

const props = defineProps({
    /** @type {import('vue').PropType<import('@/core/types/knowledgeBase').KnowledgeBaseOverview['stats']>} */
    stats: {type: Object, required: true},
});

const items = computed(() => [
    {id: 'documents', value: props.stats.documentCount, label: 'документ в базе знаний', image: STAT_IMAGES.documents},
    {
        id: 'verified',
        value: props.stats.citedShare,
        label: 'утверждений со ссылкой на пункт',
        image: STAT_IMAGES.verified,
    },
    {id: 'time', value: props.stats.averageAnswerTime, label: 'среднее время ответа', image: STAT_IMAGES.time},
]);
</script>

<template>
    <section
        class="home-stats"
        aria-label="Показатели базы знаний"
    >
        <ul class="home-stats__list">
            <li
                v-for="item in items"
                :key="item.id"
                class="home-stats__item"
            >
                <img
                    class="home-stats__image"
                    :src="item.image"
                    alt=""
                />
                <span class="home-stats__text">
                    <span class="home-stats__value">{{ item.value }}</span>
                    <span class="home-stats__label">{{ item.label }}</span>
                </span>
            </li>
        </ul>
        <p class="home-stats__note">{{ stats.metricsNote }}</p>
    </section>
</template>

<style lang="scss">
.home-stats {
    @include column($indent-step * 2);

    &__list {
        display: grid;
        margin: 0;
        padding: 0;
        list-style: none;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: $indent-step * 4;
    }

    &__item {
        display: flex;
        align-items: center;
        box-shadow: $shadow-card;
        gap: $indent-step * 4;

        @include card($radius-2xl);
        @include padding('y', 4);
        @include padding('x', 5);
    }

    &__image {
        flex-shrink: 0;
        width: 64px;
        height: 64px;
        object-fit: contain;
    }

    &__text {
        @include column($indent-step * 0.5);
    }

    &__value {
        line-height: 1;
        color: $color-navy;

        @include heading($font-size-4xl);
    }

    &__label {
        color: $color-ink-muted;
        font-size: $font-size-sm;
        font-weight: $font-weight-medium;
    }

    &__note {
        margin: 0;
        color: $color-ink-faint;
        font-size: $font-size-xs;
        text-align: right;
    }

    @include tablet {
        &__list {
            grid-template-columns: minmax(0, 1fr);
            gap: $indent-step * 3;
        }
    }
}
</style>
