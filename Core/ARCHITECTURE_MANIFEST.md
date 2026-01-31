# Core Module Architecture Manifest

## Part 1: Module Guide
このディレクトリ (`Core/`) は、アプリケーションの心臓部となる**「純粋なデータモデルと計算ロジック」**を格納します。
ここに配置されるコードは、UIフレームワーク（PySide6など）に一切依存してはならず、単体テストが容易でなければなりません。

---

## Part 2: Module Content

### 1. 核となる原則 (Core Principles)
*   **Single Source of Truth**: アプリケーションの状態（3Dモデルデータ）を一元管理する。
*   **変更通知**: データの変更を監視者（UI等）に能動的に通知する仕組みを提供する。
*   **幾何計算**: レンダリングやUIに依存しない、純粋数学的な計算（交差判定など）を提供する。

### 2. 主要なアーキテクチャ決定の記録 (Key Architectural Decisions)
<!--
Date: 2026-01-31
Decision: Observerパターンの独自実装 (Observable)
Rationale: PySide6のSignal/Slot機構は強力だが、CoreモジュールがGUIライブラリに依存することを避けるため、純粋なPythonによる軽量な通知機構を採用した。
-->

### 3. AIとの協調に関する指針 (AI Collaboration Policy)
*   **依存関係の監視**: `import PySide6` や `import OpenGL` がこのモジュール内のファイルに含まれていないか、常に監視すること。
*   **純粋関数**: `geometry_utils.py` などの計算ロジックは、副作用を持たない純粋関数として実装し、テストを容易にすること。

### 4. コンポーネント詳細 (Components)

#### 4.1. Data Model (`data_model.py`)
*   **`Observable`**:
    *   **役割**: Observerパターンの基底クラス。UIフレームワークに依存しない軽量なイベント通知機構。
*   **`Vertex`**:
    *   **役割**: 3D空間の点 (x, y, z)。プロパティ変更時に自動通知を行う。
*   **`Face`**:
    *   **役割**: 4つの頂点を持つ面。
    *   **設計意図**: 頂点の変更イベントをバブルアップ（再通知）し、Face自体の変更として扱う。
*   **`Model`**:
    *   **役割**: 全てのFaceを保持するルートコンテナ。

#### 4.2. Geometry Utils (`geometry_utils.py`)
*   **役割**: 3D空間におけるレイキャスティング等の計算ロジック。
*   **関数**:
    *   `ray_intersects_face`: レイと四角形の交差判定（Möller–Trumboreアルゴリズムを使用）。