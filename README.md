# Atomic Parser

Этот проект представляет собой инструмент для сбора и анализа данных о ядерных реакторах с помощью веб-скрапинга. Проект использует библиотеки Selenium для автоматизации работы с браузером, BeautifulSoup для разбора HTML-кода веб-страниц и модуль csv для записи данных в файлы CSV.

## Что делает этот проект?

1. Собирает данные о ядерных реакторах различных стран.
2. Извлекает информацию о каждом реакторе, такую как его название, тип, статус, емкость, даты подключения к сети и т. д.
3. Анализирует данные о загрузке реактора (Load Factor) за определенный период времени.

## Где хранятся файлы выхода?

- Файлы с данными о реакторах записываются в файл **reactors.csv** в папку **out**.
- Файлы с данными о загрузке реакторов записываются в файл **loadFactors.csv** в папку **out**.

## Как использовать?

1. Установите необходимые библиотеки, перечисленные в секции зависимостей.
2. Запустите скрипт из командной строки или интерпретатора Python.
3. Дождитесь завершения сбора данных. По окончании данные будут записаны в указанные файлы CSV.

### Примечание:

- Для использования Selenium необходимо установить драйвер браузера (в данном случае используется Microsoft Edge). Драйвер должен быть установлен и настроен соответствующим образом.
- Убедитесь, что библиотеки Selenium, BeautifulSoup установлены в вашем окружении Python.
- Убедитесь, что папка **out** существует в том месте, откуда запускается скрипт, или измените пути к файлам выхода по вашему усмотрению.
