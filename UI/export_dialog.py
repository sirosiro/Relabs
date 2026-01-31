from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QRadioButton, 
                               QDialogButtonBox, QFormLayout, QDoubleSpinBox, QWidget)
from Core.data_model import Vertex

# @intent:responsibility エクスポート時の条件（範囲、座標系、基準点）をユーザーに入力させるモーダルダイアログ。
class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export XML")
        self.resize(300, 200)
        
        layout = QVBoxLayout(self)
        
        # Scope Selection
        self._scope_group = QGroupBox("Export Scope")
        scope_layout = QVBoxLayout()
        self._radio_all = QRadioButton("All Models")
        self._radio_selection = QRadioButton("Selected Face Only")
        self._radio_all.setChecked(True)
        scope_layout.addWidget(self._radio_all)
        scope_layout.addWidget(self._radio_selection)
        self._scope_group.setLayout(scope_layout)
        layout.addWidget(self._scope_group)
        
        # Coordinate Mode Selection
        self._coord_group = QGroupBox("Coordinate System")
        coord_layout = QVBoxLayout()
        self._radio_absolute = QRadioButton("Absolute Coordinates")
        self._radio_relative = QRadioButton("Relative to Reference Point")
        self._radio_absolute.setChecked(True)
        coord_layout.addWidget(self._radio_absolute)
        coord_layout.addWidget(self._radio_relative)
        self._coord_group.setLayout(coord_layout)
        layout.addWidget(self._coord_group)
        
        # Reference Point Input
        self._ref_widget = QWidget()
        ref_layout = QFormLayout(self._ref_widget)
        self._ref_x = QDoubleSpinBox()
        self._ref_y = QDoubleSpinBox()
        self._ref_z = QDoubleSpinBox()
        for spin in [self._ref_x, self._ref_y, self._ref_z]:
            spin.setRange(-1000, 1000)
        ref_layout.addRow("Ref X:", self._ref_x)
        ref_layout.addRow("Ref Y:", self._ref_y)
        ref_layout.addRow("Ref Z:", self._ref_z)
        self._ref_widget.setEnabled(False) # Default disabled
        layout.addWidget(self._ref_widget)
        
        # Toggle reference input
        self._radio_relative.toggled.connect(self._ref_widget.setEnabled)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # @intent:operation UIの状態を集約し、ロジック層（Exporter）が利用しやすい形式で返却します。
    def get_settings(self):
        scope = 'all' if self._radio_all.isChecked() else 'selection'
        mode = 'absolute' if self._radio_absolute.isChecked() else 'relative'
        ref_point = Vertex(self._ref_x.value(), self._ref_y.value(), self._ref_z.value())
        return scope, mode, ref_point
