"""Detects user messages that impersonate system instructions or pressure the assistant.

The answering prompt in legal_core already treats every user message as untrusted data.
This module only makes such attempts visible in the interface (Answer.turns) and in audit.
"""
from __future__ import annotations

import re

INJECTION = [
    r"\[\s*(system|систем\w*|admin|developer)\s*\]",
    r"^\s*(system|систем\w*\s+сообщени\w*|системн\w+\s+инструкци\w*)\s*:",
    r"<\|?\s*(im_start|system)\s*\|?>",
    r"(игнорируй|забудь|отмени)\w*\s+(все\s+)?(предыдущ\w+|прежн\w+|сво\w+|системн\w+)?\s*(инструкци|правил|ограничени|промпт|промт)",
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|rules)",
    r"(ты\s+(больше\s+не|теперь\s+не)\s+(юридическ\w+\s+)?ассистент)",
    r"(новая|новые)\s+(роль|инструкци\w*|системн\w+)",
    r"(режим|mode)\s+(разработчика|администратора|developer|dan|jailbreak)",
    r"(выйди|выход)\s+из\s+роли",
    r"(покажи|выведи|раскрой)\s+(свой\s+)?(системн\w+\s+)?(промпт|промт|инструкци\w*)",
]

PRESSURE = [
    r"я\s+(начальник|руководител\w+|директор|глава)\b.*\b(исправ|измени|подтверди|перепиши)",
    r"(исправь|измени|перепиши)\s+(свой\s+)?(ответ|вывод)",
    r"(ты\s+ошибаешься|это\s+неправильно).*(подтверди|согласись)",
    r"(сроки\s+горят|под\s+мою\s+ответственность|я\s+разрешаю)",
]

_injection = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in INJECTION]
_pressure = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in PRESSURE]


def classify(question: str) -> str | None:
    if any(p.search(question) for p in _injection):
        return "injection"
    if any(p.search(question) for p in _pressure):
        return "pressure"
    return None


def annotate(answer: dict, question: str, kind: str | None) -> dict:
    """Adds an explanatory exchange for the chat view without touching the grounded answer."""
    if kind is None:
        return answer
    sources = len(answer.get("sources", []))
    if kind == "injection":
        badge = "Роль сохранена"
        text = ("Сообщение похоже на системную инструкцию, но пришло в пользовательском вводе, "
                "поэтому как инструкция не выполняется. Ответ ниже сформирован только по базе знаний.")
    else:
        badge = f"Ответ не изменён · {sources} {_plural(sources, 'источник', 'источника', 'источников')}"
        text = ("Вывод опирается на найденные положения базы знаний и не меняется по просьбе без нового документа. "
                "Если есть документ, который меняет порядок, загрузите его в базу или сошлитесь на него.")
    answer["turns"] = [
        {"role": "user", "text": question[:2000], "isInjected": kind == "injection"},
        {"role": "assistant", "badge": badge, "text": text},
    ]
    return answer


def _plural(n: int, one: str, few: str, many: str) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many
