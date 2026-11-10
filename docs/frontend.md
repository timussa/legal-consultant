# Правила фронтенда

Сокращённая версия стандартов, по которым написан `frontend/`. Перед PR: `npm run lint && npm run test`.

## Vue

- Только `<script setup>` и JavaScript. Модели описаны JSDoc-типами в `core/types`.
- Порядок блоков SFC: `script setup` → `template` → `style lang="scss"` (без `scoped`).
- Порядок внутри `script`: импорты (библиотеки и `@/core`, пустая строка, компоненты) → `defineProps` / `defineEmits` / `defineModel` → composables и сторы (`storeToRefs`) → `ref` → `computed` → `watch` → хуки → функции.
- Обработчики называются `handle…`, булевы — `is…` / `has…` / `can…`.
- Функции объявляются через `function`; стрелки — только как inline-колбэки.
- Без сокращений в именах: `event`, `error`, `index`.
- `??` вместо `||` для значений по умолчанию, `Object.freeze` для констант.
- Комментарии только JSDoc. Пустой `catch` запрещён.
- `v-html` запрещён. Инлайновый `:style` — только для динамики через CSS-переменные.
- Иконки — компоненты Lucide.

## Слои

- Компонент не ходит в сеть: компонент → composable / store → `core/api`.
- `core` не импортирует `.vue`. `core/data` и `core/utils` не импортируют ничего из приложения, кроме констант.
- Маршруты — только по имени из `ROUTE_NAMES`.

## Стили

- БЭМ: блок = имя компонента в kebab-case (`DialogAnswer` → `.dialog-answer`). Элементы и модификаторы — только через `&`. Для вложенных ссылок на блок — `$block: &`.
- Цвета, радиусы, тени, шрифты — только токены из `vars.scss`. Хардкод цветов в компонентах запрещён.
- Отступы кратны `$indent-step` (4px), миксины `padding` / `margin`.
- Desktop-first: `@include laptop` (1240px), `@include tablet` (860px), `@include mobile` (540px).
- Ховеры только через `@include hover`.

## Тесты

Vitest, файлы `*.test.js` рядом с кодом. Покрываются чистые utils, сторы с замоканным `core/api`, composables без DOM.

## Prettier

4 пробела, одинарные кавычки, `printWidth: 120`, `bracketSpacing: false`, атрибуты — по одному на строку.

## Git

Ветка от `develop`, conventional commits (`feat(frontend): …`, `fix(frontend): …`).
