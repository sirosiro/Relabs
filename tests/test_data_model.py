import unittest
from unittest.mock import Mock
from Core.data_model import Vertex, Face, Model

class TestDataModel(unittest.TestCase):
    def test_vertex_update_notification(self):
        """Vertexの座標変更がObserverに通知されるかテスト"""
        v = Vertex(0, 0, 0)
        observer = Mock()
        v.add_observer(observer)

        v.x = 1.0
        observer.assert_called_with(v)
        
        observer.reset_mock()
        v.y = 2.0
        observer.assert_called_with(v)

        observer.reset_mock()
        v.z = 3.0
        observer.assert_called_with(v)

        # 値が変わらない場合は通知されないこと
        observer.reset_mock()
        v.x = 1.0
        observer.assert_not_called()

    def test_face_initialization(self):
        """Faceが正しく初期化されるか、不正な頂点数でエラーになるかテスト"""
        vertices = [Vertex(0,0,0) for _ in range(4)]
        face = Face(vertices)
        self.assertEqual(len(face.vertices), 4)

        # 3つの頂点ではエラー
        with self.assertRaises(ValueError):
            Face([Vertex(0,0,0) for _ in range(3)])

    def test_face_bubble_notification(self):
        """Vertexの変更がFaceを通して通知されるか（バブルアップ）テスト"""
        vertices = [Vertex(0,0,0) for _ in range(4)]
        face = Face(vertices)
        
        observer = Mock()
        face.add_observer(observer)

        # 頂点の座標を変更
        vertices[0].x = 10.0
        
        # FaceのObserverが呼ばれるはず
        observer.assert_called_with(face)

    def test_model_management(self):
        """ModelへのFace追加・削除と通知のテスト"""
        model = Model()
        observer = Mock()
        model.add_observer(observer)

        vertices = [Vertex(0,0,0) for _ in range(4)]
        face = Face(vertices)

        # 追加
        model.add_face(face)
        observer.assert_called_with(model)
        self.assertIn(face, model.faces)

        # 頂点変更によるModelへの通知波及
        observer.reset_mock()
        vertices[0].y = 5.0
        observer.assert_called_with(model)

        # 削除
        observer.reset_mock()
        model.remove_face(face)
        observer.assert_called_with(model)
        self.assertNotIn(face, model.faces)

if __name__ == '__main__':
    unittest.main()
