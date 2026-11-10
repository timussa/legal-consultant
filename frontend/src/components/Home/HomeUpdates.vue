<script setup>
defineProps({
    /** @type {import('vue').PropType<import('@/core/types/knowledgeBase').BaseUpdate[]>} */
    updates: {type: Array, required: true},
});
</script>

<template>
    <section class="home-updates">
        <h2 class="home-updates__title">Обновления базы</h2>
        <ol class="home-updates__list">
            <li
                v-for="update in updates"
                :key="update.id"
                :class="['home-updates__item', {'home-updates__item--new': update.isNew}]"
            >
                <span class="home-updates__name">
                    {{ update.title }}
                    <span
                        v-if="update.isNew"
                        class="home-updates__badge"
                    >
                        новое
                    </span>
                </span>
                <span class="home-updates__text">{{ update.text }}</span>
                <span class="home-updates__meta">{{ update.meta }}</span>
            </li>
        </ol>
    </section>
</template>

<style lang="scss">
.home-updates {
    box-shadow: $shadow-card;

    @include card($radius-2xl);
    @include column($indent-step * 3);
    @include padding('y', 5);
    @include padding('x', 5);

    &__title {
        @include heading($font-size-lg);
    }

    &__list {
        margin: 0;
        padding: 0;
        list-style: none;

        @include column($indent-step * 4);
    }

    &__item {
        position: relative;

        @include column($indent-step);
        @include padding('left', 5);

        &::before {
            position: absolute;
            top: 6px;
            left: 0;
            width: 8px;
            height: 8px;
            border-radius: $radius-pill;
            background: $color-line-strong;
            content: '';
        }

        &--new::before {
            background: $color-orange;
            box-shadow: 0 0 0 4px rgba($color-orange, 18%);
        }
    }

    &__name {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        gap: $indent-step * 2;
    }

    &__badge {
        @include pill($color-peach, $color-peach-ink);

        font-size: $font-size-2xs;

        @include padding('y', 0.5);
        @include padding('x', 2);
    }

    &__text {
        color: $color-ink-soft;
        font-size: $font-size-xs;
        line-height: 1.5;
    }

    &__meta {
        color: $color-ink-faint;
        font-size: $font-size-2xs;
        font-weight: $font-weight-semibold;
    }
}
</style>
