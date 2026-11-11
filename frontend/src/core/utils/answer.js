/** @typedef {import('@/core/types/assistant').AnswerPart} AnswerPart */
/** @typedef {import('@/core/types/assistant').Source} Source */

/**
 * @param {AnswerPart[][]} paragraphs
 * @returns {number}
 */
export function countCitations(paragraphs) {
    return paragraphs.flat().filter((part) => part.cite !== undefined).length;
}

/**
 * @param {AnswerPart[][]} paragraphs
 * @returns {string}
 */
export function getAnswerText(paragraphs) {
    return paragraphs
        .map((paragraph) => paragraph.map((part) => (part.cite === undefined ? part.text : ` [${part.cite}]`)).join(''))
        .join('\n\n');
}

/**
 * @param {string} title
 * @param {AnswerPart[][]} paragraphs
 * @param {Source[]} sources
 * @returns {string}
 */
export function buildReferenceNote(title, paragraphs, sources) {
    const body = getAnswerText(paragraphs);

    if (!sources.length) {
        return `${title}\n\n${body}`;
    }

    const references = sources.map((source, index) => `[${index + 1}] ${source.title}, ${source.meta}`).join('\n');

    return `${title}\n\n${body}\n\nИсточники:\n${references}`;
}

/**
 * @param {{x: number, y: number}} from
 * @param {{x: number, y: number}} to
 * @returns {string}
 */
export function buildThreadPath(from, to) {
    const minimalBend = 60;
    const bend = Math.max(minimalBend, (to.x - from.x) / 2);

    return `M${from.x} ${from.y} C${from.x + bend} ${from.y} ${to.x - bend} ${to.y} ${to.x} ${to.y}`;
}

/**
 * Склеивает текст до и после цитаты с правильными пробелами.
 * @param {{before: string, after: string}} source
 * @returns {{before: string, after: string}}
 */
export function getQuoteSurroundings(source) {
    const before = source.before ? `${source.before.trimEnd()} ` : '';
    const after = source.after.trimStart();

    return {before, after: /^[.,;:!?)»]/.test(after) || !after ? after : ` ${after}`};
}

/**
 * Позиции частей ответа в общем тексте: нужны, чтобы печатать ответ по символам.
 * Сноска занимает ноль символов и стоит там, где закончился текст перед ней.
 * @param {AnswerPart[][]} paragraphs
 * @returns {{starts: number[][], citeOffsets: number[], total: number}}
 */
export function getPartOffsets(paragraphs) {
    let position = 0;

    const citeOffsets = [];
    const starts = paragraphs.map((paragraph) =>
        paragraph.map((part) => {
            const start = position;

            if (part.cite === undefined) {
                position += part.text?.length ?? 0;
            } else {
                citeOffsets.push(start);
            }

            return start;
        }),
    );

    return {starts, citeOffsets, total: position};
}
