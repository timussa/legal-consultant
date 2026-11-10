<script setup>
import {Quote} from 'lucide-vue-next';
import {ROUTE_NAMES} from '@/core/constants';

defineProps({
    /** @type {import('vue').PropType<import('@/core/types/document').LegalDocument>} */
    document: {type: Object, required: true},
});

const emit = defineEmits(['select-clause']);
</script>

<template>
    <aside class="document-aside">
        <section class="document-aside__block">
            <h2 class="document-aside__title">Цитируется в ответах</h2>
            <p
                v-if="!document.citations.length"
                class="document-aside__empty"
            >
                Пока ни один ответ не ссылается на этот документ.
            </p>
            <ul
                v-else
                class="document-aside__list"
            >
                <li
                    v-for="citation in document.citations"
                    :key="`${citation.dialogId}-${citation.clauseId}`"
                >
                    <RouterLink
                        class="document-aside__citation"
                        :to="{name: ROUTE_NAMES.dialogs, params: {dialogId: citation.dialogId}}"
                    >
                        <Quote
                            :size="14"
                            aria-hidden="true"
                        />
                        <span>
                            <span class="document-aside__citation-title">
                                {{ citation.dialogNumber }} · {{ citation.dialogTitle }}
                            </span>
                            <span class="document-aside__citation-meta">
                                п. {{ citation.clauseId }} · сноска {{ citation.cite }}
                            </span>
                        </span>
                    </RouterLink>
                </li>
            </ul>
        </section>

        <section class="document-aside__block">
            <h2 class="document-aside__title">Комментарии юристов</h2>
            <ul class="document-aside__list">
                <li
                    v-for="comment in document.comments"
                    :key="comment.id"
                    class="document-aside__comment"
                >
                    <div class="document-aside__comment-head">
                        <span class="document-aside__avatar">{{ comment.initials }}</span>
                        <span class="document-aside__comment-author">
                            {{ comment.author }}
                            <span class="document-aside__comment-date">{{ comment.dateLabel }}</span>
                        </span>
                    </div>
                    <p class="document-aside__comment-text">{{ comment.text }}</p>
                    <button
                        class="document-aside__clause"
                        type="button"
                        @click="emit('select-clause', comment.clauseId)"
                    >
                        к пункту {{ comment.clauseId }}
                    </button>
                </li>
            </ul>
        </section>
    </aside>
</template>

<style lang="scss">
.document-aside {
    @include column($indent-step * 4);

    &__block {
        @include card($radius-2xl);
        @include column($indent-step * 3);
        @include padding('y', 4);
        @include padding('x', 4);
    }

    &__title {
        @include heading($font-size-md);
    }

    &__empty {
        margin: 0;
        color: $color-ink-muted;
        font-size: $font-size-sm;
    }

    &__list {
        margin: 0;
        padding: 0;
        list-style: none;

        @include column($indent-step * 3);
    }

    &__citation {
        @include focus-ring;

        display: flex;
        align-items: flex-start;
        transition: background $duration ease;
        color: $color-violet;
        border-radius: $radius-lg;
        text-decoration: none;
        gap: $indent-step * 2;

        @include padding('y', 2);
        @include padding('x', 2);
        @include margin('x', -2);

        @include hover {
            background: $color-lavender-soft;
        }

        svg {
            flex-shrink: 0;
            margin-top: 2px;
        }
    }

    &__citation-title {
        display: block;
        color: $color-ink;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__citation-meta {
        color: $color-ink-muted;
        font-size: $font-size-xs;
    }

    &__comment {
        @include column($indent-step * 2);
    }

    &__comment-head {
        display: flex;
        align-items: center;
        gap: $indent-step * 2;
    }

    &__avatar {
        @include flex-center;

        flex-shrink: 0;
        width: 30px;
        height: 30px;
        color: $color-navy;
        border-radius: $radius-pill;
        background: $color-navy-tint;
        font-size: $font-size-2xs;
        font-weight: $font-weight-extrabold;
    }

    &__comment-author {
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;

        @include column(0);
    }

    &__comment-date {
        color: $color-ink-faint;
        font-size: $font-size-2xs;
        font-weight: $font-weight-semibold;
    }

    &__comment-text {
        margin: 0;
        color: $color-ink-soft;
        border-radius: $radius-lg;
        background: $color-surface-soft;
        font-size: $font-size-sm;
        line-height: 1.55;

        @include padding('y', 2.5);
        @include padding('x', 3);
    }

    &__clause {
        @include button-reset;
        @include focus-ring;

        align-self: flex-start;
        color: $color-violet;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;

        @include hover {
            text-decoration: underline;
        }
    }
}
</style>
