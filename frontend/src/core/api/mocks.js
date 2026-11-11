export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS !== 'false';

const MOCK_LATENCY_MS = 350;

/**
 * @template T
 * @param {T} value
 * @param {number} [latency]
 * @returns {Promise<T>}
 */
export function resolveMock(value, latency = MOCK_LATENCY_MS) {
    return new Promise((resolve) => {
        setTimeout(() => resolve(structuredClone(value)), latency);
    });
}
