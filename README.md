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

За основу взят оригинальный проект [ss14-tts-api](https://github.com/Rxup/ss14-tts-api). В данной версии мы перешли на новейшую модель **Silero V5 CIS Base (nostress)**, которая поддерживает десятки русских голосов и автоматически расставляет ударения, что позволяет отказаться от использования дополнительных библиотек вроде `StressRNN`.

Сервер позволяет генерировать речь для игровых сущностей, объявлений и интеркома прямо в Space Station 14.

## ✨ Возможности

* **Silero V5 CIS Base** — огромный выбор русских голосов (с префиксом `ru_`), а также поддержка других языков CIS.
* **Автоматические ударения** — модель `nostress` сама расставляет ударения для славянских языков.
* **Звуковые эффекты** — встроенная обработка звука через FFmpeg: `Echo` (эхо), `Radio` (рация), `Robot` (робот).
* **Кастомные голоса** — возможность сохранять и использовать собственные `.pt` файлы голосов.
* **REST API** — простой и понятный интерфейс для интеграции с игровым сервером на C#.
* **Веб-интерфейс** — встроенная страница-тестер для быстрой проверки голосов и эффектов.

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

4. Установите Python-зависимости (PyTorch скачается в CPU-версии):
    pip install -r requirements.txt

5. Запустите сервер:
    python ss14tts.py

При первом запуске автоматически скачается модель `v5_cis_base_nostress.pt` (около 90 МБ) и выполнится прогрев голосов.

## ⚙️ Конфигурация

По умолчанию сервер запускается на порту `5000`. Вы можете изменить порт и токен доступа через переменные окружения:

* `PORT` — порт сервера (по умолчанию `5000`).
* `apitoken` — токен для доступа к API (по умолчанию `test`).
* `threads` — количество потоков CPU для PyTorch (по умолчанию `6`).

Пример запуска с кастомными настройками:
    apitoken="SuperSecretToken" PORT=8080 python ss14tts.py

## 🔌 API Эндпоинты

* `GET /health` — проверка работоспособности сервера (возвращает `OK`).
* `GET /voices` — список всех доступных голосов (включая кастомные `.pt`).
* `POST /tts` — генерация речи.
    * Принимает JSON: `text`, `speaker`, `api_token`, `format` (ogg/wav), `effect` (Echo/Radio/Robot).
    * Возвращает JSON с аудио, закодированным в Base64.

## 🧪 Тестирование

В проекте настроены быстрые тесты, которые не требуют скачивания тяжелой модели. Запуск осуществляется через `pytest`:
    pytest tests/ -v

Для ручной проверки звуковых эффектов (требуется модель) используйте:
    python tests/manual_test_effects.py

## 🤝 Контрибьют и Лицензия

**Наш код — MIT.** (Подробности в файле [LICENSE](LICENSE)).

**Об оригинальном проекте:** За основу был взят репозиторий [ss14-tts-api](https://github.com/Rxup/ss14-tts-api). На момент создания нашей версии в нём **отсутствовал файл лицензии**, что по умолчанию означает сохранение всех прав автора (All Rights Reserved). Наш проект является глубокой переработкой (смена модели, удаление устаревших зависимостей, рефакторинг структуры), поэтому мы лицензируем именно наш код под MIT. Мы не претендуем на авторство оригинального кода.

**Модель Silero TTS:** Нейросеть предоставляется под [собственной лицензией](https://github.com/snakers4/silero-models#license) и не покрывается лицензией MIT нашего репозитория.

Мы всегда рады Pull Request'ам! Если вы нашли баг или хотите добавить новый звуковой эффект, создавайте Issue или присылайте PR.

---
*Разработано для проекта VanGuard. Особая благодарность Rxup за оригинальный API и сообществу Silero за их потрясающие модели.*