/** @typedef {import('@/core/types/document').LegalDocument} LegalDocument */

/**
 * @typedef {Object} TextDiff
 * @property {string} prefix
 * @property {string} removed
 * @property {string} added
 * @property {string} suffix
 */

/**
 * @param {string} before
 * @param {string} after
 * @returns {TextDiff}
 */
export function diffText(before, after) {
    if (before === after) {
        return {prefix: after, removed: '', added: '', suffix: ''};
    }

    let start = 0;

    while (start < before.length && start < after.length && before[start] === after[start]) {
        start += 1;
    }

    let endBefore = before.length;
    let endAfter = after.length;

    while (endBefore > start && endAfter > start && before[endBefore - 1] === after[endAfter - 1]) {
        endBefore -= 1;
        endAfter -= 1;
    }

    const wordStart = before.lastIndexOf(' ', start - 1) + 1;
    const nextSpace = after.indexOf(' ', endAfter);
    const wordTail =
        endAfter > 0 && after[endAfter - 1] !== ' ' ? (nextSpace === -1 ? after.length : nextSpace) - endAfter : 0;

    endAfter += wordTail;
    endBefore += wordTail;

    return {
        prefix: after.slice(0, wordStart),
        removed: before.slice(wordStart, endBefore),
        added: after.slice(wordStart, endAfter),
        suffix: after.slice(endAfter),
    };
}

/**
 * @param {LegalDocument} document
 * @param {string} editionId
 * @returns {string | null}
 */
export function getPreviousEditionId(document, editionId) {
    const index = document.editions.findIndex((edition) => edition.id === editionId);

    return index > 0 ? document.editions[index - 1].id : null;
}

/**
 * @param {LegalDocument} document
 * @param {string} editionId
 * @returns {{clauseId: string, sectionId: string, isAdded: boolean}[]}
 */
export function getChangedClauses(document, editionId) {
    const previousId = getPreviousEditionId(document, editionId);

    if (!previousId) {
        return [];
    }

    return document.sections.flatMap((section) =>
        section.clauses
            .filter(
                (clause) => clause.versions[editionId] && clause.versions[editionId] !== clause.versions[previousId],
            )
            .map((clause) => ({clauseId: clause.id, sectionId: section.id, isAdded: !clause.versions[previousId]})),
    );
}
