/** @typedef {import('@/core/types/document').LegalDocument} LegalDocument */

/**
 * @typedef {Object} SearchHit
 * @property {'document' | 'clause'} type
 * @property {string} documentId
 * @property {string} [clauseId]
 * @property {string} [editionId]
 * @property {string} title
 * @property {string} snippet
 */

const SNIPPET_RADIUS = 48;
const MIN_QUERY_LENGTH = 2;

/**
 * @param {string} value
 * @returns {string}
 */
export function normalize(value) {
    return value.toLowerCase().replaceAll('ё', 'е').replace(/\s+/g, ' ').trim();
}

/**
 * Кусок текста вокруг первого совпадения.
 * @param {string} text
 * @param {string} query
 * @returns {string}
 */
export function buildSnippet(text, query) {
    const index = normalize(text).indexOf(normalize(query));

    if (index === -1) {
        return text.length > SNIPPET_RADIUS * 2 ? `${text.slice(0, SNIPPET_RADIUS * 2)}…` : text;
    }

    const start = Math.max(0, index - SNIPPET_RADIUS);
    const end = Math.min(text.length, index + query.length + SNIPPET_RADIUS);

    return `${start > 0 ? '…' : ''}${text.slice(start, end)}${end < text.length ? '…' : ''}`;
}

/**
 * Ищет по названиям документов и тексту пунктов в последней редакции.
 * @param {LegalDocument[]} documents
 * @param {string} query
 * @param {number} [limit]
 * @returns {SearchHit[]}
 */
export function searchDocuments(documents, query, limit = 8) {
    const needle = normalize(query);

    if (needle.length < MIN_QUERY_LENGTH) {
        return [];
    }

    const hits = [];

    for (const document of documents) {
        if (normalize(`${document.title} ${document.kindLabel}`).includes(needle)) {
            hits.push({type: 'document', documentId: document.id, title: document.title, snippet: document.kindLabel});
        }

        const editionId = document.editions.at(-1)?.id;

        for (const section of document.sections) {
            for (const clause of section.clauses) {
                const text = clause.versions[editionId];

                if (text && normalize(text).includes(needle)) {
                    hits.push({
                        type: 'clause',
                        documentId: document.id,
                        clauseId: clause.id,
                        editionId,
                        title: `${document.title}, п. ${clause.id}`,
                        snippet: buildSnippet(text, query),
                    });
                }
            }
        }
    }

    return hits.slice(0, limit);
}

/**
 * Делит текст на части, чтобы подсветить совпадение без v-html.
 * @param {string} text
 * @param {string} query
 * @returns {{text: string, isMatch: boolean}[]}
 */
export function splitByMatch(text, query) {
    const needle = normalize(query);
    const index = needle ? text.toLowerCase().replaceAll('ё', 'е').indexOf(needle) : -1;

    if (index === -1) {
        return [{text, isMatch: false}];
    }

    return [
        {text: text.slice(0, index), isMatch: false},
        {text: text.slice(index, index + needle.length), isMatch: true},
        {text: text.slice(index + needle.length), isMatch: false},
    ].filter((part) => part.text);
}
