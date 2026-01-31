import math
from typing import Optional, Tuple
from Core.data_model import Vertex, Face

# @intent:responsibility 幾何学的な計算ロジックを提供します。

def dot_product(v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> float:
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def cross_product(v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return (
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0]
    )

def sub_vectors(v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return (v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2])

# @intent:algorithm Möller–Trumbore intersection algorithm
# レイの原点(origin)、方向(dir)、三角形の3頂点(v0, v1, v2)を受け取り、交差距離tを返します。交差しない場合はNone。
def ray_intersects_triangle(
    origin: Tuple[float, float, float],
    direction: Tuple[float, float, float],
    v0: Tuple[float, float, float],
    v1: Tuple[float, float, float],
    v2: Tuple[float, float, float]
) -> Optional[float]:
    epsilon = 1e-6
    edge1 = sub_vectors(v1, v0)
    edge2 = sub_vectors(v2, v0)
    h = cross_product(direction, edge2)
    a = dot_product(edge1, h)

    if -epsilon < a < epsilon:
        return None  # レイと並行

    f = 1.0 / a
    s = sub_vectors(origin, v0)
    u = f * dot_product(s, h)

    if u < 0.0 or u > 1.0:
        return None

    q = cross_product(s, edge1)
    v = f * dot_product(direction, q)

    if v < 0.0 or u + v > 1.0:
        return None

    t = f * dot_product(edge2, q)

    if t > epsilon:
        return t
    return None

# @intent:operation レイとFace(四角形)の交差判定を行います。
# Faceは2つの三角形(0-1-2, 0-2-3)として扱います。
# 最も近い交点までの距離を返します。交差しない場合はNone。
def ray_intersects_face(
    origin: Tuple[float, float, float],
    direction: Tuple[float, float, float],
    face: Face
) -> Optional[float]:
    vs = [(v.x, v.y, v.z) for v in face.vertices]
    
    # Triangle 1: 0-1-2
    t1 = ray_intersects_triangle(origin, direction, vs[0], vs[1], vs[2])
    
    # Triangle 2: 0-2-3
    t2 = ray_intersects_triangle(origin, direction, vs[0], vs[2], vs[3])
    
    if t1 is not None and t2 is not None:
        return min(t1, t2)
    if t1 is not None:
        return t1
    if t2 is not None:
        return t2
    return None

# @intent:operation 指定されたFaceリストに含まれる全頂点の重心（平均座標）を計算します。
# @intent:return (x, y, z) のタプル。頂点が存在しない場合は (0.0, 0.0, 0.0) を返します。
def calculate_center(faces: list[Face]) -> Tuple[float, float, float]:
    total_x, total_y, total_z = 0.0, 0.0, 0.0
    count = 0
    
    for face in faces:
        for v in face.vertices:
            total_x += v.x
            total_y += v.y
            total_z += v.z
            count += 1
            
    if count == 0:
        return (0.0, 0.0, 0.0)
        
    return (total_x / count, total_y / count, total_z / count)
