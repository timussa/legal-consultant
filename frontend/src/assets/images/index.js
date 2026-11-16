import brandMark from '@/assets/images/brand-mark.webp';
import brandParagraph from '@/assets/images/brand-paragraph.png';
import heroScene from '@/assets/images/hero-scene.webp';
import sectionContracts from '@/assets/images/section-contracts.png';
import sectionInternal from '@/assets/images/section-internal.png';
import sectionLabor from '@/assets/images/section-labor.png';
import sectionLaws from '@/assets/images/section-laws.png';
import sectionPersonalData from '@/assets/images/section-personal-data.png';
import sectionTaxes from '@/assets/images/section-taxes.png';
import statDocuments from '@/assets/images/stat-documents.png';
import statTime from '@/assets/images/stat-time.png';
import statVerified from '@/assets/images/stat-verified.png';
import verificationGate from '@/assets/images/verification/gate.webp';
import verificationGateLoop from '@/assets/images/verification/gate-loop.webp';
import verificationClarify from '@/assets/images/verification/icon-clarify.webp';
import verificationCompose from '@/assets/images/verification/icon-compose.webp';
import verificationGuard from '@/assets/images/verification/icon-guard.webp';
import verificationParse from '@/assets/images/verification/icon-parse.webp';
import verificationQuestion from '@/assets/images/verification/icon-question.webp';
import verificationRefusal from '@/assets/images/verification/icon-refusal.webp';
import verificationSearch from '@/assets/images/verification/icon-search.webp';
import verificationSelfcheck from '@/assets/images/verification/icon-selfcheck.webp';
import verificationScene from '@/assets/images/verification/scene.webp';

export const BRAND_IMAGE = brandParagraph;

export const BRAND_MARK = brandMark;

/** Фон баннера главной: navy-сцена со стеклянными панелями. */
export const HERO_SCENE = heroScene;

export const SECTION_IMAGES = Object.freeze({
    contracts: sectionContracts,
    internal: sectionInternal,
    labor: sectionLabor,
    laws: sectionLaws,
    personalData: sectionPersonalData,
    taxes: sectionTaxes,
});

export const STAT_IMAGES = Object.freeze({
    documents: statDocuments,
    verified: statVerified,
    time: statTime,
});

/** Стеклянные 3D-иконки и фон для схемы проверки. */
export const VERIFICATION_IMAGES = Object.freeze({
    scene: verificationScene,
    guard: verificationGuard,
    gate: verificationGate,
    gateLoop: verificationGateLoop,
    stages: Object.freeze({
        question: verificationQuestion,
        parse: verificationParse,
        search: verificationSearch,
        compose: verificationCompose,
        selfcheck: verificationSelfcheck,
    }),
    outcomes: Object.freeze({
        clarify: verificationClarify,
        refusal: verificationRefusal,
    }),
});
