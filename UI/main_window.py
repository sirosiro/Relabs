from PySide6.QtWidgets import (QMainWindow, QSplitter, QMenuBar, QMenu, 
                               QFileDialog, QMessageBox)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from UI.viewport import Viewport
from UI.control_panel import ControlPanel
from UI.export_dialog import ExportDialog
from Service.exporter import Exporter

# @intent:responsibility アプリケーションのメインウィンドウ構造を定義します。
# @intent:role コンポーネント（Viewport, ControlPanel）のコンテナであり、依存性注入のエントリーポイントとして機能します。
class MainWindow(QMainWindow):
    def __init__(self, model, selection_manager):
        super().__init__()
        self._model = model
        self._selection_manager = selection_manager
        
        self.setWindowTitle("Relabs 3D Modeler")
        self.resize(1024, 768)
        
        self._init_menu()
        
        # 左右分割レイアウト
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左：3Dビューポート
        self.viewport = Viewport(model, selection_manager)
        splitter.addWidget(self.viewport)
        
        # 右：コントロールパネル
        self.control_panel = ControlPanel(model, selection_manager)
        splitter.addWidget(self.control_panel)
        
        # 初期分割比率
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        self.setCentralWidget(splitter)

    # @intent:operation メニューバーを構築し、ファイル操作などのアクションを定義します。
    def _init_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        
        export_action = QAction("Export XML...", self)
        export_action.triggered.connect(self._show_export_dialog)
        file_menu.addAction(export_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    # @intent:operation エクスポートダイアログを表示し、ユーザー設定に基づいてファイル出力処理を調整します。
    def _show_export_dialog(self):
        dialog = ExportDialog(self)
        if dialog.exec():
            scope, mode, ref_point = dialog.get_settings()
            
            # Selection Scopeのバリデーション
            if scope == 'selection' and not self._selection_manager.selected_face:
                QMessageBox.warning(self, "Export Error", "No face selected for export.")
                return

            filepath, _ = QFileDialog.getSaveFileName(self, "Save XML", "", "XML Files (*.xml)")
            if filepath:
                try:
                    exporter = Exporter(self._model)
                    exporter.export_xml(filepath, scope, mode, ref_point, 
                                      self._selection_manager.selected_face)
                    QMessageBox.information(self, "Success", "Export completed successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")