import sys
from PySide6.QtWidgets import QApplication
from UI.main_window import MainWindow
from Core.data_model import Model, Face, Vertex
from Service.selection_manager import SelectionManager

def main():
    app = QApplication(sys.argv)
    
    # 唯一のモデルインスタンスを生成
    model = Model()
    
    # 選択状態管理マネージャの生成
    selection_manager = SelectionManager()
    
    # 初期データの投入: 原点に1つの立方体の面を追加 (テスト用)
    # @intent:rationale 現状のプロトタイプでは、頂点インスタンスは面ごとに独立して生成されており、共有されていない。
    # これは最もシンプルな実装だが、トポロジー情報（どの頂点がどの面と隣接しているか）が失われる。
    # このため、頂点単位でのスムーズな変形（例：1つの角を動かすと隣接する面が追従する）はできない。
    # この制約を回避しオブジェクト全体を操作するため、UI側に「Object Mode」が導入された。
    # 将来的な機能拡張（頂点編集など）の際には、頂点共有（Vertex Pool）の導入を検討する必要がある。
    # 前面
    model.add_face(Face([
        Vertex(-1, -1, 1), Vertex(1, -1, 1), Vertex(1, 1, 1), Vertex(-1, 1, 1)
    ], "front"))
    # 背面
    model.add_face(Face([
        Vertex(1, -1, -1), Vertex(-1, -1, -1), Vertex(-1, 1, -1), Vertex(1, 1, -1)
    ], "back"))
    # 上面
    model.add_face(Face([
        Vertex(-1, 1, 1), Vertex(1, 1, 1), Vertex(1, 1, -1), Vertex(-1, 1, -1)
    ], "top"))
    # 下面
    model.add_face(Face([
        Vertex(-1, -1, -1), Vertex(1, -1, -1), Vertex(1, -1, 1), Vertex(-1, -1, 1)
    ], "bottom"))
    # 右面
    model.add_face(Face([
        Vertex(1, -1, 1), Vertex(1, -1, -1), Vertex(1, 1, -1), Vertex(1, 1, 1)
    ], "right"))
    # 左面
    model.add_face(Face([
        Vertex(-1, -1, -1), Vertex(-1, -1, 1), Vertex(-1, 1, 1), Vertex(-1, 1, -1)
    ], "left"))
    
    # メインウィンドウの作成と表示
    window = MainWindow(model, selection_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
