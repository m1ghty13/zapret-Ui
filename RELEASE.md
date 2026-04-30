# Инструкция по созданию первого релиза

## Подготовка на Windows

### 1. Клонировать репозиторий
```bash
git clone https://github.com/m1ghtyqxddd/zapret-ui.git
cd zapret-ui
```

### 2. Установить зависимости
```bash
pip install -r requirements.txt
```

### 3. Собрать .exe
```bash
python scripts/build.py
```

Результат: `dist/ZapretUI.exe` (~15-20 МБ)

### 4. Протестировать
- Запустить `ZapretUI.exe` от имени администратора
- Проверить все панели (Главная, Стратегии, Домены, Логи, Настройки)
- Запустить автотест
- Проверить системный трей
- Проверить health monitor (подождать 5 минут)

## Создание релиза

### 5. Сделать скриншоты
Нужны:
- `screenshots/main-window.png` - главное окно
- `screenshots/strategies.png` - панель стратегий
- `screenshots/tray-menu.png` - меню трея
- `screenshots/autotest.gif` - GIF автотеста (15 сек)

Инструменты:
- Скриншоты: Win+Shift+S
- GIF: ScreenToGif (https://www.screentogif.com/)

### 6. Обновить README
Добавить в README.md:
```markdown
## 📸 Скриншоты

### Главное окно
![Main Window](screenshots/main-window.png)

### Автотест стратегий
![Autotest](screenshots/autotest.gif)

### Системный трей
![Tray Menu](screenshots/tray-menu.png)
```

### 7. Создать тег и запушить
```bash
git add screenshots/
git commit -m "Добавлены скриншоты для релиза v2.1.0"
git push

# Создать тег
git tag -a v2.1.0 -m "Zapret UI v2.1.0 - Первый стабильный релиз"
git push origin v2.1.0
```

### 8. GitHub Actions автоматически:
- Соберёт .exe на Windows runner
- Создаст GitHub Release
- Прикрепит ZapretUI.exe к релизу

### 9. Проверить релиз
- Перейти на https://github.com/m1ghtyqxddd/zapret-ui/releases
- Убедиться что релиз создан
- Скачать ZapretUI.exe и протестировать

## Changelog для v2.1.0

```markdown
## Zapret UI v2.1.0 - Первый стабильный релиз

### ✨ Основные возможности
- Нативный PyQt6 интерфейс
- Системный трей с управлением
- Автоматическое тестирование стратегий
- Управление группами доменов
- Просмотр логов winws.exe

### 🔧 Технические улучшения
- Правильная проверка DPI bypass через TLS handshake
- Health monitor - фоновая проверка каждые 5 минут
- Single-instance lock - защита от конфликта WinDivert
- Graceful shutdown winws.exe
- Crash handler с автоматическими отчётами
- Нативные Windows toast notifications

### 📦 Оптимизация
- Минимальные зависимости (только PyQt6)
- Размер .exe: ~15-20 МБ
- Потребление RAM: ~50-80 МБ
- Убраны httpx, pystray, Pillow

### 🎯 Конкурентные преимущества
- Автоматическое обнаружение поломки стратегии
- Переключение стратегий из трея
- Автоматические релизы через GitHub Actions
- UAC манифест - автозапрос прав администратора

### 📋 Требования
- Windows 10/11
- Права администратора
- Python 3.8+ (для разработки)

### 🐛 Известные проблемы
- Антивирусы могут блокировать .exe (добавьте в исключения)
- Иконка может быть в скрытых значках трея
```

## После релиза

### 10. Анонсировать
- Создать пост на Reddit (r/russia, r/pikabu)
- Telegram каналы про обход блокировок
- GitHub Discussions

### 11. Мониторинг
- Следить за Issues
- Собирать crash reports из %APPDATA%/ZapretUI/crash_*.log
- Обновлять списки доменов

## Troubleshooting

### GitHub Actions не запустился
- Проверить что тег начинается с `v` (v2.1.0)
- Проверить что workflow файл в `.github/workflows/release.yml`
- Проверить Actions в настройках репозитория

### Сборка .exe упала
- Проверить что все зависимости установлены
- Проверить что PyInstaller >= 6.0.0
- Проверить что манифест существует: `scripts/ZapretUI.manifest`

### .exe не запускается
- Запустить от имени администратора
- Проверить что winws.exe в папке bin/
- Проверить логи в %APPDATA%/ZapretUI/app.log
