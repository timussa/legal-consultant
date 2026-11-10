<script setup>
import {computed, nextTick, ref, watch} from 'vue';
import {History} from 'lucide-vue-next';
import {storeToRefs} from 'pinia';
import {useRoute, useRouter} from 'vue-router';
import {useAskPipeline} from '@/core/composables/useAskPipeline';
import {useEvidenceThread} from '@/core/composables/useEvidenceThread';
import {ANSWER_STATUSES, ROUTE_NAMES} from '@/core/constants';
import {useDialogsStore} from '@/core/stores/dialogs';
import {useToastStore} from '@/core/stores/toast';
import {buildReferenceNote} from '@/core/utils/answer';

import DialogAnswer from '@/components/Dialogs/DialogAnswer.vue';
import DialogBand from '@/components/Dialogs/DialogBand.vue';
import DialogComposer from '@/components/Dialogs/DialogComposer.vue';
import DialogEmpty from '@/components/Dialogs/DialogEmpty.vue';
import DialogList from '@/components/Dialogs/DialogList.vue';
import DialogPipeline from '@/components/Dialogs/DialogPipeline.vue';
import DialogSources from '@/components/Dialogs/DialogSources.vue';
import DialogThread from '@/components/Dialogs/DialogThread.vue';
import DialogTurns from '@/components/Dialogs/DialogTurns.vue';
import UiState from '@/components/Ui/UiState.vue';

const route = useRoute();
const router = useRouter();
const dialogsStore = useDialogsStore();
const toastStore = useToastStore();
const {dialogs, isLoading, loadError, askingDialogId, askError, feedback} = storeToRefs(dialogsStore);

const workspace = ref(null);
const sourcesPanel = ref(null);
const hoveredCite = ref(null);
const pinnedCite = ref(null);

const dialogId = computed(() => (typeof route.params.dialogId === 'string' ? route.params.dialogId : ''));
const dialog = computed(() => dialogsStore.getDialog(dialogId.value));
const answer = computed(() => dialog.value?.answer ?? null);
const isAsking = computed(() => Boolean(dialog.value) && askingDialogId.value === dialog.value.id);
const activeCite = computed(() => hoveredCite.value ?? pinnedCite.value);

const {activeStepIndex, revealedCiteCount, isStepsDone, progress, replay} = useAskPipeline(answer);
const {path: threadPath, size: threadSize} = useEvidenceThread(workspace, activeCite);

const isAnswerVisible = computed(() => Boolean(answer.value) && isStepsDone.value && !isAsking.value);

watch(dialogId, () => {
    hoveredCite.value = null;
    pinnedCite.value = null;
});

watch(
    () => route.query.question,
    async (question) => {
        if (typeof question !== 'string' || !question.trim()) {
            return;
        }

        await dialogsStore.load();

        const nextDialogId = await dialogsStore.ask(question);

        router.replace({name: ROUTE_NAMES.dialogs, params: {dialogId: nextDialogId}});
    },
    {immediate: true},
);

/** @param {string} question */
async function handleAsk(question) {
    if (dialog.value) {
        await dialogsStore.ask(question, {dialogId: dialog.value.id});

        return;
    }

    const nextDialogId = await dialogsStore.ask(question);

    router.push({name: ROUTE_NAMES.dialogs, params: {dialogId: nextDialogId}});
}

/** @param {string} option */
function handleChooseOption(option) {
    const isClarification = answer.value?.status === ANSWER_STATUSES.clarification;

    handleAsk(isClarification ? `${dialog.value.question} Речь о договоре ${option}.` : option);
}

/** @param {string} eventDate */
function handleChangeDate(eventDate) {
    dialogsStore.changeEventDate(dialog.value.id, eventDate);
}

/** @param {number} cite */
function scrollSourceIntoView(cite) {
    const panel = sourcesPanel.value?.$el;
    const card = panel?.querySelector(`[data-source-anchor="${cite}"]`);

    if (!card || panel.scrollHeight <= panel.clientHeight) {
        return;
    }

    const offset = 16;
    const panelRect = panel.getBoundingClientRect();
    const cardRect = card.getBoundingClientRect();
    const visibleTop = Math.max(panelRect.top, 0);
    const visibleBottom = Math.min(panelRect.bottom, window.innerHeight);

    if (cardRect.top < visibleTop) {
        panel.scrollTo({top: panel.scrollTop + cardRect.top - visibleTop - offset, behavior: 'smooth'});
    } else if (cardRect.bottom > visibleBottom) {
        panel.scrollTo({top: panel.scrollTop + cardRect.bottom - visibleBottom + offset, behavior: 'smooth'});
    }
}

/** @param {number} cite */
function handleActivateCite(cite) {
    hoveredCite.value = cite;
    scrollSourceIntoView(cite);
}

/** @param {number} cite */
function handleDeactivateCite(cite) {
    if (hoveredCite.value === cite) {
        hoveredCite.value = null;
    }
}

/** @param {number} cite */
async function handleSelectCite(cite) {
    pinnedCite.value = pinnedCite.value === cite ? null : cite;

    await nextTick();
    scrollSourceIntoView(cite);
}

/** @param {string} value */
async function handleFeedback(value) {
    const isSaved = await dialogsStore.setFeedback(dialog.value.id, value);

    if (isSaved && feedback.value[dialog.value.id]) {
        toastStore.show('Отметка сохранена — ответ увидит руководитель');
    }
}

async function handleCopy() {
    const note = buildReferenceNote(dialog.value.question, answer.value.paragraphs, answer.value.sources);

    try {
        await navigator.clipboard.writeText(note);
        toastStore.show('Справка со ссылками скопирована');
    } catch (error) {
        toastStore.show(`Не удалось скопировать: ${error instanceof Error ? error.message : 'нет доступа'}`);
    }
}
</script>

<template>
    <div class="dialogs-page">
        <DialogList
            class="dialogs-page__list"
            :dialogs="dialogs"
            :active-dialog-id="dialog?.id ?? null"
            :asking-dialog-id="askingDialogId"
        />

        <div class="dialogs-page__content">
            <template v-if="!dialogId">
                <DialogEmpty @ask="handleAsk" />
                <DialogComposer
                    placeholder="Задайте вопрос по договорам, регламентам или законам"
                    :is-asking="askingDialogId !== null"
                    @ask="handleAsk"
                />
            </template>

            <UiState
                v-else-if="!dialog"
                :is-loading="isLoading"
                :error="loadError ?? (isLoading ? null : 'Диалог не найден. Возможно, он был удалён.')"
                loading-text="Поднимаю историю диалогов…"
                @retry="dialogsStore.load"
            />

            <template v-else>
                <DialogBand
                    :dialog="dialog"
                    :is-asking="isAsking"
                    @change-date="handleChangeDate"
                />

                <div
                    ref="workspace"
                    class="dialogs-page__workspace"
                >
                    <DialogThread
                        :path="threadPath"
                        :width="threadSize.width"
                        :height="threadSize.height"
                    />

                    <div class="dialogs-page__conversation">
                        <details
                            v-if="dialog.history"
                            class="dialogs-page__history"
                        >
                            <summary class="dialogs-page__history-summary">
                                <History
                                    :size="16"
                                    aria-hidden="true"
                                />
                                Ранее в диалоге: {{ dialog.history.summary }}
                            </summary>
                            <p class="dialogs-page__history-question">{{ dialog.history.question }}</p>
                            <p class="dialogs-page__history-answer">{{ dialog.history.answer }}</p>
                        </details>

                        <p class="dialogs-page__question">{{ dialog.question }}</p>

                        <DialogPipeline
                            :steps="answer?.steps ?? []"
                            :active-step-index="activeStepIndex"
                            :progress="progress"
                            :total-duration-label="answer?.totalDurationLabel ?? ''"
                            :is-waiting="isAsking || !answer"
                            :is-done="isStepsDone"
                            @replay="replay"
                        />

                        <DialogAnswer
                            v-if="isAnswerVisible"
                            :answer="answer"
                            :revealed-cite-count="revealedCiteCount"
                            :active-cite="activeCite"
                            :feedback="feedback[dialog.id] ?? null"
                            @activate-cite="handleActivateCite"
                            @deactivate-cite="handleDeactivateCite"
                            @select-cite="handleSelectCite"
                            @ask="handleAsk"
                            @choose-option="handleChooseOption"
                            @feedback="handleFeedback"
                            @copy="handleCopy"
                        />

                        <DialogTurns
                            v-if="isAnswerVisible && answer.turns?.length"
                            :turns="answer.turns"
                        />

                        <p
                            v-if="askError"
                            class="dialogs-page__error"
                            role="alert"
                        >
                            {{ askError }}
                        </p>

                        <DialogComposer
                            :is-asking="isAsking"
                            @ask="handleAsk"
                        />
                    </div>

                    <DialogSources
                        v-if="isAnswerVisible"
                        ref="sourcesPanel"
                        class="dialogs-page__sources"
                        :sources="answer.sources"
                        :active-cite="activeCite"
                        :revealed-cite-count="revealedCiteCount"
                        :dialog-id="dialog.id"
                        @activate-cite="handleActivateCite"
                        @deactivate-cite="handleDeactivateCite"
                    />
                </div>
            </template>
        </div>
    </div>
</template>

<style lang="scss">
.dialogs-page {
    display: grid;
    align-items: start;
    max-width: 1520px;
    margin: 0 auto;
    grid-template-columns: 264px minmax(0, 1fr);
    gap: $indent-step * 6;

    &__list {
        position: sticky;
        top: $header-height + $indent-step * 6;
        overflow-y: auto;
        max-height: calc(100vh - #{$header-height + $indent-step * 12});
    }

    &__content {
        min-width: 0;

        @include column($indent-step * 5);
    }

    &__workspace {
        position: relative;
        display: grid;
        align-items: start;
        grid-template-columns: minmax(0, 1fr) 340px;
        gap: $indent-step * 8;
    }

    &__conversation {
        min-width: 0;

        @include column($indent-step * 4);
    }

    &__history {
        color: $color-ink-soft;
        border: 1px solid $color-line;
        border-radius: $radius-xl;
        background: $color-surface-soft;
        font-size: $font-size-sm;

        @include padding('y', 2.5);
        @include padding('x', 4);
    }

    &__history-summary {
        display: flex;
        align-items: center;
        font-weight: $font-weight-semibold;
        cursor: pointer;
        gap: $indent-step * 2;
        list-style: none;

        &::-webkit-details-marker {
            display: none;
        }
    }

    &__history-question {
        color: $color-ink;
        font-weight: $font-weight-bold;

        @include margin('top', 3);
        @include margin('bottom', 1);
    }

    &__history-answer {
        margin: 0;
        line-height: 1.5;
    }

    &__question {
        align-self: flex-end;
        max-width: 78%;
        margin: 0;
        color: $color-white;
        border-radius: $radius-2xl $radius-2xl $radius-xs $radius-2xl;
        background: $color-action;
        box-shadow: $shadow-bubble;
        font-size: $font-size-base;
        font-weight: $font-weight-medium;
        line-height: 1.55;
        animation: fade-up $duration $ease-out both;

        @include padding('y', 3.5);
        @include padding('x', 4.5);
    }

    &__error {
        margin: 0;
        color: $color-peach-ink;
        border-radius: $radius-lg;
        background: $color-peach;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;

        @include padding('y', 3);
        @include padding('x', 4);
    }

    &__sources {
        position: sticky;
        top: $header-height + $indent-step * 6;
        overflow-y: auto;
        max-height: calc(100vh - #{$header-height + $indent-step * 12});
        scrollbar-width: thin;

        @include padding('right', 1);
        @include padding('bottom', 60);
    }

    @include laptop {
        &__workspace {
            grid-template-columns: 1fr;
            gap: $indent-step * 5;
        }

        &__sources {
            position: static;
            max-height: none;

            @include padding('bottom', 0);
        }
    }

    @include tablet {
        grid-template-columns: 1fr;

        &__list {
            position: static;
            max-height: none;
        }
    }

    @include mobile {
        &__question {
            max-width: 100%;
        }
    }
}
</style>
