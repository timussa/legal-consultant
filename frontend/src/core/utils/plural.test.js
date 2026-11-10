import {describe, expect, it} from 'vitest';
import {pluralize} from '@/core/utils/plural';

const FORMS = ['шаг', 'шага', 'шагов'];

describe('pluralize', () => {
    it.each([
        [1, 'шаг'],
        [3, 'шага'],
        [5, 'шагов'],
        [11, 'шагов'],
        [21, 'шаг'],
        [104, 'шага'],
    ])('%i → %s', (count, expected) => {
        expect(pluralize(count, FORMS)).toBe(expected);
    });
});
