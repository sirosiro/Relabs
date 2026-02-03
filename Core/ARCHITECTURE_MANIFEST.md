# Core Module Architecture Manifest

## Part 1: Module Guide
このディレクトリ (`Core/`) は、アプリケーションの心臓部となる**「純粋なデータモデルと計算ロジック」**を格納します。
ここに配置されるコードは、UIフレームワーク（PySide6など）に一切依存してはならず、単体テストが容易でなければなりません。

---

## Part 2: Module Content

### 1. 核となる原則 (Core Principles)
*   **Single Source of Truth**: アプリケーションの状態（3Dモデルデータ）を一元管理する。UIはデータのコピーを持たず、常にこのモデルを参照する。
*   **能動的な変更通知**: データモデルは自身の変更を検知し、`Observable` パターンを用いて監視者（UI等）に通知する責務を持つ。
*   **純粋な計算ロジック**: 幾何計算は状態を持たない純粋関数として実装し、入力のみから出力を決定する。

### 2. 主要なアーキテクチャ決定の記録 (Key Architectural Decisions)
<!--
Date: 2026-02-04
Decision: 通知ストーム回避のためのカプセル化の意図的なバイパス
Rationale: `Model.translate_all` において、全ての頂点を移動させる際、個々の `Vertex` プロパティ経由で更新すると数千回の再描画イベントが発生しUIがフリーズする。
これを防ぐため、同メソッド内では `Vertex` のプライベートメンバ (`_x`, `_y`, `_z`) を直接操作し、最後に `Model` から一度だけ通知を発行する最適化を採用した。
これは「カプセル化」よりも「パフォーマンスとUX」を優先した結果である。

Date: 2026-01-31
Decision: Observerパターンの独自実装 (Observable)
Rationale: PySide6のSignal/Slot機構は強力だが、CoreモジュールがGUIライブラリに依存することを避けるため、純粋なPythonによる軽量な通知機構を採用した。
-->

### 3. AIとの協調に関する指針 (AI Collaboration Policy)
*   **依存関係の監視**: `import PySide6` や `import OpenGL` がこのモジュール内のファイルに含まれていないか、常に監視すること。
*   **循環参照の防止**: `Observable` パターンは循環参照（Observer <-> Subject）を引き起こしやすい。リスナー登録解除の責務を呼び出し側が負うことを徹底すること。

### 4. コンポーネント詳細 (Components)

#### 4.1. Data Model (`data_model.py`)
*   **`Observable`**:
    *   **責務**: 軽量なイベント通知機構。
    *   **API契約**:
        *   `add_observer(callback)`: コールバックは強参照で保持される。
        *   `remove_observer(callback)`: 購読者は自身のライフサイクル終了時に必ずこれを呼び出し、メモリリークを防ぐ義務がある。

*   **`Vertex`**:
    *   **責務**: 空間上の点 (x, y, z) の保持と変更通知。
    *   **通知**: プロパティ (`x`, `y`, `z`) への代入時に `notify_observers(self)` を発火。

*   **`Face`**:
    *   **責務**: 4つの頂点の管理とイベントバブリング。
    *   **制約**: 頂点数は常に4（四角形）。
    *   **イベント伝播**: 構成要素である `Vertex` の変更を検知し、自身の変更として再通知する。

*   **`Model`**:
    *   **責務**: 全ての `Face` を保持するルートコンテナ。
    *   **データ構造**: Faceのリスト（Polygon Soup）。頂点共有や位相情報（トポロジー）は持たない。
    *   **API**:
        *   `translate_all(dx, dy, dz)`: 全頂点を移動し、通知を1回に集約して発行する。

#### 4.2. Geometry Utils (`geometry_utils.py`)
*   **責務**: ステートレスな幾何計算関数群。
*   **関数**:
    *   `ray_intersects_face(origin, dir, face) -> float | None`:
        *   **アルゴリズム**: Möller–Trumbore法を使用。Faceを2つの三角形に分割して判定し、近い方の距離を返す。
    *   `calculate_center(faces) -> (x, y, z)`:
        *   **仕様**: 指定されたFace群に含まれる全頂点の算術平均を返す。空リストの場合は `(0,0,0)`。
