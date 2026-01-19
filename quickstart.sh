#!/bin/bash
# 🎾 Tennis League - Быстрые команды

echo \"╔════════════════════════════════════════════════════════════╗\"
echo \"║      🎾 TENNIS LEAGUE PLATFORM - БЫСТРЫЕ КОМАНДЫ          ║\"
echo \"╚════════════════════════════════════════════════════════════╝\"
echo \"\"

# Получить статус сервера
check_server() {
    echo \"🔍 Проверка статуса сервера...\"
    curl -s -I http://127.0.0.1:8001/ | head -1
    echo \"\"
}

# Запустить сервер
start_server() {
    echo \"🚀 Запуск сервера на порту 8001...\"
    cd /home/skifmail/Projects/Tennis
    source venv/bin/activate
    python manage.py runserver 127.0.0.1:8001
}

# Остановить сервер
stop_server() {
    echo \"⏹️  Остановка сервера...\"
    pkill -f \"python manage.py runserver\"
    echo \"✅ Сервер остановлен\"
}

# Открыть в браузере
open_browser() {
    echo \"🌐 Открыто: http://127.0.0.1:8001\"
    # Автоматическое открытие браузера (Linux/Mac/Windows)
    if command -v xdg-open > /dev/null; then
        xdg-open http://127.0.0.1:8001
    elif command -v open > /dev/null; then
        open http://127.0.0.1:8001
    elif command -v start > /dev/null; then
        start http://127.0.0.1:8001
    fi
}

# Просмотр логов
view_logs() {
    echo \"📋 Просмотр логов сервера...\"
    tail -20 /tmp/tennis_server.log 2>/dev/null || echo \"Логи не найдены\"
}

# Помощь
show_help() {
    echo \"Доступные команды:\"
    echo \"  check       - Проверить статус сервера\"
    echo \"  start       - Запустить сервер\"
    echo \"  stop        - Остановить сервер\"
    echo \"  browser     - Открыть браузер\"
    echo \"  logs        - Просмотреть логи\"
    echo \"  help        - Помощь\"
    echo \"\"
    echo \"Примеры:\"
    echo \"  ./quickstart.sh check\"
    echo \"  ./quickstart.sh start\"
    echo \"  ./quickstart.sh stop\"
}

# Основная логика
case \"$1\" in
    check)
        check_server
        ;;
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    browser)
        open_browser
        ;;
    logs)
        view_logs
        ;;
    help)
        show_help
        ;;
    *)
        echo \"Использование: $0 {check|start|stop|browser|logs|help}\"
        show_help
        ;;
esac
