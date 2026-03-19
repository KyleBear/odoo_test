# Sale Create Purchase Order

판매 주문에 **Create PO** 버튼을 추가합니다. 클릭 시 제품 공급업체별로 구매 오더를 생성합니다(B안).

## 설치 방법

### 1) 앱에서 설치 (권장)

1. Odoo를 **addons 경로를 지정해서** 실행했는지 확인하세요.
2. **Apps** → 오른쪽 상단 **⋮** → **Update Apps List**
3. 검색창에 **"Sale Create"** 또는 **"Create PO"** 입력
4. **Sale Create Purchase Order** → **Install**

### 2) 앱 목록에 안 보일 때 (명령줄 설치)

프로젝트 루트의 `addons` 폴더가 Odoo addons 경로에 없으면 앱 목록에 모듈이 나타나지 않습니다. 이 경우 아래처럼 **같은 addons 경로**를 주고 명령줄로 설치하세요.

```bash
cd /Users/a1/Desktop/odoo_project/odoo
.venv/bin/python odoo-bin --addons-path=./addons -d odoo_test -i sale_create_po --stop-after-init
```

또는 스크립트 사용:

```bash
./scripts/install_sale_create_po.sh
```

설치 후 서버를 **반드시 같은 옵션**으로 다시 실행하세요:

```bash
.venv/bin/python odoo-bin --addons-path=./addons -d odoo_test
```

## 왜 앱 목록에 안 보이나요?

- Odoo는 **--addons-path**에 지정된 폴더만 앱으로 불러옵니다.
- `odoo-bin -d odoo_test`처럼 경로 없이 실행하면, 기본 경로만 사용되어 프로젝트의 `./addons`가 포함되지 않을 수 있습니다.
- 그래서 **항상** `--addons-path=./addons`(또는 절대 경로)를 넣어 실행해야 이 모듈이 보이고 설치할 수 있습니다.

## 사용

판매 주문(견적/주문) 폼 상단 버튼 영역에 **Create PO**가 표시됩니다. 클릭 시 해당 주문 라인을 공급업체별로 묶어 구매 오더를 생성합니다.
