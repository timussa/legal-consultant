# API для фронтенда

Контракт между веб-интерфейсом и Python-бэкендом. Фронт уже работает по нему на моках (`VITE_USE_MOCKS=true`). Как только бэкенд отдаёт эти ответы, моки выключаются в `.env`, и код фронта менять не нужно.

- Базовый путь: `/api`. В dev Vite проксирует `/api/*` на `http://localhost:8000/api/*` без изменения пути.
- Формат: JSON, UTF-8. Даты — строки ISO `YYYY-MM-DD`. Названия полей — camelCase.
- Ошибка: любой статус ≥ 400 с телом `{"error": {"code": 123, "message": "Текст для пользователя"}}`. `message` показывается пользователю как есть.

Полные JSDoc-типы: `frontend/src/core/types/*.js`. Примеры данных: `frontend/src/core/data/*.js`.

## Авторизация

Все пути, кроме `/api/health` и `/api/v1/auth/login`, требуют входа. Без сессии сервер отвечает `401`.

- `POST /api/v1/auth/login` с `{"login", "password"}` возвращает `{"token", "expiresAt", "user"}`. Сервер ставит HttpOnly-cookie `legal_session` (`SameSite=Strict`, `Path=/api`). Браузеру больше ничего не нужно: фронт токен не хранит.
- Для скриптов и Swagger тот же токен передаётся заголовком `Authorization: Bearer <token>`.
- Сессия живёт `SESSION_TTL_HOURS` (по умолчанию 12 ч) и продлевается при активности. В базе хранится только SHA-256 токена.
- Пароли хешируются scrypt. После `LOGIN_MAX_FAILURES` неудачных попыток логин блокируется на `LOGIN_LOCK_MINUTES`, ответ — `429`. Неизвестный логин и неверный пароль дают одинаковый ответ.
- Роли: `lawyer` и `head`. Самостоятельной регистрации нет: учётные записи создаёт руководитель через `/api/v1/users`. При первом запуске создаются демо-учётные записи `lawyer`, `lawyer2`, `head` с паролем из `DEMO_PASSWORD`, либо записи из `BOOTSTRAP_USERS`.

`user`: `{"id", "login", "name", "initials", "position", "role"}`.

## Права

| Действие | Юрист | Руководитель |
| --- | --- | --- |
| Вопросы, свои диалоги, отзыв на свой ответ | да | да |
| Чужие диалоги | нет (`404`) | только чтение, `GET /dialogs?scope=team` |
| Решение по спорному ответу (`review`) | `403` | да |
| Цитирования в просмотрщике документа | из своих ответов | из ответов команды |
| Комментарии к пунктам | добавлять, удалять свои | добавлять, удалять любые |
| Пользователи, аудит, загрузка документов, переиндексация | `403` | да |
| `teamAnswers` на главной (вопрос и превью ответа коллег) | да | да, плюс все неразобранные спорные |
| `teamStats` на главной | пустой список | метрики команды за 7 дней |

## Эндпоинты

| Метод | Путь | Ответ |
| --- | --- | --- |
| GET | `/api/health` | без входа: `{status, documents, chunks, denseSearch}` |
| POST | `/api/v1/auth/login` | `{token, expiresAt, user}` + cookie |
| POST | `/api/v1/auth/logout` | `204`, сессия удаляется |
| GET | `/api/v1/auth/me` | `user` |
| POST | `/api/v1/auth/password` | `{currentPassword, newPassword}` → `204`; остальные сессии пользователя закрываются |
| GET | `/api/v1/knowledge-base` | `KnowledgeBaseOverview` — данные главной |
| GET | `/api/v1/dialogs` | `Dialog[]` — свои диалоги, новые сверху. `?scope=team` — все (только `head`) |
| GET | `/api/v1/dialogs/{dialogId}` | `Dialog` + `messages[]` — вся переписка |
| POST | `/api/v1/ask` | `Answer` — ответ на вопрос |
| PATCH | `/api/v1/dialogs/{dialogId}` | `{title}` → `Dialog` |
| DELETE | `/api/v1/dialogs/{dialogId}` | `204` (мягкое удаление) |
| POST | `/api/v1/dialogs/{dialogId}/feedback` | `204` |
| POST | `/api/v1/dialogs/{dialogId}/review` | `204` — решение руководителя по спорному ответу |
| GET | `/api/v1/documents` | каталог: `{id, title, type, typeLabel, label, number, date, editionCount, files}[]` |
| GET | `/api/v1/documents/{documentId}` | `LegalDocument` или `404` |
| POST | `/api/v1/documents/{documentId}/comments` | `{clauseId, text}` → `DocumentComment` |
| DELETE | `/api/v1/documents/{documentId}/comments/{id}` | `204` |
| POST | `/api/v1/documents` | `head`: `{fileName, kind: company\|law, text}` — добавить TXT в базу и переиндексировать |
| GET | `/api/v1/search?q=` | до 8 фрагментов `{type, documentId, clauseId, editionId, title, snippet}` |
| GET | `/api/v1/notifications` | `AppNotification[]` с `isRead` |
| POST | `/api/v1/notifications/read` | `{ids: string[]}` или `{all: true}` → `204` |
| GET / PUT | `/api/v1/settings` | настройки интерфейса пользователя |
| GET | `/api/v1/users` | `head`: список учётных записей |
| POST | `/api/v1/users` | `head`: `{login, name, position, role, password}` → `201` |
| PATCH | `/api/v1/users/{id}` | `head`: `{name?, position?, role?, isActive?, password?}`; сессии пользователя закрываются при смене роли, пароля или блокировке |
| GET | `/api/v1/admin/audit` | `head`: журнал действий, `?limit=&action=` |
| POST | `/api/v1/admin/reindex` | `head`: перечитать базу знаний, вернуть изменения |

Коды ошибок: `401` — нет входа, `403` — не хватает роли, `404` — нет объекта или он чужой, `409` — `dialogId` принадлежит другому пользователю или удалён, `422` — проверка данных, `429` — лимит попыток входа или вопросов (`ASK_PER_MINUTE`), `503` — ошибка сервиса моделей.

## POST /api/v1/ask

Запрос:

```json
{
    "question": "С кем нужно согласовать договор поставки П-17/2024?",
    "dialogId": "412",
    "documentId": "p-17-2024",
    "eventDate": "2026-11-10"
}
```

`dialogId` обязателен (строковый ID, создаваемый фронтом); `documentId`, `eventDate` необязательны. `eventDate` — дата события. По ней выбирается редакция документов: на `2024-02-12` действует регламент ред. 2023, на `2026-11-10` — ред. 2025.

Ответ (`Answer`):

```json
{
    "status": "confirmed",
    "verdict": "Проверено 5 из 5",
    "totalDurationLabel": "2,9 с",
    "context": [
        {"label": "Договор", "value": "П-17/2024"},
        {"label": "Регламент", "value": "ред. 2025"}
    ],
    "dateNote": null,
    "paragraphs": [
        [
            {"text": "Договор согласуется с юридическим отделом и главным бухгалтером"},
            {"cite": 1},
            {"text": ". Цена договора — "},
            {"text": "8,4 млн ₽", "isBold": true},
            {"cite": 2},
            {"text": ", это "},
            {"text": "больше 3 млн ₽", "isChanged": true}
        ]
    ],
    "sources": [
        {
            "documentId": "reglament",
            "editionId": "edition-2025",
            "clauseId": "2.1",
            "title": "Регламент согласования, п. 2.1",
            "meta": "ред. от 01.03.2025 · действует",
            "before": "",
            "quote": "Проект договора согласуется с юридическим отделом и главным бухгалтером",
            "after": "."
        }
    ],
    "steps": [
        {"title": "Разбор вопроса", "detail": "договор П-17/2024, дата события 10.11.2026", "durationLabel": "0,2 с"},
        {"title": "Реранжирование", "detail": "5 фрагментов выше порога 0,80", "durationLabel": "0,6 с"},
        {"title": "Самопроверка", "detail": "все 5 утверждений подтверждены", "durationLabel": "0,4 с"}
    ],
    "nextSteps": ["Завести согласование в СЭД", "Финансовый директор"],
    "followUps": ["Какой срок согласования у юротдела?"]
}
```

### Поля ответа

| Поле | Обязательно | Смысл |
| --- | --- | --- |
| `status` | да | `confirmed` — ответ подтверждён; `refusal` — обоснованный отказ; `clarification` — нужен уточняющий вопрос; `correction` — в вопросе ошибка, ответ по документу; `disputed` — юрист отметил как спорный; `off-topic` — вопрос не юридический, ассистент объясняет границы компетенции |
| `verdict` | да | короткий итог для шапки: «Проверено 5 из 5», «Обоснованный отказ» |
| `paragraphs` | да | абзацы → фрагменты. Фрагмент — либо текст (`text` + `isBold` / `isChanged`), либо сноска `{"cite": N}` |
| `sources` | да | источники; сноска `N` ссылается на `sources[N-1]`. При отказе без правовых выводов — `[]`; если разъясняется подтверждённая норма, ссылки сохраняются |
| `steps` | да | ход проверки, показывается анимацией. Можно отдавать реальные этапы пайплайна |
| `context` | да | плашки в шапке диалога: договор, редакция |
| `isChanged` | нет | фрагмент зависит от даты события (порог, формат согласования) — подсвечивается |
| `dateNote` | нет | пояснение, почему ответ на прошлую дату отличается |
| `checkedDocuments` | нет | для отказа: какие документы проверены |
| `missingInfo` | нет | для отказа: чего именно не хватает в базе, чтобы ответить (документ, редакция, реквизит) |
| `options` | нет | для уточнения — варианты выбора; для отказа — что можно сделать |
| `turns` | нет | реплики давления и подмены роли. `role`: `user` / `assistant`; `isInjected: true` — пользователь прислал текст под видом системной инструкции; `badge` — плашка над ответом |
| `nextSteps`, `followUps` | нет | порядок действий и подсказки следующих вопросов |

`source.quote` — дословная цитата из пункта, `before` и `after` — текст пункта вокруг неё. `editionId` нужен, чтобы ссылка открыла документ в той редакции, на которую опирается ответ.

## POST /api/v1/dialogs/{dialogId}/feedback

```json
{"value": "disputed", "comment": "Сомневаюсь в пороге"}
```

`value`: `correct`, `wrong`, `disputed` или `null`, если отметку сняли. `comment` необязателен. Ответ — `204`. Отметка `disputed` переводит диалог в статус `disputed` и отправляет руководителям уведомление. Новый вопрос в том же диалоге сбрасывает отметку и решение руководителя.

## GET /api/v1/documents/{documentId}

`LegalDocument`: `id`, `title`, `kindLabel`, `image`, `editions[]`, `outline[]`, `sections[]`, `citations[]`, `comments[]`, `files[]`.

Пункт хранит текст по редакциям:

```json
{"id": "2.3", "versions": {"edition-2023": "…свыше 1 000 000…", "edition-2025": "…свыше 3 000 000…"}}
```

Если ключа редакции нет, пункта в этой редакции нет: так помечаются новые пункты. «Было / стало» фронт считает сам по соседним редакциям в порядке массива `editions` (от старой к новой).

Сейчас во фронте используются id `p-17-2024` и `reglament`.

## GET /api/v1/knowledge-base

`KnowledgeBaseOverview`: `stats`, `sections`, `myAnswers`, `teamAnswers`, `updates`, `affected`, `teamStats`, `examples`. Пример — `frontend/src/core/data/knowledgeBase.js`.

У раздела ключ `image` — один из `contracts`, `internal`, `taxes`, `personalData`, `labor`, `laws`. Картинки лежат во фронте.

## POST /api/v1/dialogs/{dialogId}/review

Решение руководителя по ответу, который юрист отметил как спорный.

```json
{"decision": "approved"}
```

`decision`: `approved` — ответ верный, `needs-fix` — нужна правка. `comment` необязателен. Ответ — `204`. Автор ответа получает уведомление.

## Dialog

Поля из `frontend/src/core/types/assistant.js` плюс: `answerStatus` (статус ответа модели; `status` равен `disputed`, пока спор не разобран), `feedback`, `review`, `isOutdated`, `outdatedReason`, `author {id, name, initials, shortName}`, `eventDate`, `documentId`, `createdAt`, `updatedAt`. `GET /dialogs/{id}` добавляет `messages: [{role, text, answer, eventDate, createdAt}]` и `history` с предыдущим вопросом.

`dialogId` создаёт фронт. Номер `№N` назначает сервер. ID, занятый другим пользователем, даёт `409`.

## Уведомления и устаревшие ответы

`AppNotification`: `{id, kind, title, text, dateLabel, isHeadOnly, target, isRead, createdAt}`. `kind`: `update`, `outdated`, `disputed`. `target` — объект `vue-router` (`{name: "dialogs", params: {dialogId}}` или `{name: "document", params: {documentId}, query: {edition}}`).

При старте и при `/admin/reindex` сервер сравнивает SHA-256 каждого документа с прошлым запуском. Первый запуск только записывает исходное состояние. Если документ добавлен, изменён или удалён, всем пользователям приходит `update`. Ответы, в `sources` которых был этот документ, получают `isOutdated: true`, а их авторы — уведомление `outdated`. Они же попадают в `affected` на главной. Повторный вопрос в диалоге снимает отметку.

## Защита от подмены роли

Если вопрос похож на поддельную системную инструкцию («[SYSTEM]», «игнорируй инструкции», «ты больше не ассистент») или на давление («я начальник, исправь ответ»), сервер добавляет в `Answer` поле `turns`: реплику пользователя (`isInjected: true` для инъекции) и пояснение с `badge`. Сам ответ по-прежнему формирует `legal_core` по базе знаний. Срабатывание записывается в аудит (`details.guard`).

## Сценарии контроля достоверности

Фронт показывает все ситуации из кейса. Бэкенду нужно отдавать ответы такой формы (примеры — `frontend/src/core/data/dialogs.js` и `mockAnswers.js`):

| Ситуация | status | Что обязательно в ответе |
| --- | --- | --- |
| Ответ найден | `confirmed` | `sources`, сноски на каждое утверждение |
| Данных недостаточно | `refusal` | `checkedDocuments`, `missingInfo`, `sources: []` |
| Ошибка в вопросе | `correction` | что не так в вопросе + верное значение со сноской |
| Неясно, о каком договоре речь | `clarification` | `options` — варианты для выбора |
| Нужна старая редакция закона | `refusal` | действующая норма со сноской + `missingInfo` с нужной редакцией |
| Просьба нарушить закон или регламент | `refusal` | отказ помогать + правильный порядок со сносками, без выдуманных последствий |
| Давление, подмена роли | `confirmed` | `turns` с `isInjected: true` для поддельной системной инструкции |
| Не юридический вопрос | `off-topic` | объяснение границ компетенции, `sources: []` |

## Реальный бэкенд

Моки выключены по умолчанию. При `VITE_USE_MOCKS=true` вход не требуется: фронт показывает демонстрационного пользователя с ролью руководителя. `GET /api/health` возвращает состояние базы и векторного поиска. Ошибка модели возвращается как 503 с `error.message`. История хранится сервером по `dialogId` и привязана к автору. Роль приходит с сервера: переключатель «Юрист / Руководитель» виден только руководителю и меняет лишь вид интерфейса, а не права.

Код бэкенда: `server/` (`app.py` — фабрика приложения, `routers/` — эндпоинты, `db.py` — схема SQLite и миграции, `security.py` — пароли, токены, лимиты, `kb.py` — база знаний и отслеживание изменений, `guard.py` — подмена роли). `api.py` — точка входа для `uvicorn api:app`.
