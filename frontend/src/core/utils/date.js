const MONTHS_GENITIVE = Object.freeze([
    'января',
    'февраля',
    'марта',
    'апреля',
    'мая',
    'июня',
    'июля',
    'августа',
    'сентября',
    'октября',
    'ноября',
    'декабря',
]);

/**
 * @param {string} isoDate Дата в формате `YYYY-MM-DD`
 * @returns {string} Например, `10 ноября 2026`
 */
export function formatLongDate(isoDate) {
    const [year, month, day] = isoDate.split('-').map(Number);

    return `${day} ${MONTHS_GENITIVE[month - 1]} ${year}`;
}

/**
 * @param {number} hour Час от 0 до 23
 * @returns {string}
 */
export function getGreeting(hour) {
    if (hour >= 5 && hour < 12) {
        return 'Доброе утро';
    }

    if (hour >= 12 && hour < 18) {
        return 'Добрый день';
    }

    if (hour >= 18 && hour < 23) {
        return 'Добрый вечер';
    }

    return 'Доброй ночи';
}
