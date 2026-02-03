# AI協調開発アーキテクチャ憲章 (Architecture Manifest)

## Part 1: このマニフェストの取扱説明書 (Guide)

### 1. 目的 (Purpose)
このドキュメントは、Python製3Dモデリングツール開発における「北極星」となるルート定義書です。
プロジェクト全体に適用される普遍的な原則を定義し、詳細仕様は各モジュールのサブマニフェストに委譲する「フラクタル構成」を採用しています。

### 2. 憲章の書き方 (Guidelines)
*   **具体的に:** 「使いやすいUI」ではなく、「数値入力と3D操作は相互に遅延なく同期する」と記述します。
*   **参照の原則:** 詳細な実装仕様はここには書かず、必ず `path/to/module/ARCHITECTURE_MANIFEST.md` を参照するように記述します。

### 3. リスクと対策 (Risks and Mitigations)
*   **リスク: ドキュメントの陳腐化**
    *   **対策:** コードの構造変更（ファイル追加、クラス移動）を行う際は、必ず対応する `ARCHITECTURE_MANIFEST.md` の更新をコミットの必須条件とします。
*   **リスク: パフォーマンスと抽象化の衝突**
    *   **対策:** パフォーマンス要件が抽象化（カプセル化）を妨げる場合、そのトレードオフをマニフェストの「主要なアーキテクチャ決定」セクションに明記した上で、例外的な最適化を許可します（例：Coreの `translate_all`）。

---

## Part 2: マニフェスト本体 (Content)

### 1. 核となる原則 (Core Principles)

<!-- 原則: Single Source of Truth (信頼できる唯一の情報源) -->
*   データの実体は `Core` モジュールのみが持つ。UIやServiceは常にその「投影」であり、独自のデータコピーを持たない。

<!-- 原則: 依存性の方向 (Dependency Direction) -->
*   依存関係は `UI` -> `Service` -> `Core` の方向にのみ流れる。`Core` が `UI` を参照することは（型ヒントを除き）厳禁とする。

<!-- 原則: 内部表現の正規化 (Canonical Internal Representation) -->
*   内部モデルは常に「ワールド絶対座標」として保持する。相対座標などの変換は、表示・入力・出力の境界（Boundary）で行う。

### 2. モジュール構成とマニフェストマップ (Module Map)

本プロジェクトは以下の4つの主要モジュールで構成されています。詳細な仕様はリンク先を参照してください。

*   **Core Module** (`./Core/`)
    *   [Core/ARCHITECTURE_MANIFEST.md](./Core/ARCHITECTURE_MANIFEST.md)
    *   **責務:** 純粋なデータモデル、幾何計算ロジック。UI非依存。
    
*   **Service Module** (`./Service/`)
    *   [Service/ARCHITECTURE_MANIFEST.md](./Service/ARCHITECTURE_MANIFEST.md)
    *   **責務:** アプリケーションロジック、Mediator（選択管理）、Exporter。
    
*   **UI Module** (`./UI/`)
    *   [UI/ARCHITECTURE_MANIFEST.md](./UI/ARCHITECTURE_MANIFEST.md)
    *   **責務:** プレゼンテーション、ユーザー入力、OpenGLレンダリング。

*   **Tests Module** (`./tests/`)
    *   [tests/ARCHITECTURE_MANIFEST.md](./tests/ARCHITECTURE_MANIFEST.md)
    *   **責務:** Coreロジックの正当性検証、リグレッション防止。

### 3. 主要なアーキテクチャ決定の記録 (Key Architectural Decisions)

<!--
Date: 2026-01-31
Decision: GUIフレームワークとして PySide6 (Qt) を採用。
Rationale: 仕様にある「数値入力と3D表示の同期」を実装するため、堅牢なイベントループとOpenGLウィジェットが必要だったため。

Date: 2026-02-04
Decision: テスト戦略の定義
Rationale: UIテストのコスト対効果が低いため、自動テストのスコープを `Core` ロジックの検証に集中させ、UIは手動検証とする方針を決定した。
-->

### 4. AIとの協調に関する指針 (AI Collaboration Policy)

*   **変更の波及:** コードを変更する際は、必ず該当するディレクトリの `ARCHITECTURE_MANIFEST.md` を確認し、その原則に違反していないか確認すること。
*   **インテント・コメント:** 生成するコードには、実装の「理由」や「責務」を説明する `@intent` タグ付きコメントを付与し、設計意図をコードに残すこと。
