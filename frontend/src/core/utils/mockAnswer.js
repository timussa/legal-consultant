/**
 * @param {string} question
 * @param {ReadonlyArray<{key: string, words: string[]}>} keywords
 * @returns {string | null}
 */
export function findMockAnswerKey(question, keywords) {
    const normalized = question.toLowerCase();
    const match = keywords.find(({words}) => words.some((word) => normalized.includes(word)));

    return match?.key ?? null;
}
