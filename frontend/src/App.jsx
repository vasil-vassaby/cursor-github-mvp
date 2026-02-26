import { useState } from "react";
import { CopyForm } from "./components/CopyForm";
import { ResultPanel } from "./components/ResultPanel";

const API_URL =
    import.meta.env.VITE_API_URL || "http://localhost:8000";

export function App() {
    const [result, setResult] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [debugPrompt, setDebugPrompt] = useState("");
    const [showDebug, setShowDebug] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleSubmit = async (payload) => {
        setLoading(true);
        setError("");
        setCopied(false);
        setResult("");
        setDebugPrompt(payload.prompt);
        setShowDebug(payload.debug);

        try {
            const response = await fetch(`${API_URL}/generate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    business_niche: payload.business_niche,
                    product: payload.product,
                    target_audience: payload.target_audience,
                    text_type: payload.text_type,
                    tone: payload.tone,
                    length: payload.length,
                    prompt: payload.prompt,
                }),
            });

            if (!response.ok) {
                const contentType =
                    response.headers.get("Content-Type") || "";

                if (contentType.includes("application/json")) {
                    const data = await response.json();
                    if (Array.isArray(data.detail)) {
                        throw new Error(
                            "Некоторые поля заполнены некорректно. " +
                                "Проверьте, что форма заполнена верно.",
                        );
                    }
                    throw new Error(
                        typeof data.detail === "string"
                            ? data.detail
                            : "Не удалось сгенерировать текст.",
                    );
                }

                throw new Error("Не удалось сгенерировать текст.");
            }

            const data = await response.json();
            setResult(data.result || "");
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Произошла неизвестная ошибка.",
            );
        } finally {
            setLoading(false);
        }
    };

    const handleResultChange = (value) => {
        setResult(value);
    };

    const handleCopy = () => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleReset = () => {
        setResult("");
        setError("");
        setDebugPrompt("");
        setShowDebug(false);
        setCopied(false);
    };

    const handleClearResult = () => {
        setResult("");
        setCopied(false);
    };

    return (
        <div className="page">
            <header className="page-header">
                <h1>Нейро-копирайтер для экспертного бизнеса</h1>
                <p>
                    Генерация черновиков контента для эксперта в нише
                    здоровья (ТКМ, ресурс тела и др.).
                </p>
            </header>

            <main className="layout">
                <div className="layout-main">
                    <CopyForm onSubmit={handleSubmit} onReset={handleReset} />
                </div>
                <div className="layout-side">
                    <ResultPanel
                        loading={loading}
                        error={error}
                        result={result}
                        onResultChange={handleResultChange}
                        onCopy={handleCopy}
                        showDebug={showDebug}
                        debugPrompt={debugPrompt}
                        onClear={handleClearResult}
                    />
                    {copied && (
                        <p className="hint">
                            Текст скопирован в буфер обмена.
                        </p>
                    )}
                </div>
            </main>

            <section className="card how-to">
                <h2>Как пользоваться</h2>
                <ol>
                    <li>Заполните нишу, продукт и целевую аудиторию.</li>
                    <li>Выберите тип текста, тон и длину.</li>
                    <li>
                        При желании включите{" "}
                        <strong>debug mode</strong>, чтобы увидеть
                        промпт.
                    </li>
                    <li>Нажмите «Сгенерировать» и дождитесь результата.</li>
                    <li>
                        Отредактируйте текст под свой голос и скопируйте
                        его.
                    </li>
                </ol>
            </section>

            <section className="card examples">
                <h2>Примеры тем для Ксении / ТКМ</h2>
                <ul>
                    <li>Утренние отёки и работа с лимфой.</li>
                    <li>Пробуждения в 3–4 утра и ресурс печени.</li>
                    <li>Хруст коленей после 40 и мягкая поддержка суставов.</li>
                    <li>Anti-age через ресурс тела, а не насилие над собой.</li>
                </ul>
            </section>
        </div>
    );
}
