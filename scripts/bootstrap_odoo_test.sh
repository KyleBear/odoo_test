#!/usr/bin/env bash
# PostgreSQL 설치가 끝난 뒤 실행하세요.
# 1) PostgreSQL 서버 기동(미실행 시)
# 2) 데이터베이스 odoo_test 생성
# 3) odoo_test 안에 Odoo 기본 테이블 생성 (--init base --stop-after-init)
#
# 사용법:
#   cd /Users/a1/Desktop/odoo_project/odoo
#   chmod +x scripts/bootstrap_odoo_test.sh
#   ./scripts/bootstrap_odoo_test.sh

set -e

# Homebrew PostgreSQL on Apple Silicon / Intel
export PATH="/opt/homebrew/opt/postgresql@16/bin:/usr/local/opt/postgresql@16/bin:$PATH"
# Use default Unix socket (don't set PGHOST unless you need TCP)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ODOO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DB_NAME="odoo_test"
VENV_PYTHON="$ODOO_ROOT/.venv/bin/python"
ODOO_BIN="$ODOO_ROOT/odoo-bin"
MAX_TRY=60

echo "[1/4] Checking PostgreSQL..."
if ! command -v psql &>/dev/null && ! command -v pg_isready &>/dev/null; then
    echo "PostgreSQL 클라이언트가 없습니다. 먼저 설치하세요: brew install postgresql@16"
    exit 1
fi

echo "[2/4] Starting PostgreSQL if needed..."
# Homebrew: try to start service (may fail in some environments; then run manually)
if command -v brew &>/dev/null; then
    for pkg in postgresql@16 postgresql@15 postgresql; do
        if brew list "$pkg" &>/dev/null 2>&1; then
            if brew services start "$pkg" 2>/dev/null; then
                echo "Waiting 8s for PostgreSQL to bind..."
                sleep 8
            else
                echo "Could not start PostgreSQL via brew services. If not running, run in your terminal: brew services start $pkg"
            fi
            break
        fi
    done
fi

echo "[3/4] Waiting for PostgreSQL to be ready..."
for i in $(seq 1 $MAX_TRY); do
    if command -v pg_isready &>/dev/null; then
        pg_isready -q 2>/dev/null && break
    fi
    if psql -d postgres -c "SELECT 1" &>/dev/null; then
        break
    fi
    if [ "$i" -eq $MAX_TRY ]; then
        echo "PostgreSQL가 준비되지 않았습니다."
        echo "먼저 터미널에서 실행하세요: brew services start postgresql@16"
        echo "그 다음 이 스크립트를 다시 실행하세요."
        exit 1
    fi
    [ $((i % 5)) -eq 0 ] && echo "  ... still waiting ($i/$MAX_TRY)"
    sleep 2
done
echo "PostgreSQL ready."

echo "[4/4] Creating database '$DB_NAME' and initializing Odoo base tables..."
cd "$ODOO_ROOT"
if [ ! -x "$VENV_PYTHON" ] || [ ! -f "$ODOO_BIN" ]; then
    echo "Odoo 가상환경 또는 odoo-bin을 찾을 수 없습니다. .venv와 odoo-bin이 있는지 확인하세요."
    exit 1
fi

ADDONS_PATH="$ODOO_ROOT/addons"
"$VENV_PYTHON" "$ODOO_BIN" --addons-path="$ADDONS_PATH" -d "$DB_NAME" --init base --stop-after-init

echo "Done. Database '$DB_NAME' is ready with Odoo base tables."
echo "Run Odoo with: $VENV_PYTHON $ODOO_BIN --addons-path=$ADDONS_PATH -d $DB_NAME"
echo ""
echo "Create PO 모듈 설치: $VENV_PYTHON $ODOO_BIN --addons-path=$ADDONS_PATH -d $DB_NAME -i sale_create_po --stop-after-init"
