import {describe, expect, it} from 'vitest';
import {buildReferenceHtml, escapeHtml} from '@/core/utils/referenceDocument';

const DATA = {
    number: '№412',
    question: 'С кем согласовать договор <П-17>?',
    verdict: 'Проверено 1 из 1',
    dateLabel: 'Дата события: 10 ноября 2026',
    context: [{label: 'Договор', value: 'П-17/2024'}],
    paragraphs: [[{text: 'Нужен '}, {text: 'финдиректор', isBold: true}, {cite: 1}]],
    sources: [{title: 'Регламент, п. 2.3', meta: 'ред. 2025', before: 'Договоры на сумму', quote: 'свыше 3 млн', after: '.'}],
    author: 'Анна Корнеева',
};

describe('referenceDocument', () => {
    it('экранирует разметку', () => {
        expect(escapeHtml('<b>"A&B"</b>')).toBe('&lt;b&gt;&quot;A&amp;B&quot;&lt;/b&gt;');
    });

    it('собирает справку со сносками и источниками', () => {
        const html = buildReferenceHtml(DATA);

        expect(html).toContain('<b>финдиректор</b><sup>[1]</sup>');
        expect(html).toContain('&lt;П-17&gt;');
        expect(html).toContain('<b>Регламент, п. 2.3</b>');
        expect(html).toContain('Проверил: Анна Корнеева');
    });

    it('отмечает ответ без источников', () => {
        expect(buildReferenceHtml({...DATA, sources: []})).toContain('без ссылок на источники');
    });
});
