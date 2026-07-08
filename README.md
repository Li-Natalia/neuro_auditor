Веб-приложение для аудита и анализа финансовой отчетности

https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white
https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white
https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white

📋 О проекте
neuro_auditor — это интеллектуальная платформа для автоматизированного аудита и анализа финансовой отчетности. Приложение позволяет загружать Excel-отчеты (МСФО/РСБУ), проводить комплексный финансовый анализ, выявлять риски и получать контекстные ответы на вопросы через AI-чат-бот.

✨ Ключевые возможности
🔐 Аутентификация и роли — JWT-аутентификация с тремя ролями: Администратор, Аудитор, Просмотр

📤 Загрузка отчетности — Drag-and-drop загрузка Excel-файлов с поддержкой шаблонов МСФО и РСБУ

📊 Автоматический финансовый анализ — Расчет ключевых показателей с текстовым резюме

⚠️ Выявление рисков — Автоматическая классификация рисков по уровням с рекомендациями

📈 Визуализация — Интерактивные графики, тепловая карта рисков и дашборд со статистикой

🤖 AI-чат-бот — Контекстные ответы по документам с историей сессий

📄 PDF-отчеты — Автоматическая генерация PDF с результатами анализа

🎨 Современный UI — Светлая/темная темы, адаптивный дизайн

🏗️ Технологический стек
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
Python 3.10+	Язык программирования
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
1. Переменные окружения
bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
2. Запуск через Docker (рекомендуется)
bash
docker compose up --build
Сервис	URL
Frontend	http://localhost:5173
Backend (Swagger UI)	http://localhost:8000/docs
Backend (ReDoc)	http://localhost:8000/redoc
