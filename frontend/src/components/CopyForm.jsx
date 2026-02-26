import { useState } from "react";
import { buildPrompt } from "../utils/buildPrompt";

const INITIAL_STATE = {
    businessNiche: "",
    product: "",
    targetAudience: "",
    textType: "Telegram-пост",
    tone: "Экспертный",
    length: "Средний",
    debug: false,
};

export function CopyForm({ onSubmit, onReset }) {
    const [form, setForm] = useState(INITIAL_STATE);
    const [touched, setTouched] = useState({});

    const handleChange = (event) => {
        const { name, value, type, checked } = event.target;
        setForm((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value,
        }));
    };

    const handleBlur = (event) => {
        const { name } = event.target;
        setTouched((prev) => ({ ...prev, [name]: true }));
    };

    const isEmpty = (value) => !value || value.trim().length === 0;

    const errors = {
        businessNiche: isEmpty(form.businessNiche)
            ? "Пожалуйста, укажите нишу/тематику."
            : "",
        product: isEmpty(form.product)
            ? "Пожалуйста, укажите продукт или услугу."
            : "",
        targetAudience: isEmpty(form.targetAudience)
            ? "Пожалуйста, опишите целевую аудиторию."
            : "",
    };

    const isValid =
        !errors.businessNiche && !errors.product && !errors.targetAudience;

    const handleSubmit = (event) => {
        event.preventDefault();
        setTouched({
            businessNiche: true,
            product: true,
            targetAudience: true,
        });
        if (!isValid) {
            return;
        }

        const prompt = buildPrompt({
            businessNiche: form.businessNiche,
            product: form.product,
            targetAudience: form.targetAudience,
            textType: form.textType,
            tone: form.tone,
            length: form.length,
        });

        onSubmit({
            business_niche: form.businessNiche.trim(),
            product: form.product.trim(),
            target_audience: form.targetAudience.trim(),
            text_type: form.textType,
            tone: form.tone,
            length: form.length,
            prompt,
            debug: form.debug,
        });
    };

    const handleReset = () => {
        setForm(INITIAL_STATE);
        setTouched({});
        if (onReset) {
            onReset();
        }
    };

    return (
        <form onSubmit={handleSubmit} className="card">
            <div className="field">
                <label htmlFor="businessNiche">Ниша / тематика бизнеса*</label>
                <input
                    id="businessNiche"
                    name="businessNiche"
                    type="text"
                    value={form.businessNiche}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="Например: ТКМ, ресурс тела, работа со сном"
                />
                {touched.businessNiche && errors.businessNiche && (
                    <p className="error-text">{errors.businessNiche}</p>
                )}
            </div>

            <div className="field">
                <label htmlFor="product">Продукт / услуга*</label>
                <input
                    id="product"
                    name="product"
                    type="text"
                    value={form.product}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="Например: разбор по ТКМ, мини-курс, консультация"
                />
                {touched.product && errors.product && (
                    <p className="error-text">{errors.product}</p>
                )}
            </div>

            <div className="field">
                <label htmlFor="targetAudience">Целевая аудитория*</label>
                <textarea
                    id="targetAudience"
                    name="targetAudience"
                    rows={3}
                    value={form.targetAudience}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="Кто эти люди? С чем они часто приходят? Например: женщины 30–45 с утренними отёками и нарушенным сном."
                />
                {touched.targetAudience && errors.targetAudience && (
                    <p className="error-text">{errors.targetAudience}</p>
                )}
            </div>

            <div className="field-row">
                <div className="field">
                    <label htmlFor="textType">Тип текста</label>
                    <select
                        id="textType"
                        name="textType"
                        value={form.textType}
                        onChange={handleChange}
                    >
                        <option>Telegram-пост</option>
                        <option>VK-пост</option>
                        <option>Описание услуги</option>
                        <option>Продающее сообщение</option>
                        <option>Прогревающий пост</option>
                    </select>
                </div>

                <div className="field">
                    <label htmlFor="tone">Тон</label>
                    <select
                        id="tone"
                        name="tone"
                        value={form.tone}
                        onChange={handleChange}
                    >
                        <option>Экспертный</option>
                        <option>Теплый</option>
                        <option>Мягко-продающий</option>
                    </select>
                </div>

                <div className="field">
                    <label htmlFor="length">Длина</label>
                    <select
                        id="length"
                        name="length"
                        value={form.length}
                        onChange={handleChange}
                    >
                        <option>Короткий</option>
                        <option>Средний</option>
                        <option>Длинный</option>
                    </select>
                </div>
            </div>

            <label className="checkbox">
                <input
                    type="checkbox"
                    name="debug"
                    checked={form.debug}
                    onChange={handleChange}
                />
                <span>Показать промпт (debug mode)</span>
            </label>

            <div className="form-actions">
                <button
                    type="submit"
                    className="primary-button"
                    disabled={!isValid}
                >
                    Сгенерировать
                </button>
                <button
                    type="button"
                    className="ghost-button"
                    onClick={handleReset}
                >
                    Очистить форму
                </button>
            </div>
            {!isValid && (
                <p className="error-text form-error">
                    Заполните все обязательные поля, чтобы запустить
                    генерацию текста.
                </p>
            )}
        </form>
    );
}
