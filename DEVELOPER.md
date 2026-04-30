# Zapret UI - Краткая справка для разработчика

## Быстрый старт на Windows

```bash
# Клонировать и установить
git clone https://github.com/m1ghtyqxddd/zapret-ui.git
cd zapret-ui
pip install -r requirements.txt

# Запустить для разработки
python main.py

# Собрать .exe
python scripts/build.py
```

## Архитектура

### Точка входа: `main.py`
- Crash handler (sys.excepthook)
- Single-instance lock (QLocalServer)
- Создание QApplication + MainWindow + Tray

### Ядро: `core/`
- **runner.py** - управление winws.exe через subprocess
- **tester.py** - автотест стратегий (TLS handshake)
- **health_monitor.py** - фоновая проверка каждые 5 мин
- **strategies.py** - парсинг strategies/*.txt
- **domains.py** - сборка hostlist из lists/*.txt
- **config.py** - %APPDATA%/ZapretUI/config.json

### UI: `ui/`
- **main_window.py** - sidebar + 5 панелей
- **tray.py** - нативный Qt трей с меню стратегий
- **panels/** - home, strategies, domains, logs, settings

## Ключевые фичи

### 1. Правильный автотест
```python
# core/tester.py
# Проверка через TLS handshake, а не HTTP GET
sock.connect((domain, 443))
context.wrap_socket(sock, server_hostname=domain)
```

### 2. Health monitor
```python
# core/health_monitor.py
# QTimer каждые 5 минут
# Если стратегия сломалась -> диалог с предложением автотеста
```

### 3. Graceful shutdown
```python
# core/runner.py
# Windows: CTRL_BREAK_EVENT
# Ждём 3 сек, потом kill
# Освобождение WinDivert handle
```

### 4. Crash handler
```python
# main.py
# sys.excepthook -> crash_YYYYMMDD_HHMMSS.log
# Диалог с предложением отправить отчёт
```

## Создание релиза

```bash
# 1. Собрать на Windows
python scripts/build.py

# 2. Протестировать
dist/ZapretUI.exe

# 3. Сделать скриншоты
# - screenshots/main-window.png
# - screenshots/autotest.gif

# 4. Создать тег
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin v2.1.0

# 5. GitHub Actions автоматически:
# - Соберёт .exe
# - Создаст Release
# - Прикрепит артефакт
```

## Troubleshooting

### Автотест не работает
- Проверить что winws.exe запущен
- Проверить timeout (10 сек)
- Проверить settle time (5 сек)
- Логи в %APPDATA%/ZapretUI/app.log

### Трей не показывается
- Проверить QSystemTrayIcon.isSystemTrayAvailable()
- Иконки в assets/icon-active.ico, icon-inactive.ico
- Fallback иконки генерируются автоматически

### .exe не собирается
- PyInstaller >= 6.0.0
- Манифест: scripts/ZapretUI.manifest
- Проверить --add-data пути (bin;bin, lists;lists)

### Health monitor не срабатывает
- Запускается только когда winws.exe активен
- Проверка каждые 5 минут (300000 мс)
- Тестирует discord.com, youtube.com

## Будущие фичи (опционально)

### Per-application strategies
```python
# Разные стратегии для разных доменов
youtube.txt -> ALT3
discord.txt -> ALT5
# Несколько winws.exe на разных --qnum
```

### CLI режим
```bash
ZapretUI.exe --start --strategy ALT3 --silent
ZapretUI.exe --stop
ZapretUI.exe --autotest --apply-best
```

### Импорт/экспорт конфигов
```python
# Один JSON файл
# Export profile / Import profile
# Шаринг рабочих связок
```

### Speed test
```python
# Замер latency до/после
# Visual proof что работает
```

### Светлая тема
```python
# ui/theme.py
# Определение через palette().window().lightness()
```

## Полезные команды

```bash
# Логи
tail -f %APPDATA%/ZapretUI/app.log

# Crash reports
ls %APPDATA%/ZapretUI/crash_*.log

# Конфиг
cat %APPDATA%/ZapretUI/config.json

# Проверка процесса
tasklist | findstr winws.exe

# Убить процесс
taskkill /F /IM winws.exe
```

## Контакты

- GitHub: https://github.com/m1ghtyqxddd/zapret-ui
- Issues: https://github.com/m1ghtyqxddd/zapret-ui/issues
- Upstream zapret: https://github.com/bol-van/zapret

## Версия

- Текущая: v2.1.0
- Дата: 2026-04-30
- Python: 3.8+
- Платформа: Windows 10/11
