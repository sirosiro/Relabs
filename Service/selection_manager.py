from typing import Optional, List, Callable
from Core.data_model import Face

# @intent:responsibility アプリケーション内の「選択状態」を管理します。
# @intent:role Mediator pattern. ViewportとControlPanelの間の同期を取ります。
class SelectionManager:
    def __init__(self):
        self._selected_face: Optional[Face] = None
        self._observers: List[Callable] = []

    @property
    def selected_face(self) -> Optional[Face]:
        return self._selected_face

    # @intent:operation 面を選択します。Noneを渡すと選択解除になります。
    def select_face(self, face: Optional[Face]):
        if self._selected_face != face:
            self._selected_face = face
            self._notify_observers()

    def add_observer(self, callback: Callable):
        self._observers.append(callback)

    def remove_observer(self, callback: Callable):
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self):
        for callback in self._observers:
            callback(self._selected_face)
