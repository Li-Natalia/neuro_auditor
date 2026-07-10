# Нейроаудитор

Аудит и анализ финансовой отчетности: загрузка Excel-отчетов (МСФО/РСБУ),
автоматический финансовый анализ, выявление рисков, дашборд и AI-чат-бот по документам.

## Технологический стек

**Frontend:** React 18 + TypeScript, Vite, Material-UI v5, Zustand, React Hook Form + Zod,
Axios, React Router v6, MUI Data Grid, Recharts, Emotion.

**Backend:** FastAPI (Python 3.10+), PostgreSQL + Redis, SQLAlchemy 2.0 + Alembic,
Pandas + OpenPyXL, JWT + OAuth2, Celery, Transformers/spaCy.

## Структура

```
нейроаудитор/
├── frontend/          # React приложение (Vite)
├── backend/           # FastAPI приложение
├── scripts/           # Вспомогательные скрипты (ярлык для запуска и т.д.)
├── docker-compose.yml
├── .env.example
└── README.md
```

## Быстрый старт

### 1. Переменные окружения
```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Docker (рекомендуется)
```bash
docker compose up --build
```
- Frontend: http://localhost:5173
- Backend (Swagger UI): http://localhost:8000/docs

### 3. Локальная разработка

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
.\.venv\Scripts\Activate.ps1       # Windows PowerShell
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --reload      # схема БД накатывается автоматически при старте (alembic upgrade head)
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Основной функционал

- Аутентификация (JWT), роли: Админ, Аудитор, Просмотр
- Загрузка Excel (drag-and-drop), шаблоны МСФО/РСБУ, валидация, прогресс
- Анализ отчетности: баланс, ОПУ, ОДДС, финансовые коэффициенты (ликвидность,
  рентабельность ROA/ROE/ROS, оборачиваемость, устойчивость)
- Выявление рисков: критические / средние / низкие с комментариями
- Визуализация (графики, диаграммы), генерация PDF-отчета
- Чат-бот по документам (NLP, контекстные ответы, история сессий)
- Дашборд: статистика, тренды, тепловая карта рисков

## Чат-бот и LLM (Yandex Cloud)

Чат-бот отвечает через LLM, когда провайдер настроен, иначе — через
встроенный rule-based ответчик по финансовым показателям документа (приложение
полностью работает и без ключей). Провайдер выбирается настройкой `AI_PROVIDER`:

| `AI_PROVIDER` | Поведение |
|---------------|-----------|
| `auto` (по умолчанию) | YandexGPT, если задан; иначе OpenAI; иначе rule-based |
| `yandex` | Только YandexGPT |
| `openai` | Только OpenAI |
| `rule`   | Только rule-based (без внешних вызовов) |

### YandexGPT (Yandex Cloud Foundation Models)

Интеграция использует OpenAI-совместимый эндпоинт Yandex Cloud
(OpenAI SDK + заголовок `x-folder-id`).

```env
AI_PROVIDER=yandex
AI_BASE_URL=https://llm.api.cloud.yandex.net/v1
AI_YC_API_KEY=<API-ключ сервисного аккаунта Yandex Cloud>
AI_YC_FOLDER_ID=<ID каталога>
AI_MODEL=yandexgpt/latest          # или yandexgpt-lite/latest; либо полный gpt://<folder>/<model>
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=2000
```

Как получить ключи (переменные — в `backend/.env`):
1. Активируйте платёжный аккаунт в Yandex Cloud.
2. Создайте сервисный аккаунт с ролью `ai.languageModels.user`.
3. Выпустите для него **API-ключ** (именно API-ключ, не «статический ключ доступа») → `AI_YC_API_KEY`.
4. `AI_YC_FOLDER_ID` — ID каталога, **в котором создан этот сервисный аккаунт**
   (иначе Yandex вернёт 403 «folder does not match service account folder»).

Пакет `openai` входит в основной `requirements.txt` (лёгкая зависимость) —
тяжёлый локальный ML-стек (`requirements-ai.txt`) для LLM-чата не нужен.
Любая ошибка обращения к LLM мягко переходит к rule-based ответу.

## Тесты
```bash
cd backend
pytest
```

## Лицензия
MIT
