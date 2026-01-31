# Service Module Architecture Manifest

## Part 1: Module Guide
このディレクトリ (`Service/`) は、データモデル (`Core`) とユーザーインターフェース (`UI`) の間を取り持つ**「アプリケーションロジック」**を格納します。
ドメインロジックのうち、状態を持たない処理や、複数のコンポーネントにまたがる調整役（Mediator）をここに配置します。

---

## Part 2: Module Content

### 1. 核となる原則 (Core Principles)
*   **Mediator**: ビューとモデル、あるいはビュー同士（ビューポートと操作パネル）の連携を仲介する。
*   **Business Logic**: データの入出力、変換、フィルタリングなどの複雑な処理をカプセル化する。

### 2. 主要なアーキテクチャ決定の記録 (Key Architectural Decisions)
<!--
Date: 2026-01-31
Decision: SelectionManagerの分離
Rationale: 「何が選択されているか」という状態はViewの状態に見えるが、複数のView（3D表示と数値パネル）で共有されるため、Viewから切り離してService層のMediatorとして実装した。
-->

### 3. AIとの協調に関する指針 (AI Collaboration Policy)
*   **状態のライフサイクル**: Serviceクラス（Manager等）が保持する状態が、アプリケーションのライフサイクルとどう同期するか（シングルトンか、都度生成か）を明確にすること。現状、`SelectionManager` は `Main` で生成され生存し続ける。

### 4. コンポーネント詳細 (Components)

#### 4.1. Selection Manager (`selection_manager.py`)
*   **役割**: アプリケーション内の「選択状態」を一元管理する Mediator。
*   **API**:
    *   `select_face(face)`: 選択状態を変更し、監視者に通知する。

#### 4.2. Exporter (`exporter.py`)
*   **役割**: モデルデータのファイル出力（XML生成）。
*   **設計意図**: 仕様の複雑性（出力範囲のフィルタリング、絶対/相対座標の変換）をUIコードから分離するため。
*   **ロジック**:
    *   **座標変換**: エクスポート実行時にオンデマンドで計算する（内部データは変更しない）。