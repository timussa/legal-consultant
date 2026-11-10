<script setup>
import {storeToRefs} from 'pinia';
import {useRouter} from 'vue-router';
import {getKnowledgeBaseOverview} from '@/core/api/knowledgeBase';
import {useRequest} from '@/core/composables/useRequest';
import {ROUTE_NAMES} from '@/core/constants';
import {useDialogsStore} from '@/core/stores/dialogs';
import {useSessionStore} from '@/core/stores/session';
import {useToastStore} from '@/core/stores/toast';

import HomeAffected from '@/components/Home/HomeAffected.vue';
import HomeHero from '@/components/Home/HomeHero.vue';
import HomeRecentAnswers from '@/components/Home/HomeRecentAnswers.vue';
import HomeSections from '@/components/Home/HomeSections.vue';
import HomeStats from '@/components/Home/HomeStats.vue';
import HomeTeamStats from '@/components/Home/HomeTeamStats.vue';
import HomeUpdates from '@/components/Home/HomeUpdates.vue';
import UiState from '@/components/Ui/UiState.vue';

const router = useRouter();
const dialogsStore = useDialogsStore();
const sessionStore = useSessionStore();
const toastStore = useToastStore();
const {askingDialogId} = storeToRefs(dialogsStore);
const {isHead, user} = storeToRefs(sessionStore);

const {data: overview, isLoading, error, reload} = useRequest(getKnowledgeBaseOverview);

/** @param {string} question */
async function handleAsk(question) {
    const dialogId = await dialogsStore.ask(question);

    router.push({name: ROUTE_NAMES.dialogs, params: {dialogId}});
}

/** @param {import('@/core/types/knowledgeBase').KnowledgeSection} section */
function handleSectionUnavailable(section) {
    toastStore.show(`«${section.title}»: просмотр появится после загрузки документов в базу`);
}
</script>

<template>
    <div class="home-page">
        <HomeHero
            :user-name="user.name"
            :examples="overview?.examples ?? []"
            :is-asking="askingDialogId !== null"
            @ask="handleAsk"
        />

        <UiState
            v-if="!overview"
            :is-loading="isLoading"
            :error="error"
            loading-text="Загружаем базу знаний…"
            @retry="reload"
        />

        <template v-else>
            <HomeStats :stats="overview.stats" />
            <HomeTeamStats
                v-if="isHead"
                :stats="overview.teamStats"
            />
            <HomeSections
                :sections="overview.sections"
                @unavailable="handleSectionUnavailable"
            />
            <div class="home-page__columns">
                <HomeRecentAnswers
                    :my-answers="overview.myAnswers"
                    :team-answers="overview.teamAnswers"
                    :is-head="isHead"
                />
                <div class="home-page__aside">
                    <HomeAffected :affected="overview.affected" />
                    <HomeUpdates :updates="overview.updates" />
                </div>
            </div>
        </template>
    </div>
</template>

<style lang="scss">
.home-page {
    max-width: 1280px;
    margin: 0 auto;

    @include column($indent-step * 7);

    &__columns {
        display: grid;
        align-items: start;
        grid-template-columns: minmax(0, 1fr) 360px;
        gap: $indent-step * 5;
    }

    &__aside {
        @include column($indent-step * 5);
    }

    @include tablet {
        gap: $indent-step * 5;

        &__columns {
            grid-template-columns: 1fr;
        }
    }
}
</style>
