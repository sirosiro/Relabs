# UI Module Architecture Manifest

## Part 1: Module Guide
このディレクトリ (`UI/`) は、ユーザーとの対話を担当するプレゼンテーション層です。
`PySide6` (Qt) をフレームワークとして採用し、ユーザーの操作を解釈して `Core` や `Service` に伝達し、その結果を視覚化します。

---

## Part 2: Module Content

### 1. 核となる原則 (Core Principles)
*   **View & Controller**: UIコンポーネントは、モデルの状態を表示する(View)だけでなく、ユーザー入力を受け取りモデルを更新する(Controller)役割も担う。
*   **Loose Coupling (Signal/Slot)**: コンポーネント間（例：ViewportとControlPanel）の直接参照を避け、QtのSignal/Slot機構、またはMediator (`SelectionManager`) を介して連携する。
*   **Main Thread Only**: UIの描画更新やOpenGLコンテキストへのアクセスは、必ずメインスレッド（GUIスレッド）で行われなければならない。

### 2. 主要なアーキテクチャ決定の記録 (Key Architectural Decisions)
<!--
Date: 2026-02-04
Decision: 無限ループ防止フラグ (_updating_ui) の導入
Rationale: `ControlPanel` において、Modelからの変更通知を受けてUIを更新すると、ウィジェットの `valueChanged` シグナルが発火し、再度Modelを更新しようとする循環（無限ループ）が発生する。
これを防ぐため、プログラムによるUI値変更中はフラグを立ててシグナル処理をブロックするガード機構を実装した。

Date: 2026-02-04
Decision: 高DPI (Retina) 対応のための物理座標変換
Rationale: 近年の高解像度ディスプレイでは論理ピクセルと物理ピクセルが一致しない。
OpenGL (`glViewport`, `glReadPixels`) は物理ピクセルを扱うため、マウスイベント（論理ピクセル）との間で座標変換が必要となる。
`Viewport` クラス内で `devicePixelRatio` を用いた補正ロジックを実装し、クリック判定のズレを解消した。

Date: 2026-01-31
Decision: OpenGL固定機能パイプラインの採用
Rationale: 現在の要件（単純な立方体の表示）に対し、シェーダーベースの実装はコード量と複雑さが増すため、開発速度と可読性を優先して固定機能 (`glBegin`/`glEnd`) を採用した。
-->

### 3. AIとの協調に関する指針 (AI Collaboration Policy)
*   **メインスレッド保護**: ファイル入出力や重い計算を行う際は、UIをフリーズさせないよう注意すること（必要であれば別スレッド化を検討するが、現状の規模では同期処理で許容されている）。
*   **Qtリソース管理**: ウィジェットの親子関係（`parent`引数）を適切に設定し、PythonのGC任せにせずQtのオブジェクトツリーによるメモリ管理を活用すること。

### 4. コンポーネント詳細 (Components)

#### 4.1. Main Window (`main_window.py`)
*   **責務**: アプリケーションのシェル。レイアウト構築と依存性注入のエントリーポイント。
*   **Wiring**: `Viewport` と `ControlPanel` のインスタンス生成時に、共有の `Model` と `SelectionManager` を注入する。また、コンポーネント間のQtシグナル（例：ズーム変更）を接続する。

#### 4.2. 3D Viewport (`viewport.py`)
*   **責務**: OpenGLを用いた3Dレンダリングと、マウス入力によるカメラ操作・オブジェクト選択。
*   **実装詳細**:
    *   **Raycasting**: マウス座標を3Dレイに逆投影し、Coreの `ray_intersects_face` を使用して選択判定を行う。
    *   **Rendering**: `paintGL` メソッド内で、モデル描画、グリッド描画、ギズモ（座標軸）描画を順次行う。

#### 4.3. Control Panel (`control_panel.py`)
*   **責務**: 選択された要素のプロパティ編集、および表示設定の管理。
*   **編集モード**:
    *   **Face Mode**: 選択された `Face` の頂点を直接編集する。
    *   **Object Mode**: モデル全体の重心を計算・表示し、その変更差分を `Model.translate_all` に適用することで擬似的なオブジェクト移動を実現する。
