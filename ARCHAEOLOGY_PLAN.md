# Archaeology Plan for Relabs

## 1. ドメイン特定 (Domain Identification)
*   **プロジェクト名**: Relabs
*   **ドメイン**: デスクトップアプリケーション（3Dモデリングツール）
*   **技術スタック**: Python 3.x, PySide6 (Qt), OpenGL (Legacy/Fixed Pipeline)
*   **目的**: 簡易的な3D形状（現在は立方体ベース）の作成、編集、およびXML形式へのエクスポート。

## 2. マニフェスト配置マップ (Manifest Placement Map)
既存のフラクタル構造は適切であるため維持し、新たにテスト領域へのマニフェスト配置を提案します。

```text
.
├── ARCHITECTURE_MANIFEST.md (Root: 全体原則とモジュール間連携)
├── Core/
│   └── ARCHITECTURE_MANIFEST.md (Core: 純粋なデータモデルと幾何計算)
├── Service/
│   └── ARCHITECTURE_MANIFEST.md (Service: アプリケーションロジックとMediator)
├── UI/
│   └── ARCHITECTURE_MANIFEST.md (UI: プレゼンテーションとユーザー入力)
└── tests/
    └── ARCHITECTURE_MANIFEST.md (Tests: [新規] テスト戦略とカバレッジ方針)
```

## 3. 各階層の推定責務と更新方針 (Estimated Responsibilities & Update Strategy)

### Root (`.`)
*   **責務**: アプリケーションのエントリーポイント、依存関係の構成（Wiring）。
*   **更新方針**: グローバルな原則（MVC分離など）の再確認と、新規追加する `tests` モジュールへの参照追加。

### Core (`./Core`)
*   **責務**: UI/Qtに依存しない純粋なデータモデル (`Vertex`, `Face`, `Model`) と数学的計算 (`GeometryUtils`)。
*   **更新方針**:
    *   `Observable` パターンの実装詳細とメモリ管理（循環参照リスク）についての記述強化。
    *   `data_model` におけるオブジェクトの所有権（Ownership）の明文化。

### Service (`./Service`)
*   **責務**: UIとCoreの仲介 (`SelectionManager`)、外部フォーマット変換 (`Exporter`)。
*   **更新方針**:
    *   `SelectionManager` が持つ状態（選択リスト）のライフサイクル定義。
    *   `Exporter` の出力仕様と座標系変換ルールの明文化。

### UI (`./UI`)
*   **責務**: ユーザーへの視覚的フィードバック（OpenGL描画）、入力イベントの捕捉とコマンドへの変換。
*   **更新方針**:
    *   QtイベントループとOpenGL描画更新のタイミングに関する記述。
    *   ユーザー操作（マウスドラッグ等）と座標変換ロジックの分離境界の明確化。

### Tests (`./tests`) **[新規]**
*   **責務**: Coreロジックの正当性検証。
*   **更新方針**:
    *   「何をテストし、何をテストしないか（例：UI描画はテスト対象外）」の境界定義。
    *   テストデータの生成方針。

---

この計画に基づき、各ディレクトリのソースコード解析とマニフェストの更新（再発掘）を実行します。
