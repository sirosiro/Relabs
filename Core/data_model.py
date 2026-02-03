from typing import List, Callable, Optional
import uuid

# @intent:responsibility データ変更を監視するための基底クラス。UIフレームワークに依存しないObserverパターンを提供します。
# @intent:warning 循環参照（Observer <-> Subject）に注意してください。Observerは自身のライフサイクル終了時に必ず remove_observer を呼び出す責務があります。
class Observable:
    def __init__(self):
        self._observers: List[Callable] = []

    def add_observer(self, callback: Callable):
        self._observers.append(callback)

    def remove_observer(self, callback: Callable):
        if callback in self._observers:
            self._observers.remove(callback)

    def notify_observers(self, *args, **kwargs):
        for callback in self._observers:
            callback(*args, **kwargs)

# @intent:responsibility 3D空間上の1点を表現します。
# @intent:lifecycle ModelまたはFaceに所有されますが、実体は共有される可能性があります。
class Vertex(Observable):
    def __init__(self, x: float, y: float, z: float):
        super().__init__()
        self._x = x
        self._y = y
        self._z = z

    # @intent:rationale プロパティ経由でのアクセスにより、変更時に自動的に通知を発火させます。
    @property
    def x(self) -> float: return self._x
    @x.setter
    def x(self, value: float):
        if self._x != value:
            self._x = value
            self.notify_observers(self)

    @property
    def y(self) -> float: return self._y
    @y.setter
    def y(self, value: float):
        if self._y != value:
            self._y = value
            self.notify_observers(self)

    @property
    def z(self) -> float: return self._z
    @z.setter
    def z(self, value: float):
        if self._z != value:
            self._z = value
            self.notify_observers(self)

    def __repr__(self):
        return f"Vertex({self._x}, {self._y}, {self._z})"

# @intent:responsibility 4つの頂点からなる「面」を定義します。
# @intent:invariant 常に4つの頂点を持ち、反時計回りの順序（左下->右下->右上->左上）であることを期待します。
class Face(Observable):
    def __init__(self, vertices: List[Vertex], face_id: Optional[str] = None):
        super().__init__()
        if len(vertices) != 4:
            raise ValueError("A Face must consist of exactly 4 vertices.")
        self._vertices = vertices
        self._id = face_id or str(uuid.uuid4())
        
        # 頂点の変更もFaceの変更として通知する
        for v in self._vertices:
            v.add_observer(self._on_vertex_changed)

    def _on_vertex_changed(self, vertex: Vertex):
        self.notify_observers(self)

    @property
    def id(self) -> str:
        return self._id

    @property
    def vertices(self) -> List[Vertex]:
        return self._vertices

    # @intent:operation 頂点リストを更新します。数は4つでなければなりません。
    def update_vertices(self, new_vertices: List[Vertex]):
        if len(new_vertices) != 4:
            raise ValueError("A Face must consist of exactly 4 vertices.")
        
        # 古い監視を解除
        for v in self._vertices:
            v.remove_observer(self._on_vertex_changed)
            
        self._vertices = new_vertices
        
        # 新しい監視を追加
        for v in self._vertices:
            v.add_observer(self._on_vertex_changed)
            
        self.notify_observers(self)

# @intent:responsibility 3Dモデリング空間全体の状態（全ての面）を管理します。
# @intent:role Single Source of Truth. アプリケーション全体で唯一のモデルインスタンスとして扱われることを想定しています。
class Model(Observable):
    def __init__(self):
        super().__init__()
        self._faces: List[Face] = []

    @property
    def faces(self) -> List[Face]:
        return self._faces

    # @intent:operation 新しい面を追加します。
    def add_face(self, face: Face):
        self._faces.append(face)
        face.add_observer(self._on_face_changed)
        self.notify_observers(self)

    # @intent:operation 面を削除します。
    def remove_face(self, face: Face):
        if face in self._faces:
            face.remove_observer(self._on_face_changed)
            self._faces.remove(face)
            self.notify_observers(self)

    def _on_face_changed(self, face: Face):
        self.notify_observers(self)

    # @intent:operation 全てのデータをクリアします。
    def clear(self):
        for face in self._faces:
            face.remove_observer(self._on_face_changed)
        self._faces.clear()
        self.notify_observers(self)

    # @intent:operation 全ての頂点を指定された量だけ移動させます。
    # @intent:rationale パフォーマンスとUIの応答性を維持するため、このメソッドはObserver通知の最適化に責任を持つ。
    # 個々のVertex.setter経由で更新すると、頂点の数だけ通知が飛び、UIの再描画が大量に発生する。
    # このメソッドは、全頂点の内部変数を直接更新し、最後にModelとして一度だけ通知することで、これを回避する。
    # このアプローチはVertexのカプセル化を意図的に破るが、許容可能なトレードオフと判断した。
    def translate_all(self, dx: float, dy: float, dz: float):
        # 頂点の内部変数を直接更新することで、個別の通知を抑制する。
        for face in self._faces:
            for v in face.vertices:
                v._x += dx
                v._y += dy
                v._z += dz
                
        # モデル全体としての変更を一度だけ通知する。
        self.notify_observers(self)
