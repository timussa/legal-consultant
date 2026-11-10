import {describe, expect, it} from 'vitest';
import {diffText, getChangedClauses, getPreviousEditionId} from '@/core/utils/document';

const DOCUMENT = {
    editions: [{id: 'old'}, {id: 'new'}],
    sections: [
        {
            id: '2',
            clauses: [
                {id: '2.1', versions: {old: 'Порог — 1 млн рублей.', new: 'Порог — 3 млн рублей.'}},
                {id: '2.2', versions: {old: 'Без изменений.', new: 'Без изменений.'}},
                {id: '2.5', versions: {new: 'Новый пункт.'}},
            ],
        },
    ],
};

describe('document utils', () => {
    it('выделяет изменившееся слово целиком', () => {
        expect(diffText('Порог — 1 млн рублей.', 'Порог — 3 млн рублей.')).toEqual({
            prefix: 'Порог — ',
            removed: '1',
            added: '3',
            suffix: ' млн рублей.',
        });
    });

    it('возвращает пустые изменения для одинаковых строк', () => {
        const diff = diffText('Текст.', 'Текст.');

        expect(diff.removed).toBe('');
        expect(diff.added).toBe('');
    });

    it('находит предыдущую редакцию', () => {
        expect(getPreviousEditionId(DOCUMENT, 'new')).toBe('old');
        expect(getPreviousEditionId(DOCUMENT, 'old')).toBeNull();
    });

    it('находит изменённые и добавленные пункты', () => {
        expect(getChangedClauses(DOCUMENT, 'new')).toEqual([
            {clauseId: '2.1', sectionId: '2', isAdded: false},
            {clauseId: '2.5', sectionId: '2', isAdded: true},
        ]);
    });

    it('для первой редакции изменений нет', () => {
        expect(getChangedClauses(DOCUMENT, 'old')).toEqual([]);
    });
});
