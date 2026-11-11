<script setup>
import {computed, ref, watch} from 'vue';
import {BookMarked, ChevronRight} from 'lucide-vue-next';
import {ROUTE_NAMES} from '@/core/constants';

import UiSegmented from '@/components/Ui/UiSegmented.vue';
import UiStatusPill from '@/components/Ui/UiStatusPill.vue';

const TABS = Object.freeze({mine: 'mine', team: 'team'});

const props = defineProps({
    /** @type {import('vue').PropType<import('@/core/types/knowledgeBase').RecentAnswer[]>} */
    myAnswers: {type: Array, required: true},
    /** @type {import('vue').PropType<import('@/core/types/knowledgeBase').RecentAnswer[]>} */
    teamAnswers: {type: Array, required: true},
    isHead: {type: Boolean, default: false},
});

const activeTab = ref(props.isHead ? TABS.team : TABS.mine);

const tabOptions = computed(() => [
    {value: TABS.mine, label: 'Мои', hint: String(props.myAnswers.length)},
    {value: TABS.team, label: 'Команды', hint: String(props.teamAnswers.length)},
]);
const answers = computed(() => (activeTab.value === TABS.team ? props.teamAnswers : props.myAnswers));

watch(
    () => props.isHead,
    (isHead) => {
        activeTab.value = isHead ? TABS.team : TABS.mine;
    },
);

/** @param {import('@/core/types/knowledgeBase').RecentAnswer} answer */
function getTarget(answer) {
    return {name: ROUTE_NAMES.dialogs, params: {dialogId: answer.dialogId}};
}
</script>

<template>
    <section class="home-recent-answers">
        <div class="home-recent-answers__head">
            <h2 class="home-recent-answers__title">Последние ответы</h2>
            <UiSegmented
                v-model="activeTab"
                :options="tabOptions"
                label="Чьи ответы показать"
            />
        </div>

        <ul class="home-recent-answers__list">
            <li
                v-for="answer in answers"
                :key="answer.id"
            >
                <RouterLink
                    class="home-recent-answers__item"
                    :to="getTarget(answer)"
                >
                    <span class="home-recent-answers__number">{{ answer.number }}</span>
                    <span class="home-recent-answers__body">
                        <span class="home-recent-answers__question">{{ answer.question }}</span>
                        <span class="home-recent-answers__preview">{{ answer.preview }}</span>
                        <span class="home-recent-answers__meta">
                            <span class="home-recent-answers__document">
                                <BookMarked
                                    :size="13"
                                    aria-hidden="true"
                                />
                                {{ answer.documentLabel }}
                            </span>
                            <span v-if="answer.sourceCount">· {{ answer.sourceCount }} ист.</span>
                            <span v-if="answer.author">· {{ answer.author }}</span>
                            <span>· {{ answer.dateLabel }}</span>
                        </span>
                    </span>
                    <UiStatusPill
                        class="home-recent-answers__status"
                        :status="answer.status"
                    />
                    <ChevronRight
                        class="home-recent-answers__chevron"
                        :size="18"
                        aria-hidden="true"
                    />
                </RouterLink>
            </li>
        </ul>
    </section>
</template>

<style lang="scss">
.home-recent-answers {
    $block: &;

    box-shadow: $shadow-card;

    @include card($radius-2xl);
    @include column($indent-step * 3);
    @include padding('y', 5);
    @include padding('x', 5);

    &__head {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: $indent-step * 3;
    }

    &__title {
        @include heading;
    }

    &__list {
        margin: 0;
        padding: 0;
        list-style: none;

        @include column(0);
    }

    &__item {
        @include focus-ring;

        display: flex;
        align-items: center;
        transition: background $duration ease;
        color: $color-ink;
        border-radius: $radius-xl;
        text-decoration: none;
        gap: $indent-step * 3;

        @include padding('y', 3);
        @include padding('x', 3);

        @include hover {
            background: $color-surface-soft;

            #{$block}__chevron {
                transform: translateX(2px);
                color: $color-violet;
            }
        }
    }

    &__number {
        @include flex-center;

        flex-shrink: 0;
        width: 52px;
        height: 36px;
        color: $color-navy;
        border-radius: $radius-md;
        background: $color-navy-tint;
        font-size: $font-size-xs;
        font-weight: $font-weight-extrabold;
    }

    &__body {
        flex: 1;
        min-width: 0;

        @include column($indent-step * 0.5);
    }

    &__question {
        font-size: $font-size-md;
        font-weight: $font-weight-bold;
    }

    &__preview {
        overflow: hidden;
        color: $color-ink-soft;
        font-size: $font-size-sm;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    &__meta {
        display: flex;
        flex-wrap: wrap;
        color: $color-ink-faint;
        font-size: $font-size-xs;
        font-weight: $font-weight-semibold;
        gap: $indent-step;
    }

    &__document {
        display: inline-flex;
        align-items: center;
        gap: $indent-step;
    }

    &__chevron {
        flex-shrink: 0;
        transition:
            color $duration ease,
            transform $duration $ease-out;
        color: $color-ink-decor;
    }

    @include mobile {
        @include padding('x', 3);

        &__number,
        &__chevron {
            display: none;
        }

        &__item {
            flex-wrap: wrap;
        }
    }
}
</style>
