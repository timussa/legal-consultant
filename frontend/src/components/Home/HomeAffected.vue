<script setup>
import {History} from 'lucide-vue-next';
import {ROUTE_NAMES} from '@/core/constants';

defineProps({
    /** @type {import('vue').PropType<import('@/core/types/knowledgeBase').KnowledgeBaseOverview['affected']>} */
    affected: {type: Object, required: true},
});
</script>

<template>
    <section class="home-affected">
        <div class="home-affected__head">
            <span class="home-affected__icon">
                <History
                    :size="20"
                    aria-hidden="true"
                />
            </span>
            <div>
                <h2 class="home-affected__title">Ответы устарели</h2>
                <p class="home-affected__summary">{{ affected.summary }}</p>
            </div>
        </div>
        <ul class="home-affected__list">
            <li
                v-for="answer in affected.answers"
                :key="answer.number"
            >
                <RouterLink
                    class="home-affected__item"
                    :to="{name: ROUTE_NAMES.dialogs, params: {dialogId: answer.dialogId}}"
                >
                    <span class="home-affected__item-title">{{ answer.number }} · {{ answer.title }}</span>
                    <span class="home-affected__reason">{{ answer.reason }}</span>
                    <span class="home-affected__action">Переспросить по новой редакции →</span>
                </RouterLink>
            </li>
        </ul>
    </section>
</template>

<style lang="scss">
.home-affected {
    border: 1px solid $color-peach-line;
    border-radius: $radius-2xl;
    background: linear-gradient(160deg, $color-peach-soft, $color-surface 70%);

    @include column($indent-step * 3);
    @include padding('y', 5);
    @include padding('x', 5);

    &__head {
        display: flex;
        align-items: flex-start;
        gap: $indent-step * 3;
    }

    &__icon {
        @include flex-center;

        flex-shrink: 0;
        width: 40px;
        height: 40px;
        color: $color-white;
        border-radius: $radius-lg;
        background: linear-gradient(135deg, $color-orange, $color-orange-soft);
    }

    &__title {
        @include heading($font-size-lg);
    }

    &__summary {
        margin: 0;
        color: $color-peach-deep;
        font-size: $font-size-sm;
        line-height: 1.5;

        @include margin('top', 1);
    }

    &__list {
        margin: 0;
        padding: 0;
        list-style: none;

        @include column($indent-step * 2);
    }

    &__item {
        @include focus-ring;
        @include column($indent-step);
        @include padding('y', 3);
        @include padding('x', 3.5);

        transition:
            border-color $duration ease,
            box-shadow $duration ease;
        color: $color-ink;
        border: 1px solid $color-line;
        border-radius: $radius-xl;
        background: $color-surface;
        text-decoration: none;

        @include hover {
            border-color: $color-peach-line;
            box-shadow: $shadow-card;
        }
    }

    &__item-title {
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__reason {
        color: $color-ink-soft;
        font-size: $font-size-xs;
        line-height: 1.5;
    }

    &__action {
        color: $color-orange;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
    }
}
</style>
