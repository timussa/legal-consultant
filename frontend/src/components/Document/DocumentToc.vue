<script setup>
defineProps({
    /** @type {import('vue').PropType<{id: string, title: string}[]>} */
    outline: {type: Array, required: true},
    /** @type {import('vue').PropType<string[]>} */
    availableSectionIds: {type: Array, required: true},
    /** @type {import('vue').PropType<string[]>} */
    changedSectionIds: {type: Array, default: () => []},
    /** @type {import('vue').PropType<string[]>} */
    citedSectionIds: {type: Array, default: () => []},
    activeSectionId: {type: String, default: null},
});

const emit = defineEmits(['select']);
</script>

<template>
    <nav
        class="document-toc"
        aria-label="Содержание документа"
    >
        <h2 class="document-toc__title">Содержание</h2>
        <ol class="document-toc__list">
            <li
                v-for="item in outline"
                :key="item.id"
            >
                <button
                    :class="[
                        'document-toc__item',
                        {
                            'document-toc__item--active': item.id === activeSectionId,
                            'document-toc__item--unavailable': !availableSectionIds.includes(item.id),
                        },
                    ]"
                    type="button"
                    :disabled="!availableSectionIds.includes(item.id)"
                    @click="emit('select', item.id)"
                >
                    <span class="document-toc__name">{{ item.title }}</span>
                    <span class="document-toc__dots">
                        <span
                            v-if="changedSectionIds.includes(item.id)"
                            class="document-toc__dot document-toc__dot--changed"
                            title="Есть изменения в выбранной редакции"
                        />
                        <span
                            v-if="citedSectionIds.includes(item.id)"
                            class="document-toc__dot document-toc__dot--cited"
                            title="Цитируется в ответах"
                        />
                    </span>
                </button>
            </li>
        </ol>
        <ul class="document-toc__legend">
            <li class="document-toc__legend-item">
                <span class="document-toc__dot document-toc__dot--changed" />
                изменён в редакции
            </li>
            <li class="document-toc__legend-item">
                <span class="document-toc__dot document-toc__dot--cited" />
                цитируется в ответах
            </li>
        </ul>
    </nav>
</template>

<style lang="scss">
.document-toc {
    @include card($radius-2xl);
    @include column($indent-step * 3);
    @include padding('y', 4);
    @include padding('x', 3);

    &__title {
        @include heading($font-size-md);
        @include padding('x', 2);
    }

    &__list {
        margin: 0;
        padding: 0;
        list-style: none;

        @include column($indent-step * 0.5);
    }

    &__item {
        @include button-reset;
        @include focus-ring;

        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        transition:
            background $duration ease,
            color $duration ease;
        color: $color-ink-soft;
        border-radius: $radius-md;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        text-align: left;
        gap: $indent-step * 2;

        @include padding('y', 2);
        @include padding('x', 2);

        &:not(:disabled) {
            @include hover {
                color: $color-navy;
                background: $color-surface-muted;
            }
        }

        &--active {
            color: $color-navy;
            background: $color-selected;
            font-weight: $font-weight-bold;
        }

        &--unavailable {
            color: $color-ink-faint;
            cursor: default;
        }
    }

    &__dots {
        display: flex;
        flex-shrink: 0;
        gap: $indent-step;
    }

    &__dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: $radius-pill;

        &--changed {
            background: $color-orange;
        }

        &--cited {
            background: $color-violet-bright;
        }
    }

    &__legend {
        margin: 0;
        padding: 0;
        border-top: 1px solid $color-line-soft;
        list-style: none;

        @include column($indent-step * 1.5);
        @include padding('top', 3);
        @include padding('x', 2);
    }

    &__legend-item {
        display: flex;
        align-items: center;
        color: $color-ink-muted;
        font-size: $font-size-xs;
        gap: $indent-step * 2;
    }
}
</style>
