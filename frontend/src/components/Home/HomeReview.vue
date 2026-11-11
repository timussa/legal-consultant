<script setup>
import {Check, PenLine} from 'lucide-vue-next';
import {REVIEW_DECISIONS, ROUTE_NAMES} from '@/core/constants';

defineProps({
    /** @type {import('vue').PropType<import('@/core/types/knowledgeBase').RecentAnswer[]>} */
    answers: {type: Array, required: true},
    /** @type {import('vue').PropType<Record<string, string>>} */
    decisions: {type: Object, default: () => ({})},
});

const emit = defineEmits(['review']);

const DECISION_LABELS = Object.freeze({
    [REVIEW_DECISIONS.approved]: 'Подтверждено вами',
    [REVIEW_DECISIONS.needsFix]: 'Отправлено на доработку',
});
</script>

<template>
    <section class="home-review">
        <div class="home-review__head">
            <h2 class="home-review__title">На проверку</h2>
            <p class="home-review__caption">Юристы отметили эти ответы как спорные. Проверьте основания и примите решение.</p>
        </div>

        <ul class="home-review__list">
            <li
                v-for="answer in answers"
                :key="answer.id"
                :class="['home-review__item', {'home-review__item--done': decisions[answer.id]}]"
            >
                <div class="home-review__body">
                    <RouterLink
                        class="home-review__question"
                        :to="{name: ROUTE_NAMES.dialogs, params: {dialogId: answer.dialogId}}"
                    >
                        {{ answer.number }} {{ answer.question }}
                    </RouterLink>
                    <span class="home-review__preview">{{ answer.preview }}</span>
                    <span class="home-review__meta">{{ answer.author }}, {{ answer.documentLabel }}, {{ answer.dateLabel }}</span>
                </div>

                <span
                    v-if="decisions[answer.id]"
                    :class="['home-review__result', `home-review__result--${decisions[answer.id]}`]"
                >
                    {{ DECISION_LABELS[decisions[answer.id]] }}
                </span>
                <div
                    v-else
                    class="home-review__actions"
                >
                    <button
                        class="home-review__action home-review__action--approve"
                        type="button"
                        @click="emit('review', answer, REVIEW_DECISIONS.approved)"
                    >
                        <Check
                            :size="15"
                            aria-hidden="true"
                        />
                        Ответ верный
                    </button>
                    <button
                        class="home-review__action"
                        type="button"
                        @click="emit('review', answer, REVIEW_DECISIONS.needsFix)"
                    >
                        <PenLine
                            :size="15"
                            aria-hidden="true"
                        />
                        Нужна правка
                    </button>
                </div>
            </li>
        </ul>
    </section>
</template>

<style lang="scss">
.home-review {
    box-shadow: $shadow-card;

    @include card($radius-2xl);
    @include column($indent-step * 4);
    @include padding('y', 5);
    @include padding('x', 5);

    &__head {
        @include column($indent-step);
    }

    &__title {
        @include heading;
    }

    &__caption {
        margin: 0;
        color: $color-ink-muted;
        font-size: $font-size-sm;
    }

    &__list {
        margin: 0;
        padding: 0;
        list-style: none;

        @include column(0);
    }

    &__item {
        display: flex;
        align-items: center;
        transition: opacity $duration ease;
        border-top: 1px solid $color-line-soft;
        gap: $indent-step * 4;

        @include padding('y', 3.5);

        &:first-child {
            border-top: none;
        }

        &--done {
            opacity: 0.7;
        }
    }

    &__body {
        flex: 1;
        min-width: 0;

        @include column($indent-step * 0.5);
    }

    &__question {
        @include focus-ring;

        color: $color-ink;
        font-size: $font-size-md;
        font-weight: $font-weight-bold;
        text-decoration: none;

        @include hover {
            color: $color-violet;
        }
    }

    &__preview {
        color: $color-ink-soft;
        font-size: $font-size-sm;
    }

    &__meta {
        color: $color-ink-faint;
        font-size: $font-size-xs;
        font-weight: $font-weight-semibold;
    }

    &__actions {
        display: flex;
        flex-shrink: 0;
        gap: $indent-step * 2;
    }

    &__action {
        @include button-reset;
        @include focus-ring;
        @include press;

        display: inline-flex;
        align-items: center;
        transition:
            background-color $duration ease,
            border-color $duration ease,
            transform $duration-fast $ease-out;
        color: $color-navy;
        border: 1px solid $color-line;
        border-radius: $radius-lg;
        background-color: $color-surface;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        gap: $indent-step * 1.5;

        @include padding('y', 2);
        @include padding('x', 3);

        @include hover {
            border-color: $color-lavender-line;
            background-color: $color-lavender-soft;
        }

        &--approve {
            color: $color-white;
            border-color: transparent;
            background-color: $color-cta;

            @include hover {
                border-color: transparent;
                background-color: $color-cta-hover;
            }
        }
    }

    &__result {
        flex-shrink: 0;

        @include pill;

        &--needs-fix {
            color: $color-peach-ink;
            background: $color-peach;
        }
    }

    @include mobile {
        &__item {
            flex-direction: column;
            align-items: flex-start;
        }
    }
}
</style>
