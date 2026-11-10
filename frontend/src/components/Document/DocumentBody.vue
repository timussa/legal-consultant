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
                        {{ clause.diff.prefix }}
                        <del class="document-body__removed">{{ clause.diff.removed }}</del>
                        <ins class="document-body__added">{{ clause.diff.added }}</ins>
                        {{ clause.diff.suffix }}
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
                        {{ clause.text }}
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

    position: relative;
    box-shadow: $shadow-card;

    @include card($radius-2xl);
    @include column($indent-step * 8);
    @include padding('y', 8);
    @include padding('x', 9);

    &__section {
        scroll-margin-top: $header-height + $indent-step * 6;

        @include column($indent-step * 3);
    }

    &__section-title {
        @include heading($font-size-xl);
    }

    &__clause {
        display: flex;
        align-items: flex-start;
        transition: background $duration ease;
        border-radius: $radius-xl;
        scroll-margin-top: $header-height + $indent-step * 10;
        gap: $indent-step * 4;

        @include padding('y', 3);
        @include padding('x', 3);
        @include margin('x', -3);

        &--changed {
            background: $color-peach-soft;
        }

        &--highlighted {
            background: $gradient-selected;
            animation: clause-pulse 1.4s ease-out 2;

            #{$block}__clause-number {
                color: $color-white;
                background: $gradient-user;
            }
        }
    }

    &__clause-number {
        @include flex-center;

        flex-shrink: 0;
        min-width: 40px;
        height: 28px;
        color: $color-navy;
        border-radius: $radius-md;
        background: $color-navy-tint;
        font-size: $font-size-xs;
        font-weight: $font-weight-extrabold;
    }

    &__clause-body {
        flex: 1;
        min-width: 0;

        @include column($indent-step * 2);
    }

    &__text {
        margin: 0;
        color: $color-text-body;
        font-size: $font-size-base;
        line-height: 1.75;
    }

    &__removed {
        color: $color-peach-ink;
        border-radius: $radius-xs;
        background: $color-peach;
        text-decoration-thickness: 2px;

        @include padding('x', 0.5);
    }

    &__added {
        color: $color-amber-ink;
        border-radius: $radius-xs;
        background: $color-amber;
        font-weight: $font-weight-bold;
        text-decoration: none;
        animation: change-flash 1.6s ease-out both;

        @include margin('left', 1);
        @include padding('x', 0.5);
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
        background: $gradient-user;
        box-shadow: $shadow-raised;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        white-space: nowrap;
        gap: $indent-step * 2;

        @include padding('y', 2);
        @include padding('x', 3.5);
    }

    @include tablet {
        @include padding('y', 6);
        @include padding('x', 5);
    }

    @include mobile {
        @include padding('y', 5);
        @include padding('x', 4);

        &__clause {
            flex-direction: column;
            gap: $indent-step * 2;
        }
    }
}
</style>
