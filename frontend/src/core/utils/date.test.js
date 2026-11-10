import {describe, expect, it} from 'vitest';
import {formatLongDate, getGreeting} from '@/core/utils/date';

describe('date utils', () => {
    it('пишет дату словами', () => {
        expect(formatLongDate('2026-11-10')).toBe('10 ноября 2026');
        expect(formatLongDate('2024-02-12')).toBe('12 февраля 2024');
    });

    it.each([
        [7, 'Доброе утро'],
        [13, 'Добрый день'],
        [20, 'Добрый вечер'],
        [2, 'Доброй ночи'],
    ])('в %i часов — %s', (hour, expected) => {
        expect(getGreeting(hour)).toBe(expected);
    });
});
