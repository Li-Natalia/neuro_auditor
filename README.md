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
.\.venv\Scripts\Activate.ps1      # Windows PowerShell
pip install -r requirements.txt
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
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

## Тесты
```bash
cd backend
pytest
```

## Лицензия
MIT
