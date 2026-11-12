<p align="center">
  <img alt="VanGuard SS14" width="350" src="https://raw.githubusercontent.com/VG-SpaceStation14/VanGuardSS14/master/Resources/Textures/_VanGuard/Logo/logo.png" />
</p>

<div align="center">

[![Discord](https://img.shields.io/badge/Discord-Наш%20сервер-E05A33?logo=discord&logoColor=white&style=for-the-badge&labelColor=1C1C1C)](https://discord.gg/nW73CdBYkg) 
[![Сайт](https://img.shields.io/badge/Сайт-Наш%20сайт-E05A33?style=for-the-badge&labelColor=1C1C1C)](https://vanguardproject.ru/index.html)
[![Main Repo](https://img.shields.io/badge/VanGuard-SS14%20Repo-E05A33?logo=github&logoColor=white&style=for-the-badge&labelColor=1C1C1C)](https://github.com/VG-SpaceStation14/VanGuardSS14) 
[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?logo=python&logoColor=white&style=for-the-badge&labelColor=1C1C1C)](https://www.python.org/) 
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU-EE4C2C?logo=pytorch&logoColor=white&style=for-the-badge&labelColor=1C1C1C)](https://pytorch.org/)

</div>

---

## 🎙 О проекте

**VanGuard TTS API** — это адаптированный и обновленный TTS-сервер (Text-to-Speech) для проекта [VanGuard](https://github.com/VG-SpaceStation14/VanGuardSS14). 

За основу взят оригинальный проект [ss14-tts-api](https://github.com/Rxup/ss14-tts-api). В данной версии мы перешли на новейшую модель **Silero V5 CIS Base (nostress)**, которая поддерживает десятки голосов для разных языков (включая огромный выбор русских голосов с префиксом `ru_`).

Сервер позволяет генерировать речь для игровых сущностей, объявлений и интеркома прямо в Space Station 14.

## ✨ Возможности

* **Silero V5 CIS Base** — огромный выбор голосов, включая более 20 новых русских голосов.
* **Управление ударениями** — поскольку версия `nostress` **не** расставляет ударения для славянских языков автоматически, текст передается в модель как есть. Для корректного звучания сложных слов ударение можно расставить вручную (например, символом `+` перед ударной гласной: `зам+ок`).
* **Звуковые эффекты** — встроенная обработка звука через FFmpeg: `Echo` (эхо), `Radio` (рация), `Robot` (робот).
* **Кастомные голоса** — возможность сохранять и использовать собственные `.pt` файлы голосов.
* **REST API** — простой и понятный интерфейс для интеграции с игровым сервером на C#.
* **Веб-интерфейс** — встроенная страница-тестер для быстрой проверки голосов и эффектов в браузере.

## 🛠 Архитектура и Стек

* **Язык:** Python 3.14+.
* **Нейросеть:** PyTorch (CPU-версия), Silero V5 CIS Base (nostress).
* **Веб-фреймворк:** Flask.
* **Аудио-движок:** FFmpeg, SoundFile.
* **Тестирование:** Pytest (с моками для быстрой проверки без загрузки модели).

## 🚀 Установка и запуск

**Требования:** Python 3.14+, FFmpeg, libsndfile (для Linux).

1. Установите системные зависимости (на примере Arch Linux):
    sudo pacman -S ffmpeg libsndfile

2. Склонируйте репозиторий и перейдите в папку:
    git clone https://github.com/Ваш-Аккаунт/VanGuard.TTS.git
    cd VanGuard.TTS

3. Создайте виртуальное окружение и активируйте его:
    python3.14 -m venv .venv
    source .venv/bin/activate

4. Установите Python-зависимости:
    pip install -r requirements.txt

5. Создайте файл конфигурации `.env` на основе примера:
    cp .env.example .env

6. Запустите сервер:
    python ss14tts.py

При первом запуске автоматически скачается модель `v5_cis_base_nostress.pt` (около 90 МБ) и выполнится прогрев голосов.

## ⚙️ Конфигурация

Настройки сервера хранятся в файле `.env`. По умолчанию используются следующие значения:

* `PORT` — порт сервера (по умолчанию `5000`).
* `API_TOKEN` — токен для доступа к API (по умолчанию `test`). Обязательно поменяйте его на свой, если сервер доступен извне.
* `THREADS` — количество потоков CPU для PyTorch (по умолчанию `6`).

## 🔌 API Эндпоинты

* `GET /health` — проверка работоспособности сервера (возвращает `OK`).
* `GET /voices` — список всех доступных голосов (включая кастомные `.pt`).
* `POST /tts` — генерация речи.
    * Принимает JSON: `text`, `speaker`, `api_token`, `format` (ogg/wav), `effect` (Echo/Radio/Robot).
    * Возвращает JSON с аудио, закодированным в Base64.

## 🧪 Тестирование

В проекте настроены быстрые тесты, которые не требуют скачивания тяжелой модели. Запуск осуществляется через `pytest`:
    pytest tests/ -v

## 📜 Лицензия и авторство

Проект разделен на две части с точки зрения авторского права:

1. **Оригинальный код (Rxup/ss14-tts-api):** На момент форка оригинальный репозиторий **не содержал файла лицензии**, что по умолчанию означает сохранение всех прав автора (All Rights Reserved). Мы не претендуем на авторство базовой архитектуры, HTTP-эндпоинтов и оригинальной логики интеграции.
2. **Наш вклад (VanGuard):** Весь новый код, написанный командой VanGuard (переход на модель Silero V5, новые звуковые эффекты, скрипты CI, тесты, обновленный веб-интерфейс и конфигурация через `.env`), распространяется под лицензией **MIT** (см. файл `LICENSE`).

Если вы являетесь автором оригинального проекта и имеете возражения против использования вашего кода, пожалуйста, свяжитесь с нами.

**Модель Silero TTS:** Нейросеть предоставляется под [собственной лицензией](https://github.com/snakers4/silero-models#license) и не покрывается лицензией MIT нашего репозитория.

---
*Разработано для проекта VanGuard. Особая благодарность Rxup за оригинальный API и сообществу Silero за их потрясающие модели.*