<script setup>
import {TriangleAlert} from 'lucide-vue-next';

defineProps({
    /** @type {import('vue').PropType<import('@/core/types/knowledgeBase').TeamStat[]>} */
    stats: {type: Array, required: true},
});
</script>

<template>
    <section class="home-team-stats">
        <h2 class="home-team-stats__title">Команда за неделю</h2>
        <ul class="home-team-stats__list">
            <li
                v-for="stat in stats"
                :key="stat.id"
                :class="['home-team-stats__item', {'home-team-stats__item--alert': stat.isAlert}]"
            >
                <span class="home-team-stats__value">
                    <TriangleAlert
                        v-if="stat.isAlert"
                        :size="20"
                        aria-hidden="true"
                    />
                    {{ stat.value }}
                </span>
                <span class="home-team-stats__label">{{ stat.label }}</span>
            </li>
        </ul>
    </section>
</template>

<style lang="scss">
.home-team-stats {
    @include column($indent-step * 3);

    &__title {
        @include heading;
    }

    &__list {
        display: grid;
        margin: 0;
        padding: 0;
        list-style: none;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: $indent-step * 4;
    }

    &__item {
        @include card($radius-2xl);
        @include column($indent-step);
        @include padding('y', 4);
        @include padding('x', 5);

        &--alert {
            border-color: $color-peach-line;
            background: $color-peach-soft;
            color: $color-peach-ink;
        }
    }

    &__value {
        display: flex;
        align-items: center;
        gap: $indent-step * 2;

        @include heading($font-size-3xl);
    }

    &__label {
        color: $color-ink-muted;
        font-size: $font-size-sm;
    }

    @include tablet {
        &__list {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
}
</style>
