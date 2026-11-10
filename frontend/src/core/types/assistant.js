/**
 * @typedef {Object} AnswerPart
 * @property {string} [text] Фрагмент текста ответа
 * @property {boolean} [isBold] Выделить жирным
 * @property {boolean} [isChanged] Фрагмент меняется в зависимости от даты события
 * @property {number} [cite] Номер источника из `Answer.sources`, начиная с 1
 */

/**
 * @typedef {Object} Source
 * @property {string} documentId
 * @property {string} clauseId Номер пункта, например `2.3`
 * @property {string} [editionId] Редакция документа, на которую опирается вывод
 * @property {string} title Название документа и пункт
 * @property {string} meta Редакция и срок действия
 * @property {string} before Текст перед цитатой
 * @property {string} quote Цитата, на которую опирается вывод
 * @property {string} after Текст после цитаты
 */

/**
 * @typedef {Object} PipelineStep
 * @property {string} title
 * @property {string} detail
 * @property {string} durationLabel
 */

/**
 * @typedef {Object} Turn
 * @property {'user' | 'assistant'} role
 * @property {string} text
 * @property {string} [badge] Плашка над ответом ассистента
 * @property {boolean} [isInjected] Сообщение выдаёт себя за системное
 */

/**
 * @typedef {Object} Answer
 * @property {import('@/core/constants').ANSWER_STATUSES[keyof import('@/core/constants').ANSWER_STATUSES]} status
 * @property {string} verdict
 * @property {string} totalDurationLabel
 * @property {AnswerPart[][]} paragraphs
 * @property {Source[]} sources
 * @property {PipelineStep[]} steps
 * @property {{label: string, value: string}[]} context
 * @property {string} [dateNote]
 * @property {string[]} [nextSteps]
 * @property {string[]} [followUps]
 * @property {string[]} [checkedDocuments]
 * @property {string[]} [options]
 * @property {Turn[]} [turns]
 */

/**
 * @typedef {Object} EventDate
 * @property {string} value Дата в формате ISO
 * @property {string} label
 */

/**
 * @typedef {Object} Dialog
 * @property {string} id
 * @property {string} number
 * @property {string} title
 * @property {string} documentLabel
 * @property {string} timeLabel
 * @property {Answer['status']} status
 * @property {string} question
 * @property {{summary: string, question: string, answer: string}} [history]
 * @property {EventDate[]} [eventDates]
 * @property {string} [eventDate]
 * @property {Answer} answer
 */

/**
 * @typedef {Object} AskRequest
 * @property {string} question
 * @property {string} [dialogId]
 * @property {string} [documentId]
 * @property {string} [eventDate]
 */

export {};
