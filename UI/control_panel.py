from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                               QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout)
from PySide6.QtCore import Qt
from Core.data_model import Face

# @intent:responsibility 数値入力とプロパティ編集を担当するウィジェット。
class ControlPanel(QWidget):
    def __init__(self, model, selection_manager, parent=None):
        super().__init__(parent)
        self._model = model
        self._selection_manager = selection_manager
        self._selection_manager.add_observer(self._on_selection_changed)
        
        self._current_face: Face = None
        self._spinboxes = [] # (vertex_index, axis_index, spinbox)
        self._updating_ui = False # 循環更新防止フラグ

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # ヘッダー
        self._header_label = QLabel("No Selection")
        self._header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._header_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self._header_label)

        # 頂点編集エリア
        self._vertex_group = QGroupBox("Vertex Coordinates (Absolute)")
        # 全体を縦に並べるレイアウト
        main_v_layout = QVBoxLayout()
        
        axes = ['X', 'Y', 'Z']
        # ギズモの色と合わせる (RGB)
        axis_colors = ["#ff3333", "#33ff33", "#3333ff"]
        
        for v_idx in range(4):
            # 各頂点の行を横並びにするレイアウト（ラベル + X + Y + Z）
            row_layout = QHBoxLayout()
            
            # ラベル (V0, V1...)
            label = QLabel(f"V{v_idx}")
            label.setFixedWidth(25)
            label.setStyleSheet("font-weight: bold;")
            row_layout.addWidget(label)
            
            for a_idx, axis in enumerate(axes):
                # 軸ラベル (X:, Y:, Z:) に色を適用
                axis_label = QLabel(f"{axis}:")
                axis_label.setStyleSheet(f"color: {axis_colors[a_idx]}; font-weight: bold;")
                row_layout.addWidget(axis_label)
                
                spin = QDoubleSpinBox()
                spin.setRange(-100.0, 100.0)
                spin.setSingleStep(0.1)
                spin.setDecimals(2)
                # サイズ調整（少しコンパクトに）
                spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons) # ボタンを消してスッキリさせる（お好みで）
                
                # 値変更時のハンドラ接続
                spin.valueChanged.connect(
                    lambda val, v=v_idx, a=a_idx: self._on_value_changed(v, a, val)
                )
                
                self._spinboxes.append(spin)
                row_layout.addWidget(spin)
            
            # 行レイアウトをメインレイアウトに追加
            main_v_layout.addLayout(row_layout)
                
        self._vertex_group.setLayout(main_v_layout)
        layout.addWidget(self._vertex_group)
        
        # 初期状態では無効化
        self._vertex_group.setEnabled(False)
        
        layout.addStretch()

    def _on_selection_changed(self, face):
        # 古いFaceの監視解除
        if self._current_face:
            self._current_face.remove_observer(self._on_face_data_changed)

        self._current_face = face
        
        if face:
            self._header_label.setText(f"Face ID: {face.id[:8]}...")
            self._vertex_group.setEnabled(True)
            # 新しいFaceの監視開始
            self._current_face.add_observer(self._on_face_data_changed)
            self._update_values_from_model()
        else:
            self._header_label.setText("No Selection")
            self._vertex_group.setEnabled(False)

    def _on_face_data_changed(self, source):
        # モデル側の変更をUIに反映
        self._update_values_from_model()

    # @intent:operation モデルのデータをUIに反映させます。
    # @intent:rationale 'spinBox.setValue' が 'valueChanged' シグナルを発火させるため、
    # '_updating_ui' フラグを使用して、UI更新中のイベントがモデル更新をトリガーしないように保護します（無限ループ防止）。
    def _update_values_from_model(self):
        if not self._current_face:
            return

        self._updating_ui = True
        try:
            for i, spin in enumerate(self._spinboxes):
                v_idx = i // 3
                a_idx = i % 3
                
                v = self._current_face.vertices[v_idx]
                val = 0.0
                if a_idx == 0: val = v.x
                elif a_idx == 1: val = v.y
                elif a_idx == 2: val = v.z
                
                if spin.value() != val:
                    spin.setValue(val)
        finally:
            self._updating_ui = False

    # @intent:operation ユーザーによるUI操作を検知し、モデルを更新します。
    def _on_value_changed(self, v_idx, a_idx, value):
        if self._updating_ui or not self._current_face:
            return

        # UIからの変更をモデルに反映
        vertex = self._current_face.vertices[v_idx]
        
        if a_idx == 0: vertex.x = value
        elif a_idx == 1: vertex.y = value
        elif a_idx == 2: vertex.z = value