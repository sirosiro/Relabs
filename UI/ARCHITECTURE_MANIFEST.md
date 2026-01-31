# UI Module Architecture Manifest

## Part 1: Module Guide
このディレクトリ (`UI/`) は、ユーザーとの対話を担当するプレゼンテーション層です。
`PySide6` (Qt) をフレームワークとして採用し、ユーザーの操作を解釈して `Core` や `Service` に伝達し、その結果を視覚化します。

---

## Part 2: Module Content

### 1. 核となる原則 (Core Principles)
*   **View**: モデルの状態をユーザーに提示する（3D描画、数値表示）。
*   **Controller**: ユーザー入力を受け取り、モデルやサービスの更新メソッドを呼び出す。
*   **Layout**: ウィンドウやウィジェットの配置管理。

### 2. 主要なアーキテクチャ決定の記録 (Key Architectural Decisions)
<!--
Date: 2026-01-31
Decision: OpenGL固定機能パイプラインの採用
Rationale: 現在の要件（単純な立方体の表示）に対し、シェーダーベースの実装はコード量と複雑さが増すため、開発速度と可読性を優先して固定機能 (`glBegin`/`glEnd`) を採用した。将来的に複雑化した場合はVBO/Shaderへの移行を検討する。

Date: 2026-01-31
Decision: 高DPI対応 (devicePixelRatio)
Rationale: Mac Retinaディスプレイ等でクリック判定がずれる問題に対処するため、論理ピクセルから物理ピクセルへの変換ロジックをViewportに組み込んだ。
-->

### 3. AIとの協調に関する指針 (AI Collaboration Policy)
*   **メインスレッド保護**: ファイル入出力や重い計算を行う際は、UIをフリーズさせないよう注意すること。
*   **リソース管理**: OpenGLリソースやQtウィジェットは、PythonのGCだけでなく、親ウィジェットの破棄や明示的な終了処理が必要な場合があることに留意すること。

### 4. コンポーネント詳細 (Components)

#### 4.1. Main Window (`main_window.py`)
*   **役割**: アプリケーションのシェル。レイアウトと依存性注入のエントリーポイント。

#### 4.2. 3D Viewport (`viewport.py`)
*   **役割**: OpenGLを用いた3Dモデルのレンダリングとマウス操作。
*   **実装詳細**:
    *   **ギズモ**: 2Dオーバーレイとして座標軸を描画。

#### 4.3. Control Panel (`control_panel.py`)
*   **役割**: 選択された面の数値編集。
*   **UX**: 頂点ごとにグループ化し、X/Y/Zを色分けして表示（ギズモと対応）。
*   **循環参照防止**: `_updating_ui` フラグによる保護。

#### 4.4. Dialogs
*   **`ExportDialog`**: エクスポート設定の入力フォーム。