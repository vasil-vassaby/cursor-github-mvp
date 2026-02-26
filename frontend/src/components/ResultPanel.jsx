export function ResultPanel({
    loading,
    error,
    result,
    onResultChange,
    onCopy,
    showDebug,
    debugPrompt,
    onClear,
}) {
    const handleCopyResult = () => {
        if (!result) {
            return;
        }
        navigator.clipboard
            .writeText(result)
            .then(onCopy)
            .catch(() => {
                // Ошибку копирования не пробрасываем вверх, чтобы не
                // ломать UX, можно при желании добавить отдельное сообщение.
            });
    };

    const handleClear = () => {
        if (onClear) {
            onClear();
        }
    };

    const handleCopyPrompt = () => {
        if (!debugPrompt) {
            return;
        }
        navigator.clipboard.writeText(debugPrompt).catch(() => undefined);
    };

    return (
        <section className="card result-panel">
            <h2>Результат</h2>

            {loading && <p>Генерируем черновик текста...</p>}

            {error && <p className="error-text">{error}</p>}

            <textarea
                rows={14}
                value={result}
                onChange={(event) => onResultChange(event.target.value)}
                placeholder="Здесь появится черновик текста. Вы сможете отредактировать его под себя."
            />

            <div className="result-actions">
                <button
                    type="button"
                    className="secondary-button"
                    onClick={handleCopyResult}
                    disabled={!result}
                >
                    Копировать текст
                </button>
                <button
                    type="button"
                    className="ghost-button"
                    onClick={handleClear}
                    disabled={!result}
                >
                    Очистить текст
                </button>
            </div>

            {showDebug && (
                <div className="debug-block">
                    <div className="debug-header">
                        <h3>Debug: использованный промпт</h3>
                        <button
                            type="button"
                            className="ghost-button"
                            onClick={handleCopyPrompt}
                            disabled={!debugPrompt}
                        >
                            Копировать промпт
                        </button>
                    </div>
                    <pre className="debug-content">{debugPrompt}</pre>
                </div>
            )}
        </section>
    );
}
