#!/usr/bin/env bash
# 一键启动本地开发服务
#   - Wiki.js  http://localhost:3000/
#   - Website  http://localhost:3001/
# 用法：bash server/start.sh
# 停止：bash server/start.sh stop

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WIKI_DIR="$REPO_ROOT/server/wikijs-server"
WEBSITE_DIR="$REPO_ROOT/website"
LOG_DIR="$REPO_ROOT/.logs"
WIKI_PID_FILE="$LOG_DIR/wiki.pid"
WEBSITE_PID_FILE="$LOG_DIR/website.pid"

mkdir -p "$LOG_DIR"

port_in_use() {
    # macOS/Linux: lsof; Windows Git Bash: netstat; bash /dev/tcp fallback
    if command -v lsof >/dev/null 2>&1; then
        lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -ano 2>/dev/null | grep -qE ":$1[[:space:]].*LISTENING"
    else
        (echo >/dev/tcp/127.0.0.1/"$1") 2>/dev/null
    fi
}

is_running() {
    local pid_file="$1"
    [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" >/dev/null 2>&1
}

stop_service() {
    local name="$1" pid_file="$2"
    if is_running "$pid_file"; then
        local pid
        pid=$(cat "$pid_file")
        echo "[$name] 停止中 (PID $pid)..."
        kill "$pid" 2>/dev/null && rm -f "$pid_file"
        echo "[$name] 已停止"
    else
        echo "[$name] 未运行"
        rm -f "$pid_file"
    fi
}

start_wiki() {
    if is_running "$WIKI_PID_FILE"; then
        echo "[wiki] 已运行 (PID $(cat "$WIKI_PID_FILE"))，跳过"
        return
    fi
    if port_in_use 3000; then
        echo "[wiki] 端口 3000 已被占用，跳过"
        return
    fi
    echo "[wiki] 启动中..."
    node "$WIKI_DIR/server" >"$LOG_DIR/wiki.log" 2>&1 &
    echo $! >"$WIKI_PID_FILE"
    echo "[wiki] PID $! — 日志：$LOG_DIR/wiki.log"
}

start_website() {
    if is_running "$WEBSITE_PID_FILE"; then
        echo "[website] 已运行 (PID $(cat "$WEBSITE_PID_FILE"))，跳过"
        return
    fi
    if port_in_use 3001; then
        echo "[website] 端口 3001 已被占用，跳过"
        return
    fi
    echo "[website] 启动中..."
    (cd "$WEBSITE_DIR" && pnpm start) >"$LOG_DIR/website.log" 2>&1 &
    echo $! >"$WEBSITE_PID_FILE"
    echo "[website] PID $! — 日志：$LOG_DIR/website.log"
}

case "${1:-start}" in
    stop)
        stop_service "wiki"    "$WIKI_PID_FILE"
        stop_service "website" "$WEBSITE_PID_FILE"
        ;;
    restart)
        stop_service "wiki"    "$WIKI_PID_FILE"
        stop_service "website" "$WEBSITE_PID_FILE"
        sleep 1
        start_wiki
        start_website
        ;;
    *)
        start_wiki
        start_website
        echo ""
        echo "服务已启动："
        echo "  Wiki    http://localhost:3000/"
        echo "  Website http://localhost:3001/"
        echo ""
        echo "查看日志：tail -f $LOG_DIR/wiki.log"
        echo "停止服务：bash server/start.sh stop"
        ;;
esac
