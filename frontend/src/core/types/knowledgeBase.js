/**
 * @typedef {Object} KnowledgeSection
 * @property {string} id
 * @property {string} title
 * @property {string} subtitle
 * @property {number} documentCount
 * @property {string} updatedLabel
 * @property {string} [image] Ключ картинки из `SECTION_IMAGES`
 * @property {string} initials Подпись плитки, если картинки нет
 * @property {string} [documentId] Документ, который открывается по клику
 */

/**
 * @typedef {Object} RecentAnswer
 * @property {string} id
 * @property {string} dialogId
 * @property {string} number
 * @property {string} question
 * @property {string} preview
 * @property {string} documentLabel
 * @property {string} [author]
 * @property {number} sourceCount
 * @property {boolean} isVerified
 * @property {import('@/core/types/assistant').Answer['status']} status
 * @property {string} dateLabel
 */

/**
 * @typedef {Object} BaseUpdate
 * @property {string} id
 * @property {string} title
 * @property {string} text
 * @property {string} meta
 * @property {boolean} isNew
 */

/**
 * @typedef {Object} AffectedAnswer
 * @property {string} dialogId
 * @property {string} number
 * @property {string} title
 * @property {string} reason
 */

/**
 * @typedef {Object} TeamStat
 * @property {string} id
 * @property {string} label
 * @property {string} value
 * @property {boolean} [isAlert]
 */

/**
 * @typedef {Object} KnowledgeBaseOverview
 * @property {{documentCount: number, citedShare: string, averageAnswerTime: string, metricsNote: string}} stats
 * @property {KnowledgeSection[]} sections
 * @property {RecentAnswer[]} myAnswers
 * @property {RecentAnswer[]} teamAnswers
 * @property {BaseUpdate[]} updates
 * @property {{summary: string, answers: AffectedAnswer[]}} affected
 * @property {TeamStat[]} teamStats
 * @property {string[]} examples
 */

export {};
