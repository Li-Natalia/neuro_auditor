# neuro_auditor
neuro-auditor
Веб-приложение для аудита и анализа финансовой отчетности: загрузка Excel-отчётов (МСФО/РСБУ), автоматический финансовый анализ, выявление рисков, интерактивный дашборд и AI-чат-бот по документам.

Возможности
Аутентификация и роли. JWT-аутентификация с тремя ролями: Администратор, Аудитор, Просмотр.
Загрузка отчётности. Drag-and-drop загрузка Excel-файлов (.xlsx, .xls) с поддержкой шаблонов МСФО и РСБУ, валидацией, прогрессом загрузки и ограничением размера.
Автоматический финансовый анализ. Разбор баланса, отчёта о прибылях и убытках (ОПУ) и расчёт ключевых показателей:
Ликвидность: текущая ликвидность, быстрая ликвидность
Рентабельность: ROA, ROE, ROS
Оборачиваемость активов
Долговая нагрузка (Debt-to-Equity)
Текстовое резюме финансового состояния
Выявление рисков. Автоматическая классификация рисков по уровням — критические, средние, низкие — с описанием проблемы и рекомендациями по каждому показателю (ликвидность, долги, убыточность, отрицательный капитал, дебиторская задолженность).
Визуализация. Интерактивные графики и диаграммы, тепловая карта рисков, дашборд со статистикой.
AI-чат-бот по документам. Контекстные ответы на вопросы по загруженной отчётности, история сессий, подсказанные вопросы. Поддержка локальных NLP-моделей (spaCy) и интеграция с OpenAI (опционально).
PDF-отчёты. Автоматическая генерация PDF-отчёта с результатами анализа и рисками.
Дашборд. Сводная статистика, недавние отчёты, быстрый доступ к анализу.
Технологический стек
Frontend
Технология	Назначение
React 18 + TypeScript	UI-фреймворк
Vite 5	Сборка и dev-сервер
Material-UI v5	Компонентная библиотека
Zustand	Управление состоянием
React Router v6	Маршрутизация
React Hook Form + Zod	Формы и валидация
MUI X Data Grid	Таблицы данных
Recharts	Графики и диаграммы
Axios	HTTP-клиент
Backend
Технология	Назначение
FastAPI	Web-фреймворк
Python 3.10+	Язык
PostgreSQL + asyncpg	База данных
SQLAlchemy 2.0 (async)	ORM
Alembic	Миграции
Redis	Кэш, брокер сообщений
Celery	Фоновые задачи
Pandas + OpenPyXL	Парсинг Excel
python-jose + passlib	JWT, хеширование паролей
ReportLab	Генерация PDF
Инфраструктура
Docker Compose — оркестрация всех сервисов
Сервисы: PostgreSQL, Redis, Backend (FastAPI), Celery Worker, Frontend (Vite)
Архитектура
нейроаудитор/
├── frontend/              # React + TypeScript приложение
│   ├── src/
│   │   ├── api/           # API-клиенты (Axios)
│   │   ├── components/     # Переиспользуемые компоненты
│   │   ├── pages/          # Страницы приложения
│   │   ├── store/          # Zustand-хранилища (auth, chat, analysis...)
│   │   ├── hooks/          # Кастомные хуки
│   │   ├── themes/         # Светлая/тёмная темы
│   │   ├── routes/         # Защищённые маршруты
│   │   └── utils/          # Утилиты, константы, валидаторы
│   └── Dockerfile
│
├── backend/               # FastAPI приложение
│   ├── app/
│   │   ├── api/            # REST-маршруты + middleware
│   │   ├── core/           # Конфигурация, БД, безопасность
│   │   ├── models/         # SQLAlchemy-модели
│   │   ├── schemas/        # Pydantic-схемы
│   │   ├── services/       # Бизнес-логика
│   │   ├── processors/     # Финансовый и риск-анализ
│   │   ├── ai/             # NLP/чат-бот (spaCy, embeddings)
│   │   ├── tasks/          # Celery-задачи
│   │   ├── alembic/        # Миграции БД
│   │   └── utils/          # Валидаторы, PDF-генератор
│   ├── tests/              # Unit + интеграционные тесты
│   └── Dockerfile
│
├── scripts/               # Вспомогательные скрипты
├── docker-compose.yml
└── .env.example
Быстрый старт
1. Переменные окружения
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
2. Запуск через Docker (рекомендуется)
docker compose up --build
Сервис	URL
Frontend	http://localhost:5173
Backend (Swagger UI)	http://localhost:8000/docs
Backend (ReDoc)	http://localhost:8000/redoc
3. Локальная разработка
Backend:

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
Frontend:

cd frontend
npm install
npm run dev
API
Полная интерактивная документация API доступна после запуска:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
Основные эндпоинты:

Метод	Путь	Описание
POST	/api/auth/register	Регистрация
POST	/api/auth/login	Вход
POST	/api/auth/refresh	Обновление токена
GET	/api/auth/me	Текущий пользователь
POST	/api/documents/upload	Загрузка Excel
GET	/api/documents	Список документов
GET	/api/analysis	Список анализов
GET	/api/analysis/{id}	Детали анализа + риски
GET	/api/reports/{id}/pdf	Скачивание PDF-отчёта
POST	/api/chat/sessions	Новая сессия чат-бота
POST	/api/chat/messages	Вопрос чат-боту
Анализируемые финансовые показатели
Показатель	Формула	Норматив
Текущая ликвидность	Оборотные активы / Краткосрочные обязательства	≥ 1.5
Быстрая ликвидность	(Оборотные активы − Запасы) / Краткосрочные обязательства	≥ 1.0
ROA	Чистая прибыль / Активы × 100%	> 0
ROE	Чистая прибыль / Капитал × 100%	> 0
ROS	Операционная прибыль / Выручка × 100%	> 0
Debt-to-Equity	Обязательства / Капитал	≤ 1.0
Оборачиваемость активов	Выручка / Активы	—
Тесты
cd backend
pytest
Покрытие: финансовый анализатор, риск-анализатор, безопасность (JWT, пароли), NLP-пайплайн, чат-бот, интеграционные тесты API.

Доступные команды
Frontend:

Команда	Описание
npm run dev	Dev-сервер
npm run build	Production-сборка
npm run lint	ESLint-проверка
npm run typecheck	TypeScript-проверка
npm run format	Prettier-форматирование
