# Юрассистент — фронтенд

Веб-интерфейс ИИ-ассистента для юристов банка: база знаний, диалоги с ответами со ссылками на пункты, просмотр документов по редакциям и схема проверки ответа.

Vue 3 (`<script setup>`, JavaScript) · Vite 5 · Pinia · Vue Router · SCSS · Lucide · Vitest.

## Запуск

```bash
cd frontend
npm install
npm run dev
```

Откроется на http://localhost:5173.

По умолчанию используется **реальный API**. Для автономной демонстрации задайте `VITE_USE_MOCKS=true`; в этом режиме бэкенд не нужен. Моки повторяют реальную базу знаний из `data/raw`: договор П-17/2024, ДС № 1, регламент согласования ред. 2023 и 2025.

Чтобы работать с Python-бэкендом:

```bash
cp .env.example .env
# в .env: VITE_USE_MOCKS=false
# VITE_DEV_API_TARGET=http://localhost:8000 — куда Vite проксирует /api
npm run dev
```

Контракт API — в [docs/api.md](../docs/api.md).

## Команды

| Команда | Что делает |
| --- | --- |
| `npm run dev` | дев-сервер с прокси `/api` |
| `npm run build` | сборка в `dist/` |
| `npm run lint` | ESLint |
| `npm run format` | Prettier |
| `npm run test` | тесты Vitest |

## Экраны

| Маршрут | Экран |
| --- | --- |
| `/` | База знаний: вопрос, метрики, разделы, последние ответы, устаревшие ответы, обновления. Роль «Руководитель» показывает статистику команды |
| `/dialogs/:dialogId?` | Диалог: ход проверки, ответ со сносками, нить к источнику, дата события, давление и подмена роли, обратная связь |
| `/documents/:documentId` | Документ: редакции, «было / стало», подсветка пункта из ответа, вопрос по выделенному фрагменту |
| `/verification` | Схема проверки ответа с подсветкой сценариев |

Переход из ответа в документ: `/documents/reglament?clause=2.3&edition=edition-2025&dialog=412&cite=3`.

## Структура

```
src/
  assets/
    images/        картинки разделов и метрик, реестр в index.js
    styles/        vars.scss (токены), mixins/, animations.scss, global.scss
  components/      по папке на экран + Ui/ для общих компонентов
  core/
    api/           запросы к бэкенду и моки (client.js, mocks.js)
    composables/   useAskPipeline, useEvidenceThread, useTextSelection, useRequest
    constants/     маршруты, статусы ответов, роли
    data/          мок-данные и статические справочники
    helpers/       getErrorMessage
    stores/        Pinia: dialogs, session, toast
    types/         JSDoc-типы моделей
    utils/         чистые функции + тесты рядом
  layouts/         DefaultLayout: шапка, сайдбар, тосты
  pages/           страницы маршрутов
  router/
```

Правила написания кода — в [docs/frontend.md](../docs/frontend.md).
