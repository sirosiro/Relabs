# Tests Module Architecture Manifest

## Part 1: Module Guide
このディレクトリ (`tests/`) は、アプリケーションの品質を保証するための自動テストコードを格納します。
我々のテスト戦略は「ピラミッド型」ではなく、ドメインロジックの堅牢性に焦点を当てた「ロジック中心型」です。

---

## Part 2: Module Content

### 1. 核となる原則 (Core Principles)
*   **Core Logic First**: `Core` および `Service` モジュールの純粋なロジック（計算、データ構造、状態遷移）は、高いカバレッジでユニットテストされなければならない。
*   **UI is Out of Scope**: `UI` モジュールの描画ロジック（OpenGL）やウィジェットの挙動は、ユニットテストの対象外とする。これらは変更頻度が高く、自動化コストに見合わないため、動作確認は手動またはE2Eテストに委譲する。
*   **Isolation**: 各テストケースは独立しており、実行順序に依存してはならない。外部リソース（ファイルシステム等）へのアクセスは可能な限りMock化する。

### 2. 主要なアーキテクチャ決定の記録 (Key Architectural Decisions)
<!--
Date: 2026-02-04
Decision: unittestフレームワークの採用
Rationale: Python標準ライブラリであり、外部依存なしで実行可能であるため。pytest等の導入は、必要性が生じた段階で検討する。

Date: 2026-02-04
Decision: Observer通知のMock検証
Rationale: データモデルの変更通知が正しく連鎖（Bubble up）しているかを確認するため、`unittest.mock.Mock` をObserverとして登録し、呼び出し回数と引数を検証する手法を標準とする。
-->

### 3. AIとの協調に関する指針 (AI Collaboration Policy)
*   **テスト駆動の推奨**: Coreモジュールに新しいロジックを追加する際は、可能な限りテストコードを先に（あるいは同時に）生成すること。
*   **回帰テストの追加**: バグ修正を行う際は、そのバグを再現するテストケースを必ず追加し、修正後にパスすることを確認すること。

### 4. テストスイート構成 (Test Suite Structure)

#### 4.1. Unit Tests (`test_*.py`)
*   **`test_data_model.py`**:
    *   **対象**: `Core.data_model`
    *   **検証項目**:
        *   プロパティ変更時の `notify_observers` の発火。
        *   値が変化しない場合の通知抑制。
        *   `Face` 構築時の不変条件チェック（頂点数4）。
        *   `Vertex` -> `Face` -> `Model` のイベント伝播（Bubbling）。
