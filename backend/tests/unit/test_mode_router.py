"""'auto' chat mode: Code Interpreter only for questions that need the workbook itself."""
import pytest

from app.ai.mode_router import wants_code_interpreter


@pytest.mark.parametrize(
    "message",
    [
        "Сохрани в CSV таблицу активов, обязательств и капитала",
        "Построй график выручки по годам",
        "Посчитай по файлу коэффициент текущей ликвидности",
        "Сделай таблицу основных показателей баланса",
        "Пересчитай коэффициенты ликвидности",
        "Выгрузи баланс в Excel",
        "Проверь расчёты по исходным данным",
        "Что лежит в файле на втором листе?",
    ],
)
def test_file_table_chart_and_recalculation_go_to_code_interpreter(message):
    assert wants_code_interpreter(message)


@pytest.mark.parametrize(
    "message",
    [
        "Какие риски выявлены в отчетности?",
        "Какая выручка у компании?",
        "Сравни показатели ликвидности с нормативами",
        "Оцени вероятность банкротства по отчетности",
        "Какова динамика чистой прибыли?",
        "А она больше чистой прибыли? Во сколько раз?",
        "Посчитай рентабельность активов",
        "",
    ],
)
def test_plain_questions_stay_on_the_fast_path(message):
    assert not wants_code_interpreter(message)
