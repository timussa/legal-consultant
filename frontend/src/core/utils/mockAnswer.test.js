import {describe, expect, it} from 'vitest';
import {findMockAnswerKey} from '@/core/utils/mockAnswer';

const KEYWORDS = [
    {key: 'approval', words: ['соглас']},
    {key: 'payment', words: ['оплат']},
];

describe('findMockAnswerKey', () => {
    it('находит тему по ключевому слову без учёта регистра', () => {
        expect(findMockAnswerKey('С кем СОГЛАСОВАТЬ договор?', KEYWORDS)).toBe('approval');
    });

    it('возвращает первую подходящую тему', () => {
        expect(findMockAnswerKey('Срок оплаты и согласования', KEYWORDS)).toBe('approval');
    });

    it('возвращает null, если тема не найдена', () => {
        expect(findMockAnswerKey('Какая погода?', KEYWORDS)).toBeNull();
    });
});
