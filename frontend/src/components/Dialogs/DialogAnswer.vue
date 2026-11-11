<script setup>
import {computed} from 'vue';
import {
    ArrowRight,
    CalendarClock,
    Copy,
    FileDown,
    FilePlus2,
    FileSearch,
    Flag,
    MessageCircleQuestion,
    ThumbsDown,
    ThumbsUp,
} from 'lucide-vue-next';
import {ANSWER_STATUSES, FEEDBACK_VALUES} from '@/core/constants';
import {getPartOffsets} from '@/core/utils/answer';

import UiCiteBadge from '@/components/Ui/UiCiteBadge.vue';

const FEEDBACK_OPTIONS = Object.freeze([
    {value: FEEDBACK_VALUES.correct, label: 'Верно', icon: ThumbsUp},
    {value: FEEDBACK_VALUES.wrong, label: 'Ошибка', icon: ThumbsDown},
    {value: FEEDBACK_VALUES.disputed, label: 'Спорно, на проверку', icon: Flag},
]);

const props = defineProps({
    /** @type {import('vue').PropType<import('@/core/types/assistant').Answer>} */
    answer: {type: Object, required: true},
    revealedChars: {type: Number, default: Number.MAX_SAFE_INTEGER},
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
    'download',
]);

const isRefusal = computed(() => props.answer.status === ANSWER_STATUSES.refusal);
const isClarification = computed(() => props.answer.status === ANSWER_STATUSES.clarification);
const offsets = computed(() => getPartOffsets(props.answer.paragraphs));
const isTextComplete = computed(() => props.revealedChars >= offsets.value.total);
const cursorParagraph = computed(() => {
    const starts = offsets.value.starts.map((paragraph) => paragraph[0] ?? 0);

    return starts.findLastIndex((start) => start <= props.revealedChars);
});

/**
 * @param {number} paragraphIndex
 * @param {number} partIndex
 */
function getStart(paragraphIndex, partIndex) {
    return offsets.value.starts[paragraphIndex][partIndex];
}

/**
 * @param {number} paragraphIndex
 * @param {number} partIndex
 */
function isCiteRevealed(paragraphIndex, partIndex) {
    return getStart(paragraphIndex, partIndex) <= props.revealedChars;
}

/**
 * @param {import('@/core/types/assistant').AnswerPart} part
 * @param {number} paragraphIndex
 * @param {number} partIndex
 * @returns {string}
 */
function getVisibleText(part, paragraphIndex, partIndex) {
    const length = props.revealedChars - getStart(paragraphIndex, partIndex);

    return length > 0 ? part.text.slice(0, length) : '';
}

/** @param {number} paragraphIndex */
function isParagraphStarted(paragraphIndex) {
    return paragraphIndex <= cursorParagraph.value;
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
                <span
                    v-else
                    class="dialog-answer__seal"
                >
                    §
                </span>
            </span>
            <span class="dialog-answer__author">Юрассистент</span>
            <span class="dialog-answer__verdict">{{ answer.verdict }}</span>
        </div>

        <div
            class="dialog-answer__text"
            :aria-busy="!isTextComplete"
        >
            <template
                v-for="(paragraph, paragraphIndex) in answer.paragraphs"
                :key="paragraphIndex"
            >
                <p
                    v-if="isParagraphStarted(paragraphIndex)"
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
                        <template v-else-if="getVisibleText(part, paragraphIndex, partIndex)">
                            <mark
                                v-if="part.isChanged"
                                :class="['dialog-answer__changed', {'dialog-answer__changed--bold': part.isBold}]"
                                title="Зависит от даты события"
                            >
                                {{ getVisibleText(part, paragraphIndex, partIndex) }}
                            </mark>
                            <strong
                                v-else-if="part.isBold"
                                class="dialog-answer__bold"
                            >
                                {{ getVisibleText(part, paragraphIndex, partIndex) }}
                            </strong>
                            <template v-else>{{ getVisibleText(part, paragraphIndex, partIndex) }}</template>
                        </template>
                    </template>
                    <span
                        v-if="!isTextComplete && paragraphIndex === cursorParagraph"
                        class="dialog-answer__caret"
                        aria-hidden="true"
                    />
                </p>
            </template>
        </div>

        <div
            v-if="isTextComplete"
            class="dialog-answer__details"
        >

        <div
            v-if="answer.missingInfo?.length"
            class="dialog-answer__missing"
        >
            <span class="dialog-answer__label">Чего не хватает для ответа</span>
            <ul class="dialog-answer__missing-list">
                <li
                    v-for="item in answer.missingInfo"
                    :key="item"
                    class="dialog-answer__missing-item"
                >
                    <FilePlus2
                        :size="16"
                        aria-hidden="true"
                    />
                    {{ item }}
                </li>
            </ul>
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
            <div class="dialog-answer__exports">
            <button
                class="dialog-answer__copy"
                type="button"
                @click="emit('download')"
            >
                <FileDown
                    :size="15"
                    aria-hidden="true"
                />
                Справка в Word
            </button>
            <button
                class="dialog-answer__copy"
                type="button"
                @click="emit('copy')"
            >
                <Copy
                    :size="15"
                    aria-hidden="true"
                />
                Скопировать
            </button>
            </div>
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
        </div>
    </article>
</template>

<style lang="scss">
.dialog-answer {
    $block: &;

    border-radius: $radius-3xl;
    box-shadow: $shadow-card;
    animation: fade-up $duration-slow $ease-out both;

    @include accent-border;
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
        border-radius: $radius-sm;
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
        background-color: $color-navy;
    }

    &__seal {
        font-size: $font-size-lg;
        font-weight: $font-weight-extrabold;
        line-height: 1;
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

    &__details {
        animation: fade-up $duration-slow $ease-out both;

        @include column($indent-step * 4);
    }

    &__caret {
        display: inline-block;
        width: 2px;
        height: 1.1em;
        vertical-align: -0.15em;
        background-color: $color-violet;
        animation: caret-blink 0.9s steps(1) infinite;

        @include margin('left', 0.5);
    }

    &__exports {
        display: flex;
        flex-wrap: wrap;
        gap: $indent-step * 2;
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
        font-weight: $font-weight-bold;

        @include highlighter($color-highlighter-amber);
        @include highlighter-draw(0.2s);

        &--bold {
            font-weight: $font-weight-extrabold;
        }
    }

    &__label {
        color: $color-ink-muted;
        font-size: $font-size-2xs;
        font-weight: $font-weight-extrabold;
    }

    &__missing,
    &__checked,
    &__options,
    &__next {
        @include column($indent-step * 2);
    }

    &__missing-list {
        margin: 0;
        padding: 0;
        list-style: none;

        @include column($indent-step * 1.5);
    }

    &__missing-item {
        display: flex;
        align-items: center;
        color: $color-peach-deep;
        border: 1px dashed $color-peach-line;
        border-radius: $radius-lg;
        background-color: $color-surface;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        gap: $indent-step * 2;

        @include padding('y', 2);
        @include padding('x', 3);

        svg {
            flex-shrink: 0;
            color: $color-orange;
        }
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
        @include press;

        display: inline-flex;
        align-items: center;
        transition:
            border-color $duration ease,
            background $duration ease,
            transform $duration-fast $ease-out;
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
        background: $color-action;
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
        @include press;

        display: inline-flex;
        align-items: center;
        transition:
            background $duration ease,
            color $duration ease,
            border-color $duration ease,
            transform $duration-fast $ease-out;
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
        background: $color-action;

        svg {
            animation: cite-pop $duration-slow $ease-back-out;
        }

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
        @include press;

        transition:
            background $duration ease,
            transform $duration-fast $ease-out;
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
