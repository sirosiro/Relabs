import xml.etree.ElementTree as ET
from typing import List, Optional
from Core.data_model import Model, Face, Vertex

# @intent:responsibility モデルデータをXML形式でエクスポートするサービス。
# @intent:role 座標系の変換やフィルタリングのロジックをカプセル化します。
class Exporter:
    def __init__(self, model: Model):
        self._model = model

    # @intent:operation 指定された条件に基づいてXMLを生成し、ファイルに保存します。
    def export_xml(self, filepath: str, 
                   scope: str = 'all', # 'all' or 'selection'
                   coordinate_mode: str = 'absolute', # 'absolute' or 'relative'
                   reference_point: Vertex = None,
                   selected_face: Optional[Face] = None):
        
        root = ET.Element("ModelingData")
        
        # エクスポート設定のメタデータ記録
        settings_elem = ET.SubElement(root, "ExportSettings")
        ET.SubElement(settings_elem, "Scope").text = scope
        ET.SubElement(settings_elem, "CoordinateMode").text = coordinate_mode
        
        ref_x, ref_y, ref_z = 0.0, 0.0, 0.0
        if coordinate_mode == 'relative' and reference_point:
            ref_elem = ET.SubElement(settings_elem, "ReferencePoint")
            ref_elem.set("x", str(reference_point.x))
            ref_elem.set("y", str(reference_point.y))
            ref_elem.set("z", str(reference_point.z))
            ref_x, ref_y, ref_z = reference_point.x, reference_point.y, reference_point.z

        models_elem = ET.SubElement(root, "Models")
        
        # 出力対象の面を決定
        target_faces = []
        if scope == 'selection' and selected_face:
            target_faces = [selected_face]
        else:
            target_faces = self._model.faces

        # モデルデータの構築
        # 今回は単一のModelコンテナとして出力する構造とする
        model_elem = ET.SubElement(models_elem, "Model", id="main_model")

        for i, face in enumerate(target_faces):
            face_elem = ET.SubElement(model_elem, "Face", id=face.id)
            
            for v_idx, v in enumerate(face.vertices):
                # 座標変換ロジック
                # 絶対座標モードならそのまま、相対座標モードなら基準点を引く
                x = v.x - ref_x
                y = v.y - ref_y
                z = v.z - ref_z
                
                ET.SubElement(face_elem, "Vertex", 
                              index=str(v_idx), 
                              x=str(x), y=str(y), z=str(z))

        # XML書き出し
        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ", level=0)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
