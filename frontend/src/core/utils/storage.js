/**
 * Читает значение из localStorage. Если хранилище недоступно или данные испорчены, возвращает запасное значение.
 * @template T
 * @param {string} key
 * @param {T} fallback
 * @returns {T}
 */
export function readStored(key, fallback) {
    try {
        const raw = window.localStorage.getItem(key);

        return raw === null ? fallback : {...fallback, ...JSON.parse(raw)};
    } catch {
        return fallback;
    }
}

/**
 * @param {string} key
 * @param {unknown} value
 * @returns {boolean} удалось ли сохранить
 */
export function writeStored(key, value) {
    try {
        window.localStorage.setItem(key, JSON.stringify(value));

        return true;
    } catch {
        return false;
    }
}
