import {describe, expect, it} from 'vitest';
import {buildReferenceNote, buildThreadPath, countCitations, getAnswerText} from '@/core/utils/answer';

const PARAGRAPHS = [
    [{text: 'Ставка — '}, {text: '20 %', isBold: true}, {cite: 1}, {text: '.'}],
    [{text: 'Нужна виза'}, {cite: 2}, {text: '.'}],
];

const SOURCES = [
    {title: 'Договор, п. 2.1', meta: 'ред. 2024'},
    {title: 'Регламент, п. 2.3', meta: 'ред. 2025'},
];

describe('answer utils', () => {
    it('считает сноски во всех абзацах', () => {
        expect(countCitations(PARAGRAPHS)).toBe(2);
    });

    it('собирает текст ответа с номерами сносок', () => {
        expect(getAnswerText(PARAGRAPHS)).toBe('Ставка — 20 % [1].\n\nНужна виза [2].');
    });

    it('добавляет список источников в справку', () => {
        expect(buildReferenceNote('Вопрос', PARAGRAPHS, SOURCES)).toContain('[2] Регламент, п. 2.3, ред. 2025');
    });

    it('не добавляет блок источников, если их нет', () => {
        expect(buildReferenceNote('Вопрос', PARAGRAPHS, [])).not.toContain('Источники');
    });

    it('строит кривую от сноски к источнику', () => {
        expect(buildThreadPath({x: 0, y: 10}, {x: 200, y: 50})).toBe('M0 10 C100 10 100 50 200 50');
    });
});
