/** @typedef {import('@/core/types/assistant').AnswerPart} AnswerPart */
/** @typedef {import('@/core/types/assistant').Source} Source */

const HTML_ENTITIES = Object.freeze({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'});

/**
 * @param {string} value
 * @returns {string}
 */
export function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => HTML_ENTITIES[char]);
}

/**
 * @param {AnswerPart[]} paragraph
 * @returns {string}
 */
function renderParagraph(paragraph) {
    return paragraph
        .map((part) => {
            if (part.cite !== undefined) {
                return `<sup>[${part.cite}]</sup>`;
            }

            const text = escapeHtml(part.text);

            return part.isBold ? `<b>${text}</b>` : text;
        })
        .join('');
}

/**
 * Справка для Word: вопрос, вывод со сносками, источники с цитатами.
 * @param {{number: string, question: string, verdict: string, dateLabel: string, context: {label: string, value: string}[], paragraphs: AnswerPart[][], sources: Source[], author: string}} data
 * @returns {string}
 */
export function buildReferenceHtml(data) {
    const context = data.context.map((item) => `${escapeHtml(item.label)}: ${escapeHtml(item.value)}`).join('; ');
    const body = data.paragraphs.map((paragraph) => `<p>${renderParagraph(paragraph)}</p>`).join('');
    const sources = data.sources.length
        ? `<h2>Источники</h2><ol>${data.sources
              .map(
                  (source) =>
                      `<li><b>${escapeHtml(source.title)}</b> (${escapeHtml(source.meta)})<br/>«${escapeHtml(
                          `${source.before} ${source.quote}${source.after}`.trim(),
                      )}»</li>`,
              )
              .join('')}</ol>`
        : '<p><i>Ответ дан без ссылок на источники: подходящих пунктов в базе знаний нет.</i></p>';

    return [
        '<html><head><meta charset="utf-8"><title>Справка</title>',
        '<style>body{font-family:"PT Serif","Times New Roman",serif;font-size:12pt;line-height:1.5}',
        'h1{font-size:16pt}h2{font-size:13pt;margin-top:18pt}.meta{color:#555;font-size:10pt}</style></head><body>',
        `<h1>Справка по вопросу ${escapeHtml(data.number)}</h1>`,
        `<p class="meta">${escapeHtml(data.dateLabel)}. ${context}. Статус: ${escapeHtml(data.verdict)}.</p>`,
        `<h2>Вопрос</h2><p>${escapeHtml(data.question)}</p>`,
        `<h2>Ответ</h2>${body}`,
        sources,
        `<p class="meta">Подготовлено Юрассистентом по базе знаний. Проверил: ${escapeHtml(data.author)}.</p>`,
        '</body></html>',
    ].join('');
}
