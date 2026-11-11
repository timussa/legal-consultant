import {afterEach, describe, expect, it} from 'vitest';
import {readStored, writeStored} from '@/core/utils/storage';

const memory = new Map();

globalThis.window = globalThis.window ?? {};
window.localStorage = {
    getItem: (key) => (memory.has(key) ? memory.get(key) : null),
    setItem: (key, value) => memory.set(key, value),
};

describe('storage', () => {
    afterEach(() => memory.clear());

    it('возвращает запасное значение, если ничего не сохранено', () => {
        expect(readStored('settings', {isOn: true})).toEqual({isOn: true});
    });

    it('дополняет сохранённое значение новыми полями по умолчанию', () => {
        writeStored('settings', {isOn: false});

        expect(readStored('settings', {isOn: true, size: 2})).toEqual({isOn: false, size: 2});
    });

    it('не падает на испорченных данных', () => {
        memory.set('settings', '{oops');

        expect(readStored('settings', {isOn: true})).toEqual({isOn: true});
    });
});
