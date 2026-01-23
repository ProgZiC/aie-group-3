# HW06 – Report

> Файл: `homeworks/HW06/report.md`  
> Важно: не меняйте названия разделов (заголовков). Заполняйте текстом и/или вставляйте результаты.

## 1. Dataset

- **Какой датасет выбран:** `S06-hw-dataset-01.csv`
- **Размер:** 12 000 строк, 30 столбцов (после удаления `id`)
- **Целевая переменная:** `target`  
  - Класс 0: 67.66%  
  - Класс 1: 32.34%
- **Признаки:**  
  - Числовые: `num01`–`num24` (24 признака)  
  - Категориальные в виде кодов: `cat_contract`, `cat_region`, `cat_payment`  
  - Целочисленный: `tenure_months`

## 2. Protocol

- **Разбиение:** train/test – 80/20, stratified split, `random_state=42`
- **Подбор:** GridSearchCV на train (5 фолдов), оптимизация по ROC-AUC
- **Метрики:** accuracy, F1, ROC-AUC  
  Выбор обоснован умеренным дисбалансом классов: F1 учитывает баланс precision/recall, ROC-AUC оценивает разделимость классов.

## 3. Models

Описанные модели и подобранные гиперпараметры:

- **DummyClassifier(strategy="stratified")** – baseline
- **LogisticRegression + StandardScaler** – линейный baseline
- **DecisionTreeClassifier** – подбор `max_depth`, `min_samples_leaf`, `min_samples_split`, `criterion`
- **RandomForestClassifier** – подбор `n_estimators`, `max_depth`, `max_features`, `min_samples_split`
- **GradientBoostingClassifier** – подбор `n_estimators`, `learning_rate`, `max_depth`
- **StackingClassifier** (опционально) – базовые модели: LogisticRegression, DecisionTree, RandomForest, GradientBoosting; метамодель: LogisticRegression

## 4. Results

| Модель | Accuracy | F1-score | ROC-AUC |
|--------|----------|----------|---------|
| Dummy Classifier | 0.5754 | 0.3405 | 0.5137 |
| Logistic Regression | 0.8275 | 0.7076 | 0.8747 |
| Decision Tree | 0.8596 | 0.7655 | 0.8936 |
| Random Forest | 0.9213 | 0.8705 | 0.9649 |
| Gradient Boosting | 0.9192 | 0.8686 | 0.9640 |
| **Stacking** | **0.9275** | **0.8857** | **0.9677** |

**Победитель:** StackingClassifier.  
**Обоснование:** показал наивысшие значения по всем ключевым метрикам, что подтверждает эффективность ансамблирования разнородных моделей.

## 5. Analysis

- **Устойчивость:** при изменении `random_state` (5 прогонов для RandomForest и GradientBoosting) метрики колеблются в пределах ±0.01 по ROC-AUC, что свидетельствует о стабильности ансамблей.
- **Ошибки:** confusion matrix лучшей модели (Stacking) показывает сбалансированное распределение ошибок между FP и FN, без явного перекоса.
- **Интерпретация:** permutation importance для Stacking выявила топ-10 признаков, среди которых доминируют `num18` (0.0607) и `num19` (0.0568). Большинство признаков имеют низкую важность (<0.01), что указывает на возможность сокращения размерности без потери качества.

## 6. Conclusion

1. Ансамбли (Stacking, RandomForest, GradientBoosting) значительно превосходят простые модели (дерево, логистическая регрессия).
2. Stacking показал наилучшее качество, но требует больше вычислительных ресурсов и сложнее в интерпретации.
3. При умеренном дисбалансе классов целесообразно использовать F1 и ROC-AUC как основные метрики.
4. Честный протокол (фиксированный train/test split, подбор гиперпараметров только на train) позволяет избежать оптимистичной оценки качества.
5. Permutation importance помогает выявить наиболее информативные признаки и может быть использована для сокращения размерности данных.