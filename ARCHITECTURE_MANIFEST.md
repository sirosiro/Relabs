# AI協調開発アーキテクチャ憲章 (Architecture Manifest)

## Part 1: このマニフェストの取扱説明書 (Guide)

### 1. 目的 (Purpose)
このドキュメントは、Python製3Dモデリングツール開発における「北極星」となるルート定義書です。
プロジェクト全体に適用される普遍的な原則を定義し、詳細仕様は各モジュールのサブマニフェストに委譲する「フラクタル構成」を採用しています。

### 2. 憲章の書き方 (Guidelines)
*   **具体的に:** 「使いやすいUI」ではなく、「数値入力と3D操作は相互に遅延なく同期する」と記述します。
*   **参照の原則:** 詳細な実装仕様はここには書かず、必ず `path/to/module/ARCHITECTURE_MANIFEST.md` を参照するように記述します。

---

## Part 2: マニフェスト本体 (Content)

### 1. 核となる原則 (Core Principles)

<!-- 原則: Single Source of Truth (信頼できる唯一の情報源) -->
*   データの実体は `Core` モジュールのみが持つ。UIは常にその「投影」であり、独自のデータコピーを持たない。

<!-- 原則: 内部表現の正規化 (Canonical Internal Representation) -->
*   内部モデルは常に「ワールド絶対座標」として保持する。相対座標などの変換は、表示・入力・出力の境界（Boundary）で行う。

<!-- 原則: 疎結合な連携 -->
*   各モジュール間は `Observer` パターンや `Dependency Injection` を通じて連携し、直接的な相互依存を避ける。

### 2. モジュール構成とマニフェストマップ (Module Map)

本プロジェクトは以下の3つの主要モジュールで構成されています。詳細な仕様はリンク先を参照してください。

*   **Core Module** (`./Core/`)
    *   [Core/ARCHITECTURE_MANIFEST.md](./Core/ARCHITECTURE_MANIFEST.md)
    *   **責務:** 純粋なデータモデル、幾何計算ロジック。UI非依存。
    
*   **UI Module** (`./UI/`)
    *   [UI/ARCHITECTURE_MANIFEST.md](./UI/ARCHITECTURE_MANIFEST.md)
    *   **責務:** プレゼンテーション、ユーザー入力、OpenGLレンダリング。
    
*   **Service Module** (`./Service/`)
    *   [Service/ARCHITECTURE_MANIFEST.md](./Service/ARCHITECTURE_MANIFEST.md)
    *   **責務:** アプリケーションロジック、Mediator（選択管理）、Exporter。

### 3. 主要なアーキテクチャ決定の記録 (Key Architectural Decisions)

<!--
Date: 2026-01-31
Decision: GUIフレームワークとして PySide6 (Qt) を採用。
Rationale: 仕様にある「数値入力と3D表示の同期」を実装するため、堅牢なイベントループとOpenGLウィジェットが必要だったため。

Date: 2026-01-31
Decision: Observerパターンの自前実装 (Core.Observable)。
Rationale: CoreモジュールをQt (`QObject`) に依存させず、純粋なPythonクラスとして保つことで、テスト容易性と再利用性を高めるため。
-->

### 4. AIとの協調に関する指針 (AI Collaboration Policy)

*   **変更の波及:** コードを変更する際は、必ず該当するディレクトリの `ARCHITECTURE_MANIFEST.md` を確認し、その原則に違反していないか確認すること。
*   **マニフェストの保守:** 新しいモジュールを追加する場合や、責務が大きく変わる場合は、このルートマニフェストおよびサブマニフェストを更新すること。