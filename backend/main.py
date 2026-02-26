import logging
import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
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
    titles = [
        (
            f"{payload.product}: мягкий путь к балансу для "
            f"«{payload.target_audience}»"
        ),
        (
            f"Как аудитория «{payload.target_audience}» может мягко "
            f"поддержать ресурс тела через {payload.product}"
        ),
        (
            f"{payload.text_type}: внимательный взгляд на здоровье "
            "без обещаний чудес"
        ),
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
        "Короткий": "Текст компактный, ближе к анонсу.",
        "Средний": "Текст развёрнутый, но без лишней воды.",
        "Длинный": "Текст подробный, с несколькими подзаголовками.",
    }

    tone_note = tone_note_map.get(payload.tone, "")
    length_note = length_note_map.get(payload.length, "")

    main_body = (
        "Основной текст (1 версия):\n"
        f"Подзаголовок: с чем приходит аудитория «{payload.target_audience}»\n"
        "- Опиши несколько типичных состояний и запросов этой "
        "аудитории простым, понятным языком.\n\n"
        "Подзаголовок: как мягко поддержать ресурс тела\n"
        "- Покажи, какие бережные шаги может сделать человек, "
        "избегая самообвинения и крайностей.\n\n"
        f"Подзаголовок: роль продукта «{payload.product}»\n"
        "- Объясни, как продукт может поддерживать ресурс тела "
        "и повседневное самочувствие, но не является лечением, "
        "диагностикой или гарантией результата.\n\n"
        "Подзаголовок: реалистичные ожидания\n"
        "- Помоги читателю настроиться на постепенные изменения "
        "и бережный подход к себе, без обещаний «минус все "
        "симптомы за неделю».\n\n"
        f"{tone_note}\n"
        f"{length_note}\n"
    )

    ctas = [
        (
            "Если откликается и хочется мягко продолжить, можно "
            "записаться на консультацию в удобное время — без спешки "
            "и давления."
        ),
        (
            "Если хочется задать уточняющие вопросы, можно написать "
            "в личные сообщения и обсудить, подойдёт ли вам формат "
            f"«{payload.product}»."
        ),
        (
            "Если чувствуете, что время для следующего шага пришло, "
            "можно оставить запрос на бережный разбор вашей ситуации."
        ),
    ]

    disclaimer = (
        "Важно:\n"
        "- Этот текст не заменяет консультацию врача, диагностику или "
        "лечение и не ставит диагнозов.\n"
        "- Любые примеры и рекомендации носят общий, ознакомительный "
        "характер — при серьёзных симптомах важно обратиться к "
        "квалифицированному специалисту.\n"
    )

    result_parts = [
        (
            "Заголовки (3 варианта):\n"
            f"- {titles[0]}\n"
            f"- {titles[1]}\n"
            f"- {titles[2]}\n"
        ),
        f"{main_body}\n{tone_note}\n{length_note}\n",
        "Мягкие CTA (3 варианта):\n"
        f"- {ctas[0]}\n- {ctas[1]}\n- {ctas[2]}\n",
        disclaimer,
    ]

    return "\n".join(result_parts)


def _is_real_api_configured() -> bool:
    api_key = os.getenv("OPENAI_API_KEY")
    return bool(api_key)


def _get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        msg = "OPENAI_API_KEY is not configured."
        raise RuntimeError(msg)

    base_url = os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"

    timeout_env = os.getenv("OPENAI_TIMEOUT_SECONDS")
    timeout = 30.0
    if timeout_env:
        try:
            timeout = float(timeout_env)
        except ValueError:
            logger.warning(
                "Invalid OPENAI_TIMEOUT_SECONDS value. "
                "Fallback to default 30 seconds.",
            )

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
    )
    return client


def _get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL") or "gpt-4o-mini"


def _get_openai_temperature() -> float:
    temperature_env = os.getenv("OPENAI_TEMPERATURE")
    if not temperature_env:
        return 0.7
    try:
        return float(temperature_env)
    except ValueError:
        logger.warning(
            "Invalid OPENAI_TEMPERATURE value. Fallback to default 0.7.",
        )
        return 0.7


def generate_with_openai(prompt: str) -> str:
    client = _get_openai_client()
    model = _get_openai_model()
    temperature = _get_openai_temperature()

    system_prompt = (
        "Ты помогаешь экспертам по здоровью, телесным практикам и ТКМ "
        "писать бережные, понятные тексты. Не ставь диагнозы, не давай "
        "гарантий излечения и не обещай чудесных результатов. Напоминай, "
        "что текст не заменяет консультацию врача и диагностику, но делай "
        "это мягко, без запугивания."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("OpenAI chat completion failed: %s", exc)
        raise

    choice = response.choices[0]
    content = choice.message.content or ""
    return content


@app.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest) -> GenerateResponse:
    try:
        payload = GenerateRequest.model_validate(payload)
    except ValidationError as exc:
        logger.info("Validation error on /generate request.")
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    if not _is_real_api_configured():
        result_text = _build_mock_result(payload)
        return GenerateResponse(result=result_text)

    try:
        ai_text = generate_with_openai(payload.prompt)
        return GenerateResponse(result=ai_text)
    except Exception:  # noqa: BLE001
        logger.warning(
            "Falling back to mock result after AI provider error.",
        )
        mock_text = _build_mock_result(payload)
        prefix = (
            "(!) Не удалось получить ответ от AI‑провайдера, ниже "
            "приведён mock‑черновик на основе ваших данных.\n\n"
        )
        return GenerateResponse(result=f"{prefix}{mock_text}")
