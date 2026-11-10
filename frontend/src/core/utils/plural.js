/**
 * @param {number} count
 * @param {[string, string, string]} forms Формы для 1, 2 и 5: `['шаг', 'шага', 'шагов']`
 * @returns {string}
 */
export function pluralize(count, forms) {
    const lastTwo = Math.abs(count) % 100;
    const last = lastTwo % 10;

    if (lastTwo > 10 && lastTwo < 20) {
        return forms[2];
    }

    if (last === 1) {
        return forms[0];
    }

    return last > 1 && last < 5 ? forms[1] : forms[2];
}
