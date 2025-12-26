# S04 – eda_cli: HTTP-сервис качества датасетов (FastAPI)

Расширенная версия проекта `eda-cli` из Семинара 03.

К существующему CLI-приложению для EDA добавлен **HTTP-сервис на FastAPI** с эндпоинтами `/health`, `/quality` и `/quality-from-csv`.  
Используется в рамках Семинара 04 курса «Инженерия ИИ».

---

## Связь с S03

Проект в S04 основан на том же пакете `eda_cli`, что и в S03:

- сохраняется структура `src/eda_cli/` и CLI-команда `eda-cli`;
- добавлен модуль `api.py` с FastAPI-приложением;
- в зависимости добавлены `fastapi` и `uvicorn[standard]`.

Цель S04 – показать, как поверх уже написанного EDA-ядра поднять простой HTTP-сервис.

---

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему
- Браузер (для Swagger UI `/docs`) или любой HTTP-клиент:
  - `curl` / HTTP-клиент в IDE / Postman / Hoppscotch и т.п.

---

## Инициализация проекта

В корне проекта (каталог S04/eda-cli):

```bash
uv sync
```

Команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml` (включая FastAPI и Uvicorn);
- установит сам проект `eda-cli` в окружение.

---

## Запуск CLI (как в S03)

CLI остаётся доступным и в S04.

### Краткий обзор

```bash
uv run eda-cli overview data/example.csv
```

Параметры:

- `--sep` - разделитель (по умолчанию `,`);
- `--encoding` - кодировка (по умолчанию `utf-8`).

### Полный EDA-отчёт

```bash
uv run eda-cli report data/example.csv --out-dir reports
```

В результате в каталоге `reports/` появятся:

- `report.md` - основной отчёт в Markdown;
- `summary.csv` - таблица по колонкам;
- `missing.csv` - пропуски по колонкам;
- `correlation.csv` - корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` - top-k категорий по строковым признакам;
- `hist_*.png` - гистограммы числовых колонок;
- `missing_matrix.png` - визуализация пропусков;
- `correlation_heatmap.png` - тепловая карта корреляций.

---

## Запуск HTTP-сервиса

HTTP-сервис реализован в модуле `eda_cli.api` на FastAPI.

### Запуск Uvicorn

```bash
uv run uvicorn eda_cli.api:app --reload --port 8000
```

Пояснения:

- `eda_cli.api:app` - путь до объекта FastAPI `app` в модуле `eda_cli.api`;
- `--reload` - автоматический перезапуск сервера при изменении кода (удобно для разработки);
- `--port 8000` - порт сервиса (можно поменять при необходимости).

После запуска сервис будет доступен по адресу:

```text
http://127.0.0.1:8000
```

---

## Эндпоинты сервиса

### 1. `GET /health`

Простейший health-check.

**Запрос:**

```http
GET /health
```

**Ожидаемый ответ `200 OK` (JSON):**

```json
{
  "status": "ok",
  "service": "dataset-quality",
  "version": "0.2.0"
}
```

Пример проверки через `curl`:

```bash
curl http://127.0.0.1:8000/health
```

---

### 2. Swagger UI: `GET /docs`

Интерфейс документации и тестирования API:

```text
http://127.0.0.1:8000/docs
```

Через `/docs` можно:

- вызывать `GET /health`;
- вызывать `POST /quality` (форма для JSON);
- вызывать `POST /quality-from-csv` (форма для загрузки файла).

---

### 3. `POST /quality` – заглушка по агрегированным признакам

Эндпоинт принимает **агрегированные признаки датасета** (размеры, доля пропусков и т.п.) и возвращает эвристическую оценку качества.

**Пример запроса:**

```http
POST /quality
Content-Type: application/json
```

Тело:

```json
{
  "n_rows": 10000,
  "n_cols": 12,
  "max_missing_share": 0.15,
  "numeric_cols": 8,
  "categorical_cols": 4
}
```

**Пример ответа `200 OK`:**

```json
{
  "ok_for_model": true,
  "quality_score": 0.8,
  "message": "Данных достаточно, модель можно обучать (по текущим эвристикам).",
  "latency_ms": 3.2,
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": false,
    "no_numeric_columns": false,
    "no_categorical_columns": false
  },
  "dataset_shape": {
    "n_rows": 10000,
    "n_cols": 12
  }
}
```

**Пример вызова через `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/quality" \
  -H "Content-Type: application/json" \
  -d '{"n_rows": 10000, "n_cols": 12, "max_missing_share": 0.15, "numeric_cols": 8, "categorical_cols": 4}'
```

---

### 4. `POST /quality-from-csv` – оценка качества по CSV-файлу

Эндпоинт принимает CSV-файл, внутри:

- читает его в `pandas.DataFrame`;
- вызывает функции из `eda_cli.core`:

  - `summarize_dataset`,
  - `missing_table`,
  - `compute_quality_flags`;
- возвращает оценку качества датасета в том же формате, что `/quality`.

**Запрос:**

```http
POST /quality-from-csv
Content-Type: multipart/form-data
file: <CSV-файл>
```

Через Swagger:

- в `/docs` открыть `POST /quality-from-csv`,
- нажать `Try it out`,
- выбрать файл (например, `data/example.csv`),
- нажать `Execute`.

**Пример вызова через `curl` (Linux/macOS/WSL):**

```bash
curl -X POST "http://127.0.0.1:8000/quality-from-csv" \
  -F "file=@data/example.csv"
```

Ответ будет содержать:

- `ok_for_model` - результат по эвристикам;
- `quality_score` - интегральный скор качества;
- `flags` - булевы флаги из `compute_quality_flags`;
- `dataset_shape` - реальные размеры датасета (`n_rows`, `n_cols`);
- `latency_ms` - время обработки запроса.

---

### 5. `POST /quality-flags-from-csv` – эвристики по CSV-файлу,возвращает полный набор флагов качества

Эндпоинт принимает CSV-файл, внутри:

- читает его в `pandas.DataFrame`;
- вызывает функции из `eda_cli.core`:

  - `summarize_dataset`,
  - `missing_table`,
  - `compute_quality_flags`;


**Запрос:**

```http
POST /quality-flags-from-csv
Content-Type: multipart/form-data
file: <CSV-файл>
```

Через Swagger:

- в `/docs` открыть `POST /quality-flags-from-csv`,
- нажать `Try it out`,
- выбрать файл (например, `data/example.csv`),
- нажать `Execute`.

**Пример вызова через `curl` (Linux/macOS/WSL):**

```bash
curl -X POST "http://127.0.0.1:8000/quality-flags-from-csv" \
  -F "file=@data/example.csv"
```
---

Ответ будет содержать:


- `flags` - булевы флаги из `compute_quality_flags`;
- `dataset_shape` - реальные размеры датасета (`n_rows`, `n_cols`);
- `latency_ms` - время обработки запроса.

---

**Пример ответа `200 OK`:**

```json
{
  "flags": {
    "too_few_rows": true,
    "too_many_columns": false,
    "too_many_missing": false,
    "has_constant_columns": false,
    "has_high_cardinality_categoricals": false,
    "has_suspicious_id_duplicates": true
  },
  "dataset_shape": {
    "n_rows": 36,
    "n_cols": 14
  },
  "latency_ms": 18.32030015066266
}
```


### 6. `POST /summary-from-csv` – JSON-сводка о датасете CSV-файла

Эндпоинт принимает CSV-файл, внутри:

- читает его в `pandas.DataFrame`;
- вызывает функции из `eda_cli.core`:

  - `summarize_dataset`,
  - `missing_table`,
  - `compute_quality_flags`;


**Запрос:**

```http
POST /quality-from-csv
Content-Type: multipart/form-data
file: <CSV-файл>
```

Через Swagger:

- в `/docs` открыть `POST /summary-from-csv`,
- нажать `Try it out`,
- выбрать файл (например, `data/example.csv`),
- нажать `Execute`.

**Пример вызова через `curl` (Linux/macOS/WSL):**

```bash
curl -X POST "http://127.0.0.1:8000/summary-from-csv" \
  -F "file=@data/example.csv"
```

Ответ будет содержать:

- `columns` - стастика по данным в датасете;
- `quality_score` - интегральный скор качества;
- `flags` - булевы флаги из `compute_quality_flags`;
- `dataset_shape` - реальные размеры датасета (`n_rows`, `n_cols`);
- `latency_ms` - время обработки запроса.

**Пример ответа `200 OK`:**

```json
{
  "summary": {
    "shape": {
      "n_rows": 36,
      "n_cols": 14
    },
    "n_rows": 36,
    "n_cols": 14,
    "columns": [
      {
        "name": "user_id",
        "dtype": "int64",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 35,
        "example_values": [
          "1001",
          "1002",
          "1003"
        ],
        "is_numeric": true,
        "min": 1001,
        "max": 1035,
        "mean": 1018.1944444444445,
        "std": 10.166666666666666
      },
      {
        "name": "country",
        "dtype": "object",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 4,
        "example_values": [
          "RU",
          "KZ",
          "BY"
        ],
        "is_numeric": false,
        "min": null,
        "max": null,
        "mean": null,
        "std": null
      },
      {
        "name": "city",
        "dtype": "object",
        "non_null": 34,
        "missing": 2,
        "missing_share": 0.05555555555555555,
        "unique": 16,
        "example_values": [
          "Moscow",
          "Saint Petersburg",
          "Almaty"
        ],
        "is_numeric": false,
        "min": null,
        "max": null,
        "mean": null,
        "std": null
      },
      {
        "name": "device",
        "dtype": "object",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 3,
        "example_values": [
          "Desktop",
          "Mobile",
          "Tablet"
        ],
        "is_numeric": false,
        "min": null,
        "max": null,
        "mean": null,
        "std": null
      },
      {
        "name": "channel",
        "dtype": "object",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 4,
        "example_values": [
          "Organic",
          "Ads",
          "Referral"
        ],
        "is_numeric": false,
        "min": null,
        "max": null,
        "mean": null,
        "std": null
      },
      {
        "name": "sessions_last_30d",
        "dtype": "int64",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 26,
        "example_values": [
          "25",
          "5",
          "12"
        ],
        "is_numeric": true,
        "min": 0,
        "max": 34,
        "mean": 11.944444444444445,
        "std": 8.608781046763305
      },
      {
        "name": "avg_session_duration_min",
        "dtype": "float64",
        "non_null": 34,
        "missing": 2,
        "missing_share": 0.05555555555555555,
        "unique": 32,
        "example_values": [
          "12.5",
          "4.2",
          "8.3"
        ],
        "is_numeric": true,
        "min": 2,
        "max": 15.2,
        "mean": 7.247058823529413,
        "std": 3.473382361148563
      },
      {
        "name": "pages_per_session",
        "dtype": "float64",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 32,
        "example_values": [
          "6.2",
          "3.1",
          "5.0"
        ],
        "is_numeric": true,
        "min": 1,
        "max": 7.5,
        "mean": 4.099999999999999,
        "std": 1.5605859705343283
      },
      {
        "name": "purchases_last_30d",
        "dtype": "int64",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 5,
        "example_values": [
          "3",
          "0",
          "1"
        ],
        "is_numeric": true,
        "min": 0,
        "max": 4,
        "mean": 1.1388888888888888,
        "std": 1.1251102238772057
      },
      {
        "name": "revenue_last_30d",
        "dtype": "float64",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 23,
        "example_values": [
          "4500.0",
          "0.0",
          "1200.0"
        ],
        "is_numeric": true,
        "min": 0,
        "max": 7000,
        "mean": 1575.013888888889,
        "std": 1815.2805784156387
      },
      {
        "name": "churned",
        "dtype": "int64",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 2,
        "example_values": [
          "0",
          "1"
        ],
        "is_numeric": true,
        "min": 0,
        "max": 1,
        "mean": 0.3333333333333333,
        "std": 0.47809144373375745
      },
      {
        "name": "signup_year",
        "dtype": "int64",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 7,
        "example_values": [
          "2021",
          "2020",
          "2022"
        ],
        "is_numeric": true,
        "min": 2018,
        "max": 2024,
        "mean": 2020.9722222222222,
        "std": 1.5210167860651849
      },
      {
        "name": "plan",
        "dtype": "object",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 3,
        "example_values": [
          "Pro",
          "Free",
          "Basic"
        ],
        "is_numeric": false,
        "min": null,
        "max": null,
        "mean": null,
        "std": null
      },
      {
        "name": "n_support_tickets",
        "dtype": "int64",
        "non_null": 36,
        "missing": 0,
        "missing_share": 0,
        "unique": 6,
        "example_values": [
          "1",
          "0",
          "2"
        ],
        "is_numeric": true,
        "min": 0,
        "max": 5,
        "mean": 1.0833333333333333,
        "std": 1.2041594578792296
      }
    ],
    "missing_info": [
      {
        "missing_count": 2,
        "missing_share": 0.05555555555555555
      },
      {
        "missing_count": 2,
        "missing_share": 0.05555555555555555
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      },
      {
        "missing_count": 0,
        "missing_share": 0
      }
    ],
    "quality_flags": {
      "too_few_rows": true,
      "too_many_columns": false,
      "max_missing_share": 0.05555555555555555,
      "too_many_missing": false,
      "has_constant_columns": false,
      "constant_columns": [],
      "n_constant_columns": 0,
      "has_high_cardinality_categoricals": false,
      "high_cardinality_columns": [],
      "n_high_cardinality_columns": 0,
      "has_suspicious_id_duplicates": true,
      "suspicious_id_columns": [
        {
          "column": "user_id",
          "unique_values": 35,
          "duplicate_ratio": 0.02777777777777779,
          "description": "Возможный ID с дубликатами (35 уникальных из 36)"
        }
      ],
      "quality_score": 0.49444444444444446
    }
  },
  "latency_ms": 20.446799928322434
}
```


## Структура проекта (упрощённо)

```text
S04/
  eda-cli/
    pyproject.toml
    README.md                # этот файл
    src/
      eda_cli/
        __init__.py
        core.py              # EDA-логика, эвристики качества
        viz.py               # визуализации
        cli.py               # CLI (overview/report)
        api.py               # HTTP-сервис (FastAPI)
    tests/
      test_core.py           # тесты ядра
    data/
      example.csv            # учебный CSV для экспериментов
```

---

## Тесты

Запуск тестов (как и в S03):

```bash
uv run pytest -q
```

Рекомендуется перед любыми изменениями в логике качества данных и API:

1. Запустить тесты `pytest`;
2. Проверить работу CLI (`uv run eda-cli ...`);
3. Проверить работу HTTP-сервиса (`uv run uvicorn ...`, затем `/health` и `/quality`/`/quality-from-csv` через `/docs` или HTTP-клиент).
