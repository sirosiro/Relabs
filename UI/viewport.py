from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
from Core.data_model import Face
from Core.geometry_utils import ray_intersects_face

# @intent:responsibility 3Dレンダリングとカメラ操作を担当します。
class Viewport(QOpenGLWidget):
    def __init__(self, model, selection_manager, parent=None):
        super().__init__(parent)
        self._model = model
        self._model.add_observer(self._on_model_changed)
        
        self._selection_manager = selection_manager
        self._selection_manager.add_observer(self._on_selection_changed)
        
        # カメラの状態
        self._cam_rot_x = 0.0
        self._cam_rot_y = 0.0
        self._last_mouse_pos = QPoint()
        self._press_pos = QPoint() # クリック判定用
        self._zoom = -10.0
        
        # レイキャスティング用のキャッシュ
        self._last_modelview = None
        self._last_projection = None
        self._last_viewport = None

    def _on_model_changed(self, source):
        self.update()

    def _on_selection_changed(self, selected_face):
        self.update()

    def initializeGL(self):
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if h == 0: h = 1
        gluPerspective(45, w / h, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # カメラ変換
        glTranslatef(0.0, 0.0, self._zoom)
        glRotatef(self._cam_rot_x, 1.0, 0.0, 0.0)
        glRotatef(self._cam_rot_y, 0.0, 1.0, 0.0)
        
        # 行列情報の保存（レイキャスティング用）
        # @intent:rationale mousePressEventなどのイベントハンドラ内ではOpenGLコンテキストが保証されないため、
        # 描画ループ内で計算済みの行列を取得・キャッシュし、クリック判定に使用します。
        self._last_modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        self._last_projection = glGetDoublev(GL_PROJECTION_MATRIX)
        self._last_viewport = glGetIntegerv(GL_VIEWPORT)
        
        selected_face = self._selection_manager.selected_face

        # モデルの描画
        glBegin(GL_QUADS)
        for face in self._model.faces:
            # 選択されている面は赤色、それ以外はグレー
            if face == selected_face:
                glColor3f(1.0, 0.2, 0.2)
            else:
                glColor3f(0.8, 0.8, 0.8)
            
            for v in face.vertices:
                glVertex3f(v.x, v.y, v.z)
        glEnd()
        
        # ワイヤーフレーム
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(2.0)
        glColor3f(0.0, 0.0, 0.0)
        
        glBegin(GL_QUADS)
        for face in self._model.faces:
            for v in face.vertices:
                glVertex3f(v.x, v.y, v.z)
        glEnd()
        
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)

        # 座標軸インジケータの描画 (Overdraw)
        self._draw_axes_indicator()

    def _draw_axes_indicator(self):
        # 現在の投影行列等を保存
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        # 2D描画用の正射影 (左下が0,0)
        w, h = self.width(), self.height()
        glOrtho(0, w, 0, h, -100, 100)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # 左下 (60, 60) に配置
        glTranslatef(60, 60, 0)
        
        # メインカメラの回転を適用
        glRotatef(self._cam_rot_x, 1.0, 0.0, 0.0)
        glRotatef(self._cam_rot_y, 0.0, 1.0, 0.0)
        
        axis_len = 40.0
        tip_size = 4.0
        
        glDisable(GL_DEPTH_TEST) # 重なりを気にせず描画
        glLineWidth(2.0)

        # 軸とチップを描画するヘルパー
        def draw_axis(vector, color):
            glColor3fv(color)
            # 軸の線
            glBegin(GL_LINES)
            glVertex3f(0, 0, 0)
            glVertex3f(vector[0]*axis_len, vector[1]*axis_len, vector[2]*axis_len)
            glEnd()
            
            # 先端のボックス (ギズモっぽさ)
            glPushMatrix()
            glTranslatef(vector[0]*axis_len, vector[1]*axis_len, vector[2]*axis_len)
            s = tip_size
            glBegin(GL_QUADS)
            # 小さな立方体を描画
            glVertex3f(-s,-s, s); glVertex3f( s,-s, s); glVertex3f( s, s, s); glVertex3f(-s, s, s)
            glVertex3f(-s,-s,-s); glVertex3f(-s, s,-s); glVertex3f( s, s,-s); glVertex3f( s,-s,-s)
            glVertex3f(-s, s,-s); glVertex3f(-s, s, s); glVertex3f( s, s, s); glVertex3f( s, s,-s)
            glVertex3f(-s,-s,-s); glVertex3f( s,-s,-s); glVertex3f( s,-s, s); glVertex3f(-s,-s, s)
            glVertex3f( s,-s,-s); glVertex3f( s, s,-s); glVertex3f( s, s, s); glVertex3f( s,-s, s)
            glVertex3f(-s,-s,-s); glVertex3f(-s,-s, s); glVertex3f(-s, s, s); glVertex3f(-s, s,-s)
            glEnd()
            glPopMatrix()

        # X軸 (赤)
        draw_axis((1, 0, 0), (1.0, 0.2, 0.2))
        # Y軸 (緑)
        draw_axis((0, 1, 0), (0.2, 1.0, 0.2))
        # Z軸 (青)
        draw_axis((0, 0, 1), (0.2, 0.2, 1.0))
        
        glEnable(GL_DEPTH_TEST)
        
        # 行列復帰
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def mousePressEvent(self, event):
        self._last_mouse_pos = event.position().toPoint()
        self._press_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        dx = event.position().toPoint().x() - self._last_mouse_pos.x()
        dy = event.position().toPoint().y() - self._last_mouse_pos.y()

        if event.buttons() & Qt.MouseButton.LeftButton:
            self._cam_rot_y += dx * 0.5
            self._cam_rot_x += dy * 0.5
            self.update()

        self._last_mouse_pos = event.position().toPoint()

    def mouseReleaseEvent(self, event):
        # クリック判定（移動距離が小さい場合のみ）
        dist = (event.position().toPoint() - self._press_pos).manhattanLength()
        if dist < 5:
            self._perform_raycast(event.position().toPoint())

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self._zoom += delta * 0.01
        self.update()

    # @intent:operation クリック位置から3D空間へのレイを飛ばし、交差する面を特定します。
    def _perform_raycast(self, pos):
        if self._last_modelview is None:
            print("Debug: ModelView matrix is not ready.")
            return

        # 高DPI対応: 論理ピクセルを物理ピクセルに変換
        # @intent:rationale Retinaディスプレイ等ではOSの座標系とOpenGLのバッファ解像度が異なるため、
        # devicePixelRatioを用いて物理ピクセル座標に補正する必要があります。
        ratio = self.devicePixelRatio()
        x = pos.x() * ratio
        # OpenGLのY軸は下から上。ビューポートの高さも考慮して反転
        y = self._last_viewport[3] - (pos.y() * ratio)

        print(f"Debug: Click at logical({pos.x()}, {pos.y()}) -> physical({x}, {y})")

        try:
            # Near平面上の点
            near_pt = gluUnProject(x, y, 0.0, 
                                 self._last_modelview, 
                                 self._last_projection, 
                                 self._last_viewport)
            # Far平面上の点
            far_pt = gluUnProject(x, y, 1.0, 
                                self._last_modelview, 
                                self._last_projection, 
                                self._last_viewport)
            
            origin = near_pt
            # 方向ベクトルの正規化
            direction = (far_pt[0]-near_pt[0], far_pt[1]-near_pt[1], far_pt[2]-near_pt[2])
            length = (direction[0]**2 + direction[1]**2 + direction[2]**2)**0.5
            direction = (direction[0]/length, direction[1]/length, direction[2]/length)

            # 最も近い交差面を探す
            min_dist = float('inf')
            hit_face = None

            for face in self._model.faces:
                dist = ray_intersects_face(origin, direction, face)
                if dist is not None and dist < min_dist:
                    min_dist = dist
                    hit_face = face

            if hit_face:
                print(f"Debug: Hit face {hit_face.id}")
            else:
                print("Debug: No face hit.")

            self._selection_manager.select_face(hit_face)
            
        except Exception as e:
            print(f"Raycast error: {e}")
