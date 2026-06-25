# Генератор коммерческих предложений

Веб-приложение для автоматической генерации коммерческих предложений в PDF.

## Возможности
- Заполнение данных через веб-форму
- Автоматический расчет сумм и НДС
- Генерация PDF с поддержкой кириллицы
- Скачивание готового документа

## Технологии
**Backend** - Python 3.8+, Flask
**PDF генерация** - ReportLab
**Frontend**  - HTML5, CSS3, JavaScript (Vanilla)
**Шрифты** - Поддержка кириллицы (Arial)
**Среда** - Виртуальное окружение (venv)

## Установка и запуск

### 1. Клонируйте репозиторий
git clone https://github.com/kzrrwv/commercial-offer-generator.git
cd commercial-offer-generator

### 2. Создайте виртуальное окружение
python -m venv venv

### 3. Активирйте виртуальное окружение
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate

### 4. Установите зависимости
pip install -r requirements.txt

### 5. Сгенирируйте PDF-шаблон
python create_template.py

### 6. Запустите приложение
python app.py

### 7. Откройте в браузере
Перейдите по адресу:
http://127.0.0.1:5000