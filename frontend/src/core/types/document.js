/**
 * @typedef {Object} Edition
 * @property {string} id
 * @property {string} label
 * @property {string} date
 * @property {string} [note]
 */

/**
 * @typedef {Object} Clause
 * @property {string} id Номер пункта, например `3.2`
 * @property {Record<string, string>} versions Текст пункта по id редакции; нет ключа — пункта в редакции нет
 */

/**
 * @typedef {Object} DocumentSection
 * @property {string} id
 * @property {string} title
 * @property {Clause[]} clauses
 */

/**
 * @typedef {Object} Citation
 * @property {string} clauseId
 * @property {string} dialogId
 * @property {string} dialogNumber
 * @property {string} dialogTitle
 * @property {number} cite
 */

/**
 * @typedef {Object} DocumentComment
 * @property {string} id
 * @property {string} author
 * @property {string} initials
 * @property {string} clauseId
 * @property {string} dateLabel
 * @property {string} text
 */

/**
 * @typedef {Object} LegalDocument
 * @property {string} id
 * @property {string} title
 * @property {string} kindLabel
 * @property {string} image
 * @property {Edition[]} editions
 * @property {{id: string, title: string}[]} outline Содержание документа целиком
 * @property {DocumentSection[]} sections Разделы, которые показываются в просмотрщике
 * @property {Citation[]} citations
 * @property {DocumentComment[]} comments
 * @property {string[]} files
 */

export {};
