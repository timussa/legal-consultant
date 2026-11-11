import {describe, expect, it} from 'vitest';
import {buildSnippet, normalize, searchDocuments, splitByMatch} from '@/core/utils/search';

const DOCUMENTS = [
    {
        id: 'reglament',
        title: 'Регламент согласования договоров',
        kindLabel: 'Внутренний документ',
        editions: [{id: 'old'}, {id: 'new'}],
        sections: [
            {
                id: '2',
                clauses: [
                    {id: '2.3', versions: {old: 'Свыше 1 000 000 рублей — финдиректор.', new: 'Свыше 3 000 000 рублей — финансовый директор.'}},
                    {id: '2.5', versions: {new: 'Поручительство согласуется с финансовым директором.'}},
                ],
            },
        ],
    },
];

describe('search utils', () => {
    it('нормализует регистр, ё и пробелы', () => {
        expect(normalize('  Ёлка   ПАЛКА ')).toBe('елка палка');
    });

    it('находит документ по названию', () => {
        expect(searchDocuments(DOCUMENTS, 'регламент')[0]).toMatchObject({type: 'document', documentId: 'reglament'});
    });

    it('ищет пункты в последней редакции', () => {
        const hits = searchDocuments(DOCUMENTS, 'финансов');

        expect(hits.map((hit) => hit.clauseId)).toEqual(['2.3', '2.5']);
        expect(hits[0].editionId).toBe('new');
    });

    it('не ищет по одной букве', () => {
        expect(searchDocuments(DOCUMENTS, 'ф')).toEqual([]);
    });

    it('обрезает сниппет вокруг совпадения', () => {
        const text = `${'а'.repeat(100)} нужное слово ${'б'.repeat(100)}`;
        const snippet = buildSnippet(text, 'нужное');

        expect(snippet.startsWith('…')).toBe(true);
        expect(snippet.endsWith('…')).toBe(true);
        expect(snippet).toContain('нужное слово');
    });

    it('делит текст на части для подсветки', () => {
        expect(splitByMatch('Срок оплаты 30 дней', 'оплаты')).toEqual([
            {text: 'Срок ', isMatch: false},
            {text: 'оплаты', isMatch: true},
            {text: ' 30 дней', isMatch: false},
        ]);
        expect(splitByMatch('Текст', 'нет')).toEqual([{text: 'Текст', isMatch: false}]);
    });
});
