import logging
import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, field_validator


load_dotenv(dotenv_path="../.env", override=False)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


TEXT_TYPES = [
    "Telegram-пост",
    "VK-пост",
    "Описание услуги",
    "Продающее сообщение",
    "Прогревающий пост",
]

TONES = [
    "Экспертный",
    "Теплый",
    "Мягко-продающий",
]

LENGTHS = [
    "Короткий",
    "Средний",
    "Длинный",
]


class GenerateRequest(BaseModel):
    business_niche: str = Field(..., min_length=1)
    product: str = Field(..., min_length=1)
    target_audience: str = Field(..., min_length=1)
    text_type: Literal[
        "Telegram-пост",
        "VK-пост",
        "Описание услуги",
        "Продающее сообщение",
        "Прогревающий пост",
    ]
    tone: Literal["Экспертный", "Теплый", "Мягко-продающий"]
    length: Literal["Короткий", "Средний", "Длинный"]
    prompt: str = Field(..., min_length=1)

    @field_validator("business_niche", "product", "target_audience", "prompt")
    @classmethod
    def not_empty_after_strip(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            msg = "Значение не может быть пустой строкой."
            raise ValueError(msg)
        return stripped


class GenerateResponse(BaseModel):
    result: str


app = FastAPI(
    title="Neuro Copywriter API",
    description="MVP backend для генерации черновиков текста.",
)

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _build_mock_result(payload: GenerateRequest) -> str:
    title_intro = (
        f"{payload.text_type} для ниши "
        f"«{payload.business_niche}» и продукта "
        f"«{payload.product}»"
    )

    titles = [
        f"{payload.product}: мягкий путь к балансу для "
        f"«{payload.target_audience}»",
        f"Как {payload.target_audience} могут поддержать "
        f"ресурс тела через {payload.product}",
        f"{payload.text_type}: внимательный взгляд на "
        f"здоровье без обещаний чудес",
    ]

    tone_note_map = {
        "Экспертный": (
            "Текст спокойный, опирается на опыт, объясняет логику "
            "подхода без запугивания и громких обещаний."
        ),
        "Теплый": (
            "Текст поддерживающий, с фокусом на заботе, принятии и "
            "бережном отношении к телу."
        ),
        "Мягко-продающий": (
            "Текст приглашает к следующему шагу без давления, "
            "подчеркивает выбор и свободу клиента."
        ),
    }

    length_note_map = {
        "Короткий": "Сделай текст компактным, ближе к анонсу.",
        "Средний": "Сделай текст развёрнутым, но без лишней воды.",
        "Длинный": "Сделай текст подробным, с пояснениями и примерами.",
    }

    tone_note = tone_note_map.get(payload.tone, "")
    length_note = length_note_map.get(payload.length, "")

    main_body = (
        "Основной текст:\n"
        f"- Объясни, с какими типичными состояниями сталкивается "
        f"аудитория «{payload.target_audience}».\n"
        "- Опиши, как можно мягко поддержать ресурс тела, "
        "не обещая лечения и точных диагнозов.\n"
        f"- Покажи роль продукта «{payload.product}» как инструмента "
        "поддержки, а не волшебной таблетки.\n"
        "- Избегай категоричных формулировок и пугающих описаний.\n"
    )

    ctas = [
        "Если откликается, можно записаться на консультацию — "
        "в своём темпе, без спешки.",
        "Если хочется разобраться глубже, можно задать вопросы "
        "в личные сообщения.",
        "Если чувствуете, что время для следующего шага пришло, "
        "можно оставить заявку на разбор ситуации.",
    ]

    disclaimer = (
        "Важно:\n"
        "- Этот текст не заменяет консультацию врача, диагностику "
        "или лечение.\n"
        "- Любые рекомендации носят общий, ознакомительный характер.\n"
        "- При любых подозрениях на заболевания обращайтесь к "
        "квалифицированным специалистам.\n"
    )

    result_parts = [
        f"Заголовки (3 варианта):\n- {titles[0]}\n- {titles[1]}\n- "
        f"{titles[2]}\n",
        f"{main_body}\n{tone_note}\n{length_note}\n",
        "Мягкие CTA (3 варианта):\n"
        f"- {ctas[0]}\n- {ctas[1]}\n- {ctas[2]}\n",
        disclaimer,
    ]

    return "\n".join(result_parts)


def _is_real_api_configured() -> bool:
    api_key = os.getenv("OPENAI_API_KEY")
    return bool(api_key)


@app.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest) -> GenerateResponse:
    try:
        payload = GenerateRequest.model_validate(payload)
    except ValidationError as exc:
        logger.info("Validation error on /generate request.")
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    if _is_real_api_configured():
        logger.info(
            "OPENAI_API_KEY найден. Используется mock-ответ. "
            "Реальная интеграция с API может быть добавлена "
            "в отдельной feature-ветке.",
        )

    result_text = _build_mock_result(payload)

    return GenerateResponse(result=result_text)
