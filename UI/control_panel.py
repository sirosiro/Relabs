from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                               QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout, QCheckBox, QSlider,
                               QRadioButton, QButtonGroup, QStackedWidget)
from PySide6.QtCore import Qt, Signal
from Core.data_model import Face
from Core.geometry_utils import calculate_center

# @intent:responsibility 数値入力とプロパティ編集を担当するウィジェット。
class ControlPanel(QWidget):
    # @intent:notification グリッド表示の切り替えを通知するシグナル
    grid_visibility_changed = Signal(bool)
    # @intent:notification ズームレベルの変更を通知するシグナル (値はカメラのZ位置)
    zoom_level_changed = Signal(float)

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

        # モード選択 (Face / Object)
        mode_layout = QHBoxLayout()
        self._radio_face = QRadioButton("Face Mode")
        self._radio_object = QRadioButton("Object Mode")
        self._radio_face.setChecked(True)
        
        self._mode_group = QButtonGroup(self)
        self._mode_group.addButton(self._radio_face)
        self._mode_group.addButton(self._radio_object)
        
        # モード切り替えイベント
        self._mode_group.buttonToggled.connect(self._on_mode_changed)
        
        mode_layout.addWidget(self._radio_face)
        mode_layout.addWidget(self._radio_object)
        layout.addLayout(mode_layout)

        # 表示設定エリア
        self._view_group = QGroupBox("View Settings")
        view_layout = QVBoxLayout()
        
        # Grid Checkbox
        self._check_grid = QCheckBox("Show Grid (Scale)")
        self._check_grid.toggled.connect(self.grid_visibility_changed.emit)
        view_layout.addWidget(self._check_grid)
        
        # Zoom Slider
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom:"))
        self._zoom_slider = QSlider(Qt.Orientation.Horizontal)
        # 範囲: -100 (遠い) ～ -2 (近い)
        self._zoom_slider.setRange(-100, -2)
        self._zoom_slider.setValue(-10) # 初期値
        self._zoom_slider.valueChanged.connect(self.zoom_level_changed.emit)
        zoom_layout.addWidget(self._zoom_slider)
        view_layout.addLayout(zoom_layout)
        
        self._view_group.setLayout(view_layout)
        layout.addWidget(self._view_group)

        # 編集エリア（スタック切り替え）
        self._editor_stack = QStackedWidget()
        
        # 1. Face Mode Editor (既存の頂点編集)
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
        self._editor_stack.addWidget(self._vertex_group)
        
        # 2. Object Mode Editor (重心移動)
        self._object_group = QGroupBox("Object Position (Center)")
        obj_layout = QFormLayout()
        
        self._obj_spinboxes = []
        for i, axis in enumerate(axes):
            spin = QDoubleSpinBox()
            spin.setRange(-1000.0, 1000.0)
            spin.setSingleStep(0.1)
            spin.setDecimals(2)
            
            # ラベル色
            label = QLabel(f"{axis}:")
            label.setStyleSheet(f"color: {axis_colors[i]}; font-weight: bold;")
            
            spin.valueChanged.connect(lambda val, a=i: self._on_object_pos_changed(a, val))
            self._obj_spinboxes.append(spin)
            obj_layout.addRow(label, spin)
            
        self._object_group.setLayout(obj_layout)
        self._editor_stack.addWidget(self._object_group)
        
        layout.addWidget(self._editor_stack)
        
        # 初期状態では無効化
        self._vertex_group.setEnabled(False)
        self._object_group.setEnabled(True) # Object Modeは常時有効（モデルがあれば）
        
        layout.addStretch()

    # @intent:operation モード切り替え時のUI更新を行います。
    def _on_mode_changed(self):
        is_object_mode = self._radio_object.isChecked()
        self._editor_stack.setCurrentIndex(1 if is_object_mode else 0)
        
        if is_object_mode:
            self._update_object_values()
            self._header_label.setText("Whole Object")
        else:
            # Faceモードに戻ったら選択状態を復元表示
            face = self._selection_manager.selected_face
            if face:
                self._header_label.setText(f"Face ID: {face.id[:8]}...")
                self._vertex_group.setEnabled(True)
                self._update_values_from_model()
            else:
                self._header_label.setText("No Selection")
                self._vertex_group.setEnabled(False)

    def _on_selection_changed(self, face):
        # 古いFaceの監視解除
        if self._current_face:
            self._current_face.remove_observer(self._on_face_data_changed)

        self._current_face = face
        
        # 新しいFaceの監視開始
        if face:
            face.add_observer(self._on_face_data_changed)

        # UI更新（モードによって振る舞いが違う）
        if self._radio_object.isChecked():
            self._update_object_values()
        else:
            if face:
                self._header_label.setText(f"Face ID: {face.id[:8]}...")
                self._vertex_group.setEnabled(True)
                self._update_values_from_model()
            else:
                self._header_label.setText("No Selection")
                self._vertex_group.setEnabled(False)

    def _on_face_data_changed(self, source):
        # モデル側の変更をUIに反映
        if self._radio_object.isChecked():
            self._update_object_values()
        else:
            self._update_values_from_model()

    # @intent:operation モデル全体の重心を計算し、UIに反映します。
    def _update_object_values(self):
        if not self._model.faces:
            self._object_group.setEnabled(False)
            return
            
        self._object_group.setEnabled(True)
        self._updating_ui = True
        try:
            # 重心計算 (Coreのロジックを使用)
            cx, cy, cz = calculate_center(self._model.faces)
            
            for i, val in enumerate([cx, cy, cz]):
                if self._obj_spinboxes[i].value() != val:
                    self._obj_spinboxes[i].setValue(val)
        finally:
            self._updating_ui = False

    # @intent:operation 重心座標の変更を検知し、全頂点を移動（Translate）させます。
    def _on_object_pos_changed(self, axis_idx, new_value):
        if self._updating_ui:
            return

        # 現在の重心を再計算（基準点）
        current_center = calculate_center(self._model.faces)
        current_val = current_center[axis_idx]
        
        # 差分移動量
        delta = new_value - current_val
        
        dx, dy, dz = 0.0, 0.0, 0.0
        if axis_idx == 0: dx = delta
        elif axis_idx == 1: dy = delta
        elif axis_idx == 2: dz = delta
        
        # モデル一括更新 (Coreのメソッドを使用)
        self._model.translate_all(dx, dy, dz)

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