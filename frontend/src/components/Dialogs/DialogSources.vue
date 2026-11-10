<script setup>
import {BookOpenCheck, ExternalLink} from 'lucide-vue-next';
import {ROUTE_NAMES} from '@/core/constants';
import {getQuoteSurroundings} from '@/core/utils/answer';

defineProps({
    /** @type {import('vue').PropType<import('@/core/types/assistant').Source[]>} */
    sources: {type: Array, required: true},
    activeCite: {type: Number, default: null},
    revealedCiteCount: {type: Number, default: 0},
    dialogId: {type: String, required: true},
});

const emit = defineEmits(['activate-cite', 'deactivate-cite']);

/**
 * @param {import('@/core/types/assistant').Source} source
 * @param {number} cite
 * @param {string} dialogId
 */
function getTarget(source, cite, dialogId) {
    return {
        name: ROUTE_NAMES.document,
        params: {documentId: source.documentId},
        query: {clause: source.clauseId, edition: source.editionId, dialog: dialogId, cite},
    };
}
</script>

<template>
    <aside class="dialog-sources">
        <h2 class="dialog-sources__title">
            <BookOpenCheck
                :size="18"
                aria-hidden="true"
            />
            Источники
            <span class="dialog-sources__count">{{ sources.length }}</span>
        </h2>

        <p
            v-if="!sources.length"
            class="dialog-sources__empty"
        >
            Вывод без источников не делается. В этом ответе ссылок нет — значит, в базе не нашлось подходящих пунктов.
        </p>

        <ol
            v-else
            class="dialog-sources__list"
        >
            <li
                v-for="(source, index) in sources"
                :key="`${source.documentId}-${source.clauseId}`"
                :class="[
                    'dialog-sources__card',
                    {
                        'dialog-sources__card--active': activeCite === index + 1,
                        'dialog-sources__card--muted': index >= revealedCiteCount,
                    },
                ]"
                :data-source-anchor="index + 1"
                @mouseenter="emit('activate-cite', index + 1)"
                @mouseleave="emit('deactivate-cite', index + 1)"
            >
                <div class="dialog-sources__head">
                    <span class="dialog-sources__number">{{ index + 1 }}</span>
                    <span class="dialog-sources__name">
                        {{ source.title }}
                        <span class="dialog-sources__meta">{{ source.meta }}</span>
                    </span>
                </div>
                <blockquote class="dialog-sources__quote">
                    <span>{{ getQuoteSurroundings(source).before }}</span>
                    <mark class="dialog-sources__mark">{{ source.quote }}</mark>
                    <span>{{ getQuoteSurroundings(source).after }}</span>
                </blockquote>
                <RouterLink
                    class="dialog-sources__link"
                    :to="getTarget(source, index + 1, dialogId)"
                >
                    Открыть пункт {{ source.clauseId }}
                    <ExternalLink
                        :size="13"
                        aria-hidden="true"
                    />
                </RouterLink>
            </li>
        </ol>
    </aside>
</template>

<style lang="scss">
.dialog-sources {
    @include column($indent-step * 3);

    &__title {
        display: flex;
        align-items: center;
        gap: $indent-step * 2;

        @include heading($font-size-lg);
    }

    &__count {
        @include pill;
    }

    &__empty {
        margin: 0;
        color: $color-ink-muted;
        border: 1px dashed $color-line-strong;
        border-radius: $radius-xl;
        font-size: $font-size-sm;
        line-height: 1.55;

        @include padding('y', 4);
        @include padding('x', 4);
    }

    &__list {
        margin: 0;
        padding: 0;
        list-style: none;

        @include column($indent-step * 3);
    }

    &__card {
        transition:
            opacity $duration ease,
            transform $duration $ease-out,
            box-shadow $duration ease,
            border-color $duration ease;

        @include card($radius-xl);
        @include column($indent-step * 2.5);
        @include padding('y', 4);
        @include padding('x', 4);

        &--active {
            transform: translateX(-4px);
            box-shadow: $shadow-raised;

            @include accent-border;

            border-color: $color-navy;
        }

        &--muted {
            opacity: 0.45;
        }
    }

    &__head {
        display: flex;
        align-items: flex-start;
        gap: $indent-step * 2.5;
    }

    &__number {
        @include flex-center;

        flex-shrink: 0;
        width: 24px;
        height: 24px;
        color: $color-violet;
        border-radius: $radius-pill;
        background: $color-lavender;
        font-size: $font-size-2xs;
        font-weight: $font-weight-extrabold;
    }

    &__name {
        font-size: $font-size-sm;
        font-weight: $font-weight-extrabold;

        @include column($indent-step * 0.5);
    }

    &__meta {
        color: $color-ink-muted;
        font-size: $font-size-xs;
        font-weight: $font-weight-medium;
    }

    &__quote {
        margin: 0;
        color: $color-ink-soft;
        font-family: $font-document;
        font-size: $font-size-base;
        line-height: 1.65;
        quotes: '«' '»';

        &::before {
            content: open-quote;
        }

        &::after {
            content: close-quote;
        }
    }

    &__mark {
        color: $color-ink;

        @include highlighter;
        @include highlighter-draw(0.15s);
    }

    &__link {
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        align-self: flex-start;
        color: $color-violet;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
        text-decoration: none;
        gap: $indent-step * 1.5;

        @include hover {
            text-decoration: underline;
        }
    }
}
</style>
