# Service Module Architecture Manifest

## Part 1: Module Guide
このディレクトリ (`Service/`) は、データモデル (`Core`) とユーザーインターフェース (`UI`) の間を取り持つ**「アプリケーションロジック」**を格納します。
ドメインロジックのうち、状態を持たない処理や、複数のコンポーネントにまたがる調整役（Mediator）をここに配置します。

---

## Part 2: Module Content

### 1. 核となる原則 (Core Principles)
*   **Mediator**: ビューとモデル、あるいはビュー同士（ビューポートと操作パネル）の連携を仲介し、直接的な結合を防ぐ。
*   **Business Logic Encapsulation**: データの入出力、変換、フィルタリングなどの複雑な処理をカプセル化し、UI層にロジックを漏洩させない。
*   **Stateless Services**: `Exporter` のような処理サービスは、原則として状態を持たず（あるいは実行時のみ一時的に持ち）、副作用（Side Effects）を最小限に抑える。

### 2. 主要なアーキテクチャ決定の記録 (Key Architectural Decisions)
<!--
Date: 2026-02-04
Decision: 座標変換ロジックのExporterへの配置
Rationale: 相対座標での出力機能が必要だが、これをCoreモデル自体に持たせるとモデルの状態管理が複雑化する。
そのため、モデルは常に「絶対座標」のみを保持し、Exporterがファイル書き出し時にオンデマンドで座標変換計算を行う設計とした。
これにより、データの「正」の状態を汚染することなく出力要件を満たしている。

Date: 2026-01-31
Decision: SelectionManagerの分離
Rationale: 「何が選択されているか」という状態はViewの状態に見えるが、複数のView（3D表示と数値パネル）で共有され同期する必要がある。
View間の密結合を避けるため、この状態を管理する責務をService層のMediatorとして切り出した。
-->

### 3. AIとの協調に関する指針 (AI Collaboration Policy)
*   **依存関係の方向**: `Service` -> `Core` は許可される。`Core` -> `Service` は禁止される（循環依存防止）。
*   **シングルトンの扱い**: `SelectionManager` は実質的なシングルトン（アプリケーションスコープ）として扱われるべきだが、実装上は `Main` で生成され依存性注入されるインスタンスである。グローバル変数としてのアクセスは避けること。

### 4. コンポーネント詳細 (Components)

#### 4.1. Selection Manager (`selection_manager.py`)
*   **責務**: アプリケーション内の「選択状態」を一元管理する Mediator。
*   **状態**: 現在は「単一の面 (`Face`)」または「選択なし (`None`)」のみを管理する。複数選択は未サポート。
*   **API**:
    *   `select_face(face: Face | None)`: 選択状態を更新し、登録されたObserverに通知する。
    *   `add_observer(callback)` / `remove_observer(callback)`: 変更通知の購読管理。

#### 4.2. Exporter (`exporter.py`)
*   **責務**: モデルデータをXML形式でファイルに出力する。
*   **ロジック**:
    *   **Scope Filtering**: 全体出力 (`all`) か、選択部分のみ (`selection`) かを制御する。
    *   **Coordinate Transformation**: 出力モード (`absolute` / `relative`) に応じて、頂点座標を計算し直して出力する。基準点 (`ReferencePoint`) の指定もサポートする。
