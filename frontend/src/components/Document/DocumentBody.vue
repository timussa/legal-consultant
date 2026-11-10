<script setup>
import {computed, ref} from 'vue';
import {MessageSquareQuote, MessagesSquare, Quote} from 'lucide-vue-next';
import {useTextSelection} from '@/core/composables/useTextSelection';
import {ROUTE_NAMES} from '@/core/constants';
import {diffText, getPreviousEditionId} from '@/core/utils/document';

const props = defineProps({
    /** @type {import('vue').PropType<import('@/core/types/document').LegalDocument>} */
    document: {type: Object, required: true},
    editionId: {type: String, required: true},
    isCompare: {type: Boolean, default: false},
    /** @type {import('vue').PropType<{clauseId: string, sectionId: string, isAdded: boolean}[]>} */
    changedClauses: {type: Array, default: () => []},
    highlightedClauseId: {type: String, default: null},
});

const emit = defineEmits(['ask-fragment']);

const root = ref(null);

const {selection, clear} = useTextSelection(root);

const previousEditionId = computed(() => getPreviousEditionId(props.document, props.editionId));
const sections = computed(() =>
    props.document.sections
        .map((section) => ({
            ...section,
            clauses: section.clauses
                .filter((clause) => clause.versions[props.editionId] !== undefined)
                .map((clause) => buildClause(clause)),
        }))
        .filter((section) => section.clauses.length),
);

/** @param {import('@/core/types/document').Clause} clause */
function buildClause(clause) {
    const text = clause.versions[props.editionId];
    const change = props.changedClauses.find((item) => item.clauseId === clause.id);
    const previousText = previousEditionId.value ? clause.versions[previousEditionId.value] : undefined;

    return {
        id: clause.id,
        text,
        change,
        diff: change && !change.isAdded && previousText ? diffText(previousText, text) : null,
        citations: props.document.citations.filter((citation) => citation.clauseId === clause.id),
        commentCount: props.document.comments.filter((comment) => comment.clauseId === clause.id).length,
    };
}

function handleAskFragment() {
    if (!selection.value) {
        return;
    }

    emit('ask-fragment', {text: selection.value.text, clauseId: selection.value.clauseId});
    window.getSelection()?.removeAllRanges();
    clear();
}
</script>

<template>
    <div
        ref="root"
        class="document-body"
    >
        <section
            v-for="section in sections"
            :id="`section-${section.id}`"
            :key="section.id"
            class="document-body__section"
            :data-section-id="section.id"
        >
            <h2 class="document-body__section-title">{{ section.title }}</h2>

            <div
                v-for="clause in section.clauses"
                :id="`clause-${clause.id}`"
                :key="clause.id"
                :class="[
                    'document-body__clause',
                    {
                        'document-body__clause--highlighted': clause.id === highlightedClauseId,
                        'document-body__clause--changed': clause.change,
                    },
                ]"
                :data-clause-id="clause.id"
            >
                <span class="document-body__clause-number">{{ clause.id }}</span>
                <div class="document-body__clause-body">
                    <p
                        v-if="isCompare && clause.diff"
                        class="document-body__text"
                    >
                        <span>{{ clause.diff.prefix }}</span>
                        <del class="document-body__removed">{{ clause.diff.removed }}</del>
                        <span>&#32;</span>
                        <ins class="document-body__added">{{ clause.diff.added }}</ins>
                        <span>{{ clause.diff.suffix }}</span>
                    </p>
                    <p
                        v-else-if="isCompare && clause.change?.isAdded"
                        class="document-body__text"
                    >
                        <ins class="document-body__added">{{ clause.text }}</ins>
                    </p>
                    <p
                        v-else
                        class="document-body__text"
                    >
                        <span :class="{'document-body__highlight': clause.id === highlightedClauseId}">
                            {{ clause.text }}
                        </span>
                    </p>

                    <div
                        v-if="clause.change || clause.citations.length || clause.commentCount"
                        class="document-body__marks"
                    >
                        <span
                            v-if="clause.change"
                            class="document-body__mark document-body__mark--changed"
                        >
                            {{ clause.change.isAdded ? 'новый пункт' : 'изменён в этой редакции' }}
                        </span>
                        <RouterLink
                            v-for="citation in clause.citations"
                            :key="`${citation.dialogId}-${citation.cite}`"
                            class="document-body__mark document-body__mark--cited"
                            :to="{name: ROUTE_NAMES.dialogs, params: {dialogId: citation.dialogId}}"
                        >
                            <Quote
                                :size="12"
                                aria-hidden="true"
                            />
                            {{ citation.dialogNumber }} · сноска {{ citation.cite }}
                        </RouterLink>
                        <span
                            v-if="clause.commentCount"
                            class="document-body__mark"
                        >
                            <MessagesSquare
                                :size="12"
                                aria-hidden="true"
                            />
                            {{ clause.commentCount }}
                        </span>
                    </div>
                </div>
            </div>
        </section>

        <button
            v-if="selection"
            class="document-body__ask"
            type="button"
            :style="{'--selection-x': `${selection.x}px`, '--selection-y': `${selection.y}px`}"
            @mousedown.prevent
            @click="handleAskFragment"
        >
            <MessageSquareQuote
                :size="16"
                aria-hidden="true"
            />
            Спросить по фрагменту
        </button>
    </div>
</template>

<style lang="scss">
.document-body {
    $block: &;
    $gutter: $indent-step * 16;

    position: relative;
    border: 1px solid $color-line;
    border-radius: $radius-md;
    background-color: $color-paper;
    box-shadow:
        0 1px 2px rgba($color-ink, 6%),
        0 24px 48px -32px rgba($color-ink, 35%);

    @include column($indent-step * 10);
    @include padding('y', 14);
    @include padding('right', 16);
    @include padding('left', 16);

    &__section {
        scroll-margin-top: $header-height + $indent-step * 22;

        @include column($indent-step * 4);
    }

    &__section-title {
        margin: 0;
        color: $color-ink;
        font-family: $font-document;
        font-size: $font-size-xl;
        font-weight: $font-weight-bold;
        text-align: center;
    }

    &__clause {
        position: relative;
        scroll-margin-top: $header-height + $indent-step * 26;
        padding-left: $gutter;
    }

    &__clause-number {
        position: absolute;
        top: 0;
        left: 0;
        width: $gutter - $indent-step * 4;
        transition: color $duration ease;
        color: $color-ink-muted;
        font-family: $font-document;
        font-size: $font-size-lg;
        line-height: 1.75;
        text-align: right;
    }

    &__clause--changed &__clause-number {
        color: $color-orange;
    }

    &__clause--highlighted &__clause-number {
        color: $color-navy;
        font-weight: $font-weight-bold;
    }

    &__clause-body {
        min-width: 0;

        @include column($indent-step * 2);
    }

    &__text {
        margin: 0;
        color: $color-text-body;
        font-family: $font-document;
        font-size: $font-size-lg;
        line-height: 1.75;
        hyphens: auto;
    }

    &__highlight {
        @include highlighter($color-highlighter-amber);
        @include highlighter-draw(0.3s);
    }

    &__removed {
        color: $color-peach-ink;
        text-decoration-color: rgba($color-peach-ink, 70%);
        text-decoration-thickness: 1.5px;
    }

    &__added {
        color: $color-ink;
        text-decoration: none;

        @include highlighter($color-highlighter-amber);
        @include highlighter-draw;
    }

    &__marks {
        display: flex;
        flex-wrap: wrap;
        gap: $indent-step * 1.5;
    }

    &__mark {
        @include pill($color-surface-muted, $color-ink-muted);

        font-size: $font-size-2xs;
        text-decoration: none;

        &--changed {
            color: $color-peach-ink;
            background: $color-peach;
        }

        &--cited {
            color: $color-violet;
            background: $color-lavender;

            @include focus-ring;
            @include hover {
                background: $color-lavender-line;
            }
        }
    }

    &__ask {
        @include button-reset;
        @include focus-ring;

        position: absolute;
        z-index: $ui-index-overlay;
        top: var(--selection-y);
        left: var(--selection-x);
        display: inline-flex;
        align-items: center;
        transform: translate(-50%, calc(-100% - #{$indent-step * 2}));
        color: $color-white;
        border-radius: $radius-pill;
        background: $color-action;
        box-shadow: $shadow-raised;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        white-space: nowrap;
        gap: $indent-step * 2;

        @include padding('y', 2);
        @include padding('x', 3.5);
    }

    @include tablet {
        @include padding('y', 10);
        @include padding('right', 8);
        @include padding('left', 6);
    }

    @include mobile {
        @include padding('y', 6);
        @include padding('x', 4);

        &__clause {
            padding-left: 0;
        }

        &__clause-number {
            position: static;
            display: block;
            width: auto;
            text-align: left;
        }
    }
}
</style>
