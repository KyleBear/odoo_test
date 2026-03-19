#!/usr/bin/env bash
# Sale Create PO 모듈을 odoo_test DB에 설치합니다.
# 앱 목록에 모듈이 안 보일 때 이 스크립트로 설치한 뒤 서버를 다시 실행하세요.
#
# 사용법:
#   cd /Users/a1/Desktop/odoo_project/odoo
#   chmod +x scripts/install_sale_create_po.sh
#   ./scripts/install_sale_create_po.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ODOO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ADDONS_PATH="$ODOO_ROOT/addons"
DB_NAME="${1:-odoo_test}"
VENV_PYTHON="$ODOO_ROOT/.venv/bin/python"
ODOO_BIN="$ODOO_ROOT/odoo-bin"

cd "$ODOO_ROOT"
"$VENV_PYTHON" "$ODOO_BIN" --addons-path="$ADDONS_PATH" -d "$DB_NAME" -i sale_create_po --stop-after-init

echo "sale_create_po 설치 완료. 서버를 아래처럼 실행하세요:"
echo "  $VENV_PYTHON $ODOO_BIN --addons-path=$ADDONS_PATH -d $DB_NAME"
