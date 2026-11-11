<script setup>
import {computed, nextTick, ref, watch} from 'vue';
import {CornerDownLeft, FileText, MessageSquareText, Search, Sparkles} from 'lucide-vue-next';
import {storeToRefs} from 'pinia';
import {useRouter} from 'vue-router';
import {useSearch} from '@/core/composables/useSearch';
import {ROUTE_NAMES} from '@/core/constants';
import {DOCUMENTS} from '@/core/data/documents';
import {useDialogsStore} from '@/core/stores/dialogs';
import {normalize, splitByMatch} from '@/core/utils/search';

import UiSkeleton from '@/components/Ui/UiSkeleton.vue';

const RECENT_LIMIT = 4;
const DIALOG_LIMIT = 4;

const isOpen = defineModel('open', {type: Boolean, default: false});

const router = useRouter();
const dialogsStore = useDialogsStore();
const {dialogs} = storeToRefs(dialogsStore);

const query = ref('');
const activeIndex = ref(0);
const input = ref(null);
const list = ref(null);

const {hits, isLoading, error} = useSearch(query);

const trimmed = computed(() => query.value.trim());
const matchedDialogs = computed(() => {
    if (!trimmed.value) {
        return dialogs.value.slice(0, RECENT_LIMIT);
    }

    const needle = normalize(trimmed.value);

    return dialogs.value
        .filter((dialog) => normalize(`${dialog.title} ${dialog.question}`).includes(needle))
        .slice(0, DIALOG_LIMIT);
});
const quickDocuments = computed(() =>
    trimmed.value
        ? []
        : Object.values(DOCUMENTS).map((document) => ({
              type: 'document',
              documentId: document.id,
              title: document.title,
              snippet: document.kindLabel,
          })),
);
const groups = computed(() => {
    const result = [];

    if (trimmed.value) {
        result.push({id: 'ask', title: '', items: [{kind: 'ask', key: 'ask', title: trimmed.value}]});
    }

    const documentItems = (trimmed.value ? hits.value : quickDocuments.value).map((hit) => ({
        kind: 'hit',
        key: `${hit.documentId}-${hit.clauseId ?? 'doc'}`,
        hit,
    }));

    if (documentItems.length) {
        result.push({id: 'documents', title: trimmed.value ? 'Документы и пункты' : 'Документы', items: documentItems});
    }

    if (matchedDialogs.value.length) {
        result.push({
            id: 'dialogs',
            title: trimmed.value ? 'Диалоги' : 'Недавние диалоги',
            items: matchedDialogs.value.map((dialog) => ({kind: 'dialog', key: `dialog-${dialog.id}`, dialog})),
        });
    }

    return result;
});
const flatItems = computed(() => groups.value.flatMap((group) => group.items));
const isEmpty = computed(() => Boolean(trimmed.value) && !isLoading.value && flatItems.value.length <= 1);

watch(isOpen, async (value) => {
    if (!value) {
        return;
    }

    query.value = '';
    activeIndex.value = 0;
    await nextTick();
    input.value?.focus();
});

watch(flatItems, () => {
    activeIndex.value = 0;
});

/** @param {(typeof flatItems.value)[number]} item */
function getIndex(item) {
    return flatItems.value.indexOf(item);
}

function close() {
    isOpen.value = false;
}

/** @param {(typeof flatItems.value)[number]} item */
async function activate(item) {
    close();

    if (item.kind === 'ask') {
        const dialogId = await dialogsStore.ask(item.title);

        router.push({name: ROUTE_NAMES.dialogs, params: {dialogId}});

        return;
    }

    if (item.kind === 'dialog') {
        router.push({name: ROUTE_NAMES.dialogs, params: {dialogId: item.dialog.id}});

        return;
    }

    router.push({
        name: ROUTE_NAMES.document,
        params: {documentId: item.hit.documentId},
        query: item.hit.clauseId ? {clause: item.hit.clauseId, edition: item.hit.editionId} : {},
    });
}

/** @param {number} step */
async function moveActive(step) {
    const count = flatItems.value.length;

    if (!count) {
        return;
    }

    activeIndex.value = (activeIndex.value + step + count) % count;
    await nextTick();
    list.value?.querySelector('[aria-selected="true"]')?.scrollIntoView({block: 'nearest'});
}

/** @param {KeyboardEvent} event */
function handleKeydown(event) {
    if (event.key === 'ArrowDown') {
        event.preventDefault();
        moveActive(1);
    } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        moveActive(-1);
    } else if (event.key === 'Enter') {
        event.preventDefault();

        const item = flatItems.value[activeIndex.value];

        if (item) {
            activate(item);
        }
    } else if (event.key === 'Escape') {
        close();
    }
}
</script>

<template>
    <Teleport to="body">
        <Transition name="search-palette">
            <div
                v-if="isOpen"
                class="search-palette"
                @mousedown.self="close"
            >
                <div
                    class="search-palette__panel"
                    role="dialog"
                    aria-modal="true"
                    aria-label="Поиск по базе знаний"
                >
                    <div class="search-palette__field">
                        <Search
                            class="search-palette__field-icon"
                            :size="20"
                            aria-hidden="true"
                        />
                        <input
                            ref="input"
                            v-model="query"
                            class="search-palette__input"
                            type="text"
                            placeholder="Найдите пункт, документ или задайте вопрос"
                            role="combobox"
                            aria-expanded="true"
                            aria-controls="search-palette-list"
                            aria-autocomplete="list"
                            @keydown="handleKeydown"
                        />
                        <button
                            class="search-palette__close"
                            type="button"
                            @click="close"
                        >
                            Esc
                        </button>
                    </div>

                    <div
                        id="search-palette-list"
                        ref="list"
                        class="search-palette__body"
                        role="listbox"
                    >
                        <section
                            v-for="group in groups"
                            :key="group.id"
                            class="search-palette__group"
                        >
                            <h3
                                v-if="group.title"
                                class="search-palette__group-title"
                            >
                                {{ group.title }}
                            </h3>
                            <button
                                v-for="item in group.items"
                                :key="item.key"
                                :class="[
                                    'search-palette__item',
                                    `search-palette__item--${item.kind}`,
                                    {'search-palette__item--active': getIndex(item) === activeIndex},
                                ]"
                                type="button"
                                role="option"
                                :aria-selected="getIndex(item) === activeIndex"
                                @mousemove="activeIndex = getIndex(item)"
                                @click="activate(item)"
                            >
                                <span class="search-palette__item-icon">
                                    <Sparkles
                                        v-if="item.kind === 'ask'"
                                        :size="18"
                                        aria-hidden="true"
                                    />
                                    <MessageSquareText
                                        v-else-if="item.kind === 'dialog'"
                                        :size="18"
                                        aria-hidden="true"
                                    />
                                    <FileText
                                        v-else
                                        :size="18"
                                        aria-hidden="true"
                                    />
                                </span>

                                <span
                                    v-if="item.kind === 'ask'"
                                    class="search-palette__item-body"
                                >
                                    <span class="search-palette__item-title">Спросить ассистента</span>
                                    <span class="search-palette__item-text">{{ item.title }}</span>
                                </span>
                                <span
                                    v-else-if="item.kind === 'dialog'"
                                    class="search-palette__item-body"
                                >
                                    <span class="search-palette__item-title">
                                        {{ item.dialog.number }} {{ item.dialog.title }}
                                    </span>
                                    <span class="search-palette__item-text">{{ item.dialog.question }}</span>
                                </span>
                                <span
                                    v-else
                                    class="search-palette__item-body"
                                >
                                    <span class="search-palette__item-title">{{ item.hit.title }}</span>
                                    <span class="search-palette__item-text">
                                        <template
                                            v-for="(part, index) in splitByMatch(item.hit.snippet, trimmed)"
                                            :key="index"
                                        >
                                            <mark
                                                v-if="part.isMatch"
                                                class="search-palette__match"
                                            >
                                                {{ part.text }}
                                            </mark>
                                            <template v-else>{{ part.text }}</template>
                                        </template>
                                    </span>
                                </span>

                                <CornerDownLeft
                                    class="search-palette__enter"
                                    :size="16"
                                    aria-hidden="true"
                                />
                            </button>
                        </section>

                        <div
                            v-if="isLoading && trimmed"
                            class="search-palette__loading"
                            aria-label="Ищу в документах"
                        >
                            <UiSkeleton
                                v-for="index in 3"
                                :key="index"
                                height="44px"
                            />
                        </div>

                        <p
                            v-if="isEmpty"
                            class="search-palette__empty"
                        >
                            В документах совпадений нет. Нажмите Enter — ассистент поищет ответ по смыслу.
                        </p>
                        <p
                            v-if="error"
                            class="search-palette__empty"
                            role="alert"
                        >
                            {{ error }}
                        </p>
                    </div>

                    <footer class="search-palette__footer">
                        <span><kbd class="search-palette__key">↑</kbd><kbd class="search-palette__key">↓</kbd> выбрать</span>
                        <span><kbd class="search-palette__key">Enter</kbd> открыть</span>
                        <span><kbd class="search-palette__key">Esc</kbd> закрыть</span>
                    </footer>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<style lang="scss">
.search-palette {
    $block: &;

    position: fixed;
    z-index: $ui-index-modal;
    display: flex;
    justify-content: center;
    background-color: rgba($color-ink, 35%);
    inset: 0;
    backdrop-filter: blur(4px);

    @include padding('top', 20);
    @include padding('x', 4);

    &-enter-active,
    &-leave-active {
        transition: opacity $duration-fast ease;

        #{$block}__panel {
            transition: transform $duration $ease-out;
        }
    }

    &-enter-from,
    &-leave-to {
        opacity: 0;

        #{$block}__panel {
            transform: translateY(-8px) scale(0.98);
        }
    }

    &__panel {
        display: flex;
        flex-direction: column;
        overflow: hidden;
        width: 100%;
        max-width: 680px;
        max-height: min(560px, calc(100vh - #{$indent-step * 40}));
        border: 1px solid $color-line;
        border-radius: $radius-2xl;
        background-color: $color-surface;
        box-shadow: 0 32px 64px -24px rgba($color-ink, 45%);
        align-self: flex-start;
    }

    &__field {
        display: flex;
        align-items: center;
        border-bottom: 1px solid $color-line;
        gap: $indent-step * 3;

        @include padding('x', 5);
    }

    &__field-icon {
        flex-shrink: 0;
        color: $color-ink-muted;
    }

    &__input {
        flex: 1;
        min-width: 0;
        height: 60px;
        color: $color-ink;
        border: none;
        outline: none;
        background: transparent;
        font: inherit;
        font-size: $font-size-lg;

        &::placeholder {
            color: $color-ink-faint;
        }
    }

    &__close {
        @include button-reset;
        @include focus-ring;

        flex-shrink: 0;
        color: $color-ink-muted;
        border: 1px solid $color-line;
        border-radius: $radius-sm;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;

        @include padding('y', 1);
        @include padding('x', 2);
    }

    &__body {
        overflow-y: auto;
        overscroll-behavior: contain;

        @include padding('y', 2);
        @include padding('x', 2);
    }

    &__group + &__group {
        @include margin('top', 2);
    }

    &__group-title {
        margin: 0;
        color: $color-ink-muted;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;

        @include padding('y', 2);
        @include padding('x', 3);
    }

    &__item {
        @include button-reset;

        display: flex;
        align-items: center;
        width: 100%;
        color: $color-ink;
        border-radius: $radius-lg;
        text-align: left;
        gap: $indent-step * 3;

        @include padding('y', 2.5);
        @include padding('x', 3);

        &--active {
            background-color: $color-lavender-soft;

            #{$block}__enter {
                opacity: 1;
            }

            #{$block}__item-icon {
                color: $color-navy;
                background-color: $color-surface;
            }
        }

        &--ask #{$block}__item-icon {
            color: $color-white;
            background-color: $color-action;
        }
    }

    &__item-icon {
        @include flex-center;

        flex-shrink: 0;
        width: 36px;
        height: 36px;
        color: $color-ink-soft;
        border-radius: $radius-md;
        background-color: $color-surface-muted;
    }

    &__item-body {
        flex: 1;
        min-width: 0;

        @include column(0);
    }

    &__item-title {
        overflow: hidden;
        font-size: $font-size-md;
        font-weight: $font-weight-bold;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    &__item-text {
        overflow: hidden;
        color: $color-ink-soft;
        font-size: $font-size-sm;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    &__item--hit &__item-text {
        font-family: $font-document;
    }

    &__match {
        color: $color-ink;
        border-radius: $radius-xs;
        background-color: $color-highlighter-amber;
    }

    &__enter {
        flex-shrink: 0;
        opacity: 0;
        color: $color-ink-muted;
    }

    &__loading {
        @include column($indent-step * 2);
        @include padding('x', 3);
        @include padding('y', 2);
    }

    &__empty {
        margin: 0;
        color: $color-ink-muted;
        font-size: $font-size-sm;
        text-align: center;

        @include padding('y', 4);
        @include padding('x', 4);
    }

    &__footer {
        display: flex;
        flex-wrap: wrap;
        color: $color-ink-muted;
        border-top: 1px solid $color-line;
        background-color: $color-surface-soft;
        font-size: $font-size-xs;
        gap: $indent-step * 5;

        @include padding('y', 2.5);
        @include padding('x', 5);
    }

    &__key {
        display: inline-block;
        min-width: 20px;
        color: $color-ink-soft;
        border: 1px solid $color-line;
        border-radius: $radius-xs;
        background-color: $color-surface;
        font-family: $font-primary;
        font-size: $font-size-2xs;
        font-weight: $font-weight-bold;
        text-align: center;

        @include margin('right', 1);
        @include padding('x', 1);
    }

    @include mobile {
        @include padding('top', 3);
        @include padding('x', 2);

        &__panel {
            max-height: calc(100vh - #{$indent-step * 30});
        }

        &__footer {
            display: none;
        }
    }
}
</style>
