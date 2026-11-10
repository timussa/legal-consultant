<script setup>
import {computed} from 'vue';
import {
    ArrowRight,
    CalendarClock,
    Copy,
    FileSearch,
    Flag,
    MessageCircleQuestion,
    Sparkles,
    ThumbsDown,
    ThumbsUp,
} from 'lucide-vue-next';
import {ANSWER_STATUSES, FEEDBACK_VALUES} from '@/core/constants';

import UiCiteBadge from '@/components/Ui/UiCiteBadge.vue';

const FEEDBACK_OPTIONS = Object.freeze([
    {value: FEEDBACK_VALUES.correct, label: 'Верно', icon: ThumbsUp},
    {value: FEEDBACK_VALUES.wrong, label: 'Ошибка', icon: ThumbsDown},
    {value: FEEDBACK_VALUES.disputed, label: 'Спорно, на проверку', icon: Flag},
]);

const props = defineProps({
    /** @type {import('vue').PropType<import('@/core/types/assistant').Answer>} */
    answer: {type: Object, required: true},
    revealedCiteCount: {type: Number, default: 0},
    activeCite: {type: Number, default: null},
    feedback: {type: String, default: null},
});

const emit = defineEmits([
    'activate-cite',
    'deactivate-cite',
    'select-cite',
    'ask',
    'choose-option',
    'feedback',
    'copy',
]);

const isRefusal = computed(() => props.answer.status === ANSWER_STATUSES.refusal);
const isClarification = computed(() => props.answer.status === ANSWER_STATUSES.clarification);
const citeOrder = computed(() => {
    const order = {};
    let position = 0;

    props.answer.paragraphs.forEach((paragraph, paragraphIndex) => {
        paragraph.forEach((part, partIndex) => {
            if (part.cite !== undefined) {
                order[`${paragraphIndex}-${partIndex}`] = position;
                position += 1;
            }
        });
    });

    return order;
});

/**
 * @param {number} paragraphIndex
 * @param {number} partIndex
 */
function isCiteRevealed(paragraphIndex, partIndex) {
    return citeOrder.value[`${paragraphIndex}-${partIndex}`] < props.revealedCiteCount;
}
</script>

<template>
    <article :class="['dialog-answer', `dialog-answer--${answer.status}`]">
        <div
            v-if="answer.dateNote"
            class="dialog-answer__date-note"
        >
            <CalendarClock
                :size="18"
                aria-hidden="true"
            />
            {{ answer.dateNote }}
        </div>

        <div class="dialog-answer__head">
            <span class="dialog-answer__avatar">
                <FileSearch
                    v-if="isRefusal"
                    :size="18"
                    aria-hidden="true"
                />
                <MessageCircleQuestion
                    v-else-if="isClarification"
                    :size="18"
                    aria-hidden="true"
                />
                <Sparkles
                    v-else
                    :size="18"
                    aria-hidden="true"
                />
            </span>
            <span class="dialog-answer__author">Юрассистент</span>
            <span class="dialog-answer__verdict">{{ answer.verdict }}</span>
        </div>

        <div class="dialog-answer__text">
            <p
                v-for="(paragraph, paragraphIndex) in answer.paragraphs"
                :key="paragraphIndex"
                class="dialog-answer__paragraph"
            >
                <template
                    v-for="(part, partIndex) in paragraph"
                    :key="partIndex"
                >
                    <UiCiteBadge
                        v-if="part.cite !== undefined"
                        :number="part.cite"
                        :is-active="activeCite === part.cite"
                        :is-revealed="isCiteRevealed(paragraphIndex, partIndex)"
                        @activate="emit('activate-cite', $event)"
                        @deactivate="emit('deactivate-cite', $event)"
                        @select="emit('select-cite', $event)"
                    />
                    <mark
                        v-else-if="part.isChanged"
                        :class="['dialog-answer__changed', {'dialog-answer__changed--bold': part.isBold}]"
                        title="Зависит от даты события"
                    >
                        {{ part.text }}
                    </mark>
                    <strong
                        v-else-if="part.isBold"
                        class="dialog-answer__bold"
                    >
                        {{ part.text }}
                    </strong>
                    <template v-else>{{ part.text }}</template>
                </template>
            </p>
        </div>

        <div
            v-if="answer.checkedDocuments?.length"
            class="dialog-answer__checked"
        >
            <span class="dialog-answer__label">Что проверено</span>
            <ul class="dialog-answer__checked-list">
                <li
                    v-for="document in answer.checkedDocuments"
                    :key="document"
                    class="dialog-answer__checked-item"
                >
                    {{ document }}
                </li>
            </ul>
        </div>

        <div
            v-if="answer.options?.length"
            class="dialog-answer__options"
        >
            <span class="dialog-answer__label">{{ isClarification ? 'Уточните' : 'Что можно сделать' }}</span>
            <div class="dialog-answer__chips">
                <button
                    v-for="option in answer.options"
                    :key="option"
                    class="dialog-answer__option"
                    type="button"
                    @click="emit('choose-option', option)"
                >
                    {{ option }}
                    <ArrowRight
                        :size="14"
                        aria-hidden="true"
                    />
                </button>
            </div>
        </div>

        <div
            v-if="answer.nextSteps?.length"
            class="dialog-answer__next"
        >
            <span class="dialog-answer__label">Порядок действий</span>
            <ol class="dialog-answer__next-list">
                <li
                    v-for="(step, index) in answer.nextSteps"
                    :key="step"
                    class="dialog-answer__next-step"
                >
                    <span class="dialog-answer__next-number">{{ index + 1 }}</span>
                    {{ step }}
                </li>
            </ol>
        </div>

        <footer class="dialog-answer__footer">
            <div
                class="dialog-answer__feedback"
                role="group"
                aria-label="Оценка ответа"
            >
                <button
                    v-for="option in FEEDBACK_OPTIONS"
                    :key="option.value"
                    :class="[
                        'dialog-answer__feedback-button',
                        `dialog-answer__feedback-button--${option.value}`,
                        {'dialog-answer__feedback-button--active': feedback === option.value},
                    ]"
                    type="button"
                    :aria-pressed="feedback === option.value"
                    @click="emit('feedback', option.value)"
                >
                    <component
                        :is="option.icon"
                        :size="15"
                        aria-hidden="true"
                    />
                    {{ option.label }}
                </button>
            </div>
            <button
                class="dialog-answer__copy"
                type="button"
                @click="emit('copy')"
            >
                <Copy
                    :size="15"
                    aria-hidden="true"
                />
                Скопировать справку
            </button>
        </footer>

        <div
            v-if="answer.followUps?.length"
            class="dialog-answer__follow-ups"
        >
            <button
                v-for="followUp in answer.followUps"
                :key="followUp"
                class="dialog-answer__follow-up"
                type="button"
                @click="emit('ask', followUp)"
            >
                {{ followUp }}
            </button>
        </div>
    </article>
</template>

<style lang="scss">
.dialog-answer {
    $block: &;

    border-radius: $radius-3xl;
    box-shadow: $shadow-card;
    animation: fade-up $duration-slow $ease-out both;

    @include gradient-border;
    @include column($indent-step * 4);
    @include padding('y', 6);
    @include padding('x', 6);

    &--refusal {
        border: 1px solid $color-peach-line;
        background: linear-gradient(170deg, $color-peach-soft, $color-surface 55%);
    }

    &--clarification {
        border: 1px solid $color-line;
        background: linear-gradient(170deg, $color-amber, $color-surface 45%);
    }

    &__date-note {
        display: flex;
        align-items: flex-start;
        color: $color-amber-ink;
        border-radius: $radius-xl;
        background: $color-amber;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        line-height: 1.5;
        gap: $indent-step * 2.5;

        @include padding('y', 3);
        @include padding('x', 4);

        svg {
            flex-shrink: 0;
            margin-top: 1px;
        }
    }

    &__head {
        display: flex;
        align-items: center;
        gap: $indent-step * 2.5;
    }

    &__avatar {
        @include flex-center;

        width: 34px;
        height: 34px;
        color: $color-white;
        border-radius: $radius-lg;
        background: $gradient-brand;
    }

    &__author {
        font-size: $font-size-sm;
        font-weight: $font-weight-extrabold;
    }

    &__verdict {
        color: $color-ink-muted;
        font-size: $font-size-xs;
        font-weight: $font-weight-semibold;
    }

    &__text {
        @include column($indent-step * 3);
    }

    &__paragraph {
        margin: 0;
        color: $color-text-body;
        font-size: $font-size-lg;
        line-height: 1.7;
    }

    &__bold {
        color: $color-ink;
        font-weight: $font-weight-extrabold;
    }

    &__changed {
        color: $color-amber-ink;
        border-radius: $radius-xs;
        background: $color-amber;
        font-weight: $font-weight-bold;
        animation: change-flash 1.6s ease-out both;
        box-decoration-break: clone;

        @include padding('x', 1);

        &--bold {
            font-weight: $font-weight-extrabold;
        }
    }

    &__label {
        color: $color-ink-muted;
        font-size: $font-size-2xs;
        font-weight: $font-weight-extrabold;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    &__checked,
    &__options,
    &__next {
        @include column($indent-step * 2);
    }

    &__checked-list {
        display: flex;
        flex-wrap: wrap;
        margin: 0;
        padding: 0;
        list-style: none;
        gap: $indent-step * 2;
    }

    &__checked-item {
        @include pill($color-surface, $color-ink-soft);

        box-shadow: inset 0 0 0 1px $color-line;
    }

    &__chips {
        display: flex;
        flex-wrap: wrap;
        gap: $indent-step * 2;
    }

    &__option {
        @include button-reset;
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        transition:
            border-color $duration ease,
            background $duration ease;
        color: $color-navy;
        border: 1px solid $color-lavender-line;
        border-radius: $radius-lg;
        background: $color-surface;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        gap: $indent-step * 2;

        @include padding('y', 2);
        @include padding('x', 3.5);

        @include hover {
            background: $color-lavender-soft;
        }
    }

    &__next-list {
        display: flex;
        flex-wrap: wrap;
        margin: 0;
        padding: 0;
        list-style: none;
        gap: $indent-step * 2;
    }

    &__next-step {
        display: inline-flex;
        align-items: center;
        color: $color-ink;
        border-radius: $radius-lg;
        background: $color-surface-muted;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        gap: $indent-step * 2;

        @include padding('y', 1.5);
        @include padding('left', 1.5);
        @include padding('right', 3);
    }

    &__next-number {
        @include flex-center;

        width: 22px;
        height: 22px;
        color: $color-white;
        border-radius: $radius-sm;
        background: $gradient-user;
        font-size: $font-size-2xs;
        font-weight: $font-weight-extrabold;
    }

    &__footer {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        border-top: 1px solid $color-line-soft;
        gap: $indent-step * 3;

        @include padding('top', 4);
    }

    &__feedback {
        display: flex;
        flex-wrap: wrap;
        gap: $indent-step * 2;
    }

    &__feedback-button,
    &__copy {
        @include button-reset;
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        transition:
            background $duration ease,
            color $duration ease,
            border-color $duration ease;
        color: $color-ink-soft;
        border: 1px solid $color-line;
        border-radius: $radius-pill;
        background: $color-surface;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
        gap: $indent-step * 1.5;

        @include padding('y', 1.5);
        @include padding('x', 3);

        @include hover {
            color: $color-navy;
            border-color: $color-lavender-line;
        }
    }

    &__feedback-button--active {
        color: $color-white;
        border-color: transparent;
        background: $gradient-user;

        @include hover {
            color: $color-white;
        }
    }

    &__feedback-button--disputed {
        &#{$block}__feedback-button--active {
            background: linear-gradient(120deg, $color-orange, $color-orange-soft);
        }
    }

    &__follow-ups {
        display: flex;
        flex-wrap: wrap;
        gap: $indent-step * 2;
    }

    &__follow-up {
        @include button-reset;
        @include focus-ring;

        transition: background $duration ease;
        color: $color-violet;
        border-radius: $radius-pill;
        background: $color-lavender;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;

        @include padding('y', 2);
        @include padding('x', 3.5);

        @include hover {
            background: $color-lavender-line;
        }
    }

    @include mobile {
        border-radius: $radius-2xl;

        @include padding('y', 5);
        @include padding('x', 4);

        &__paragraph {
            font-size: $font-size-base;
        }
    }
}
</style>
