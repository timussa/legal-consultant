<script setup>
import {computed, nextTick, ref, watch} from 'vue';
import {ArrowLeft, CornerDownRight} from 'lucide-vue-next';
import {useRoute, useRouter} from 'vue-router';
import {getDocument} from '@/core/api/documents';
import {useRequest} from '@/core/composables/useRequest';
import {ROUTE_NAMES} from '@/core/constants';
import {getChangedClauses, getPreviousEditionId} from '@/core/utils/document';

import DocumentAside from '@/components/Document/DocumentAside.vue';
import DocumentBand from '@/components/Document/DocumentBand.vue';
import DocumentBody from '@/components/Document/DocumentBody.vue';
import DocumentToc from '@/components/Document/DocumentToc.vue';
import UiState from '@/components/Ui/UiState.vue';

const route = useRoute();
const router = useRouter();

const editionId = ref('');
const isCompare = ref(false);
const activeSectionId = ref(null);
const highlightedClauseId = ref(null);

const documentId = computed(() => String(route.params.documentId ?? ''));
const fromDialogId = computed(() => (typeof route.query.dialog === 'string' ? route.query.dialog : null));
const fromCite = computed(() => (typeof route.query.cite === 'string' ? route.query.cite : null));

const {data: document, isLoading, error, reload} = useRequest(getDocument, documentId);

const changedClauses = computed(() => (document.value ? getChangedClauses(document.value, editionId.value) : []));
const changedSectionIds = computed(() => [...new Set(changedClauses.value.map((item) => item.sectionId))]);
const availableSectionIds = computed(() => document.value?.sections.map((section) => section.id) ?? []);
const citedSectionIds = computed(() => {
    const clauseIds = new Set(document.value?.citations.map((citation) => citation.clauseId) ?? []);

    return (document.value?.sections ?? [])
        .filter((section) => section.clauses.some((clause) => clauseIds.has(clause.id)))
        .map((section) => section.id);
});
const canCompare = computed(() => Boolean(document.value && getPreviousEditionId(document.value, editionId.value)));
const fromNote = computed(() => {
    const cite = fromCite.value ? ` · сноска ${fromCite.value}` : '';
    const clause = highlightedClauseId.value ? ` — пункт ${highlightedClauseId.value} подсвечен` : '';

    return `${cite}${clause}`;
});
const notFoundError = computed(() =>
    !isLoading.value && !error.value && !document.value ? 'Документ не найден' : null,
);

watch(canCompare, (value) => {
    if (!value) {
        isCompare.value = false;
    }
});

watch(document, async (loaded) => {
    if (!loaded) {
        return;
    }

    const requestedEdition = loaded.editions.find((edition) => edition.id === route.query.edition);

    editionId.value = requestedEdition?.id ?? loaded.editions.at(-1).id;
    highlightedClauseId.value = typeof route.query.clause === 'string' ? route.query.clause : null;
    activeSectionId.value = loaded.sections[0]?.id ?? null;

    await nextTick();

    if (highlightedClauseId.value) {
        scrollToClause(highlightedClauseId.value);
    }
});

/** @param {string} clauseId */
function scrollToClause(clauseId) {
    const element = window.document.getElementById(`clause-${clauseId}`);

    element?.scrollIntoView({behavior: 'smooth', block: 'center'});
    activeSectionId.value = element?.closest('[data-section-id]')?.getAttribute('data-section-id') ?? null;
}

/** @param {string} sectionId */
function handleSelectSection(sectionId) {
    activeSectionId.value = sectionId;
    window.document.getElementById(`section-${sectionId}`)?.scrollIntoView({behavior: 'smooth', block: 'start'});
}

/** @param {string} clauseId */
function handleSelectClause(clauseId) {
    highlightedClauseId.value = null;

    nextTick(() => {
        highlightedClauseId.value = clauseId;
        scrollToClause(clauseId);
    });
}

/** @param {{text: string, clauseId: string | null}} fragment */
function handleAskFragment(fragment) {
    const place = fragment.clauseId ? `, п. ${fragment.clauseId}` : '';
    const question = `Что означает в документе «${document.value.title}»${place}: «${fragment.text}»?`;

    router.push({name: ROUTE_NAMES.dialogs, query: {question}});
}
</script>

<template>
    <div class="document-page">
        <UiState
            v-if="!document"
            :is-loading="isLoading"
            :error="error ?? notFoundError"
            loading-text="Открываем документ…"
            @retry="reload"
        />

        <template v-else>
            <div
                v-if="fromDialogId"
                class="document-page__from"
            >
                <CornerDownRight
                    :size="18"
                    aria-hidden="true"
                />
                <span>
                    Вы перешли из ответа
                    <strong>№{{ fromDialogId }}</strong>
                    {{ fromNote }}
                </span>
                <RouterLink
                    class="document-page__back"
                    :to="{name: ROUTE_NAMES.dialogs, params: {dialogId: fromDialogId}}"
                >
                    <ArrowLeft
                        :size="15"
                        aria-hidden="true"
                    />
                    Вернуться к ответу
                </RouterLink>
            </div>

            <DocumentBand
                v-model:edition-id="editionId"
                v-model:is-compare="isCompare"
                :document="document"
                :changed-count="changedClauses.length"
                :can-compare="canCompare"
            />

            <div class="document-page__grid">
                <DocumentToc
                    class="document-page__toc"
                    :outline="document.outline"
                    :available-section-ids="availableSectionIds"
                    :changed-section-ids="changedSectionIds"
                    :cited-section-ids="citedSectionIds"
                    :active-section-id="activeSectionId"
                    @select="handleSelectSection"
                />
                <DocumentBody
                    :document="document"
                    :edition-id="editionId"
                    :is-compare="isCompare"
                    :changed-clauses="changedClauses"
                    :highlighted-clause-id="highlightedClauseId"
                    @ask-fragment="handleAskFragment"
                />
                <DocumentAside
                    class="document-page__aside"
                    :document="document"
                    @select-clause="handleSelectClause"
                />
            </div>
            <p class="document-page__hint">Выделите текст пункта, чтобы задать вопрос именно по этому фрагменту.</p>
        </template>
    </div>
</template>

<style lang="scss">
.document-page {
    max-width: 1440px;
    margin: 0 auto;

    @include column($indent-step * 5);

    &__from {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        color: $color-violet;
        border: 1px solid $color-lavender-line;
        border-radius: $radius-xl;
        background: $color-lavender-soft;
        font-size: $font-size-sm;
        gap: $indent-step * 2.5;
        animation: fade-up $duration-slow $ease-out both;

        @include padding('y', 3);
        @include padding('x', 4);

        strong {
            font-weight: $font-weight-extrabold;
        }
    }

    &__back {
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        margin-left: auto;
        color: $color-navy;
        font-weight: $font-weight-bold;
        text-decoration: none;
        gap: $indent-step * 1.5;

        @include hover {
            text-decoration: underline;
        }
    }

    &__grid {
        display: grid;
        align-items: start;
        grid-template-columns: 240px minmax(0, 1fr) 300px;
        gap: $indent-step * 5;
    }

    &__toc,
    &__aside {
        position: sticky;
        top: $header-height + $indent-step * 6;
    }

    &__hint {
        margin: 0;
        color: $color-ink-faint;
        font-size: $font-size-xs;
        text-align: center;
    }

    @include laptop {
        &__grid {
            grid-template-columns: 220px minmax(0, 1fr);
        }

        &__aside {
            position: static;
            grid-column: 1 / -1;
        }
    }

    @include tablet {
        &__grid {
            grid-template-columns: 1fr;
        }

        &__toc {
            position: static;
        }
    }
}
</style>
