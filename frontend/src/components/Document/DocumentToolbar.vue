<script setup>
import {computed, ref, watch} from 'vue';
import {ChevronDown, ChevronUp, GitCompareArrows, TriangleAlert} from 'lucide-vue-next';

import UiSegmented from '@/components/Ui/UiSegmented.vue';

const props = defineProps({
    /** @type {import('vue').PropType<import('@/core/types/document').LegalDocument>} */
    document: {type: Object, required: true},
    /** @type {import('vue').PropType<{clauseId: string, sectionId: string, isAdded: boolean}[]>} */
    changedClauses: {type: Array, default: () => []},
    canCompare: {type: Boolean, default: false},
});

const emit = defineEmits(['go-to-change']);

const editionId = defineModel('editionId', {type: String, required: true});
const isCompare = defineModel('isCompare', {type: Boolean, default: false});

const changeIndex = ref(0);

const editionOptions = computed(() =>
    props.document.editions.map((edition) => ({value: edition.id, label: edition.label, hint: edition.date})),
);
const edition = computed(() => props.document.editions.find((item) => item.id === editionId.value));
const changeCount = computed(() => props.changedClauses.length);
const isNavigationVisible = computed(() => isCompare.value && changeCount.value > 0);
const compareTitle = computed(() =>
    props.canCompare ? 'Показать, что изменилось относительно прошлой редакции' : 'Это первая редакция, сравнивать не с чем',
);

watch(editionId, () => {
    changeIndex.value = 0;
});

/** @param {number} index */
function goToChange(index) {
    changeIndex.value = (index + changeCount.value) % changeCount.value;
    emit('go-to-change', props.changedClauses[changeIndex.value].clauseId);
}

function handleCompareClick() {
    const isEnabled = !isCompare.value;

    isCompare.value = isEnabled;

    if (isEnabled && changeCount.value) {
        goToChange(0);
    }
}
</script>

<template>
    <div class="document-toolbar">
        <div class="document-toolbar__group">
            <UiSegmented
                v-model="editionId"
                :options="editionOptions"
                label="Редакция документа"
            />
            <span
                v-if="edition?.note"
                class="document-toolbar__note"
            >
                <TriangleAlert
                    :size="14"
                    aria-hidden="true"
                />
                {{ edition.note }}
            </span>
        </div>

        <div class="document-toolbar__group">
            <button
                :class="['document-toolbar__compare', {'document-toolbar__compare--active': isCompare}]"
                type="button"
                :disabled="!canCompare"
                :title="compareTitle"
                :aria-pressed="isCompare"
                @click="handleCompareClick"
            >
                <GitCompareArrows
                    :size="16"
                    aria-hidden="true"
                />
                Было / стало
                <span
                    v-if="canCompare && changeCount"
                    class="document-toolbar__count"
                >
                    {{ changeCount }}
                </span>
            </button>

            <div
                v-if="isNavigationVisible"
                class="document-toolbar__navigation"
            >
                <span class="document-toolbar__position">{{ changeIndex + 1 }} из {{ changeCount }}</span>
                <button
                    class="document-toolbar__arrow"
                    type="button"
                    aria-label="Предыдущее изменение"
                    @click="goToChange(changeIndex - 1)"
                >
                    <ChevronUp
                        :size="18"
                        aria-hidden="true"
                    />
                </button>
                <button
                    class="document-toolbar__arrow"
                    type="button"
                    aria-label="Следующее изменение"
                    @click="goToChange(changeIndex + 1)"
                >
                    <ChevronDown
                        :size="18"
                        aria-hidden="true"
                    />
                </button>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
.document-toolbar {
    position: sticky;
    z-index: $ui-index-overlay;
    top: $header-height + $indent-step * 3;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    color: $color-ink;
    border: 1px solid $color-lavender-line;
    border-radius: $radius-2xl;
    background-color: rgba($color-lavender-soft, 94%);
    box-shadow: $shadow-card;
    backdrop-filter: blur(12px);
    gap: $indent-step * 3;

    @include padding('y', 2);
    @include padding('x', 2);

    &__group {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        min-width: 0;
        max-width: 100%;
        gap: $indent-step * 2;
    }

    &__note {
        @include pill($color-amber, $color-amber-ink);
    }

    &__compare {
        @include button-reset;
        @include press;
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        transition:
            color $duration ease,
            border-color $duration ease,
            background-color $duration ease,
            transform $duration-fast $ease-out;
        color: $color-navy;
        border: 1px solid $color-lavender-line;
        border-radius: $radius-pill;
        background-color: $color-surface;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        gap: $indent-step * 2;

        @include padding('y', 2);
        @include padding('x', 3.5);

        &:not(:disabled) {
            @include hover {
                border-color: $color-peach-line;
            }
        }

        &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        &--active {
            color: $color-peach-ink;
            border-color: $color-peach-line;
            background-color: $color-peach;
        }
    }

    &__count {
        @include pill($color-orange, $color-white);

        font-size: $font-size-2xs;

        @include padding('y', 0);
        @include padding('x', 1.5);
    }

    &__navigation {
        display: flex;
        align-items: center;
        gap: $indent-step;
    }

    &__position {
        color: $color-ink-soft;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        white-space: nowrap;

        @include padding('right', 1);
    }

    &__arrow {
        @include button-reset;
        @include flex-center;
        @include focus-ring;
        @include press;

        width: 34px;
        height: 34px;
        transition:
            background-color $duration ease,
            transform $duration-fast $ease-out;
        color: $color-navy;
        border: 1px solid $color-lavender-line;
        border-radius: $radius-md;
        background-color: $color-surface;

        @include hover {
            background-color: $color-lavender;
        }
    }

    @include mobile {
        top: $header-height + $indent-step * 2;

        &__note {
            display: none;
        }
    }
}
</style>
