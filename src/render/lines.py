import numpy as np
from pyrr import quaternion as q, Quaternion, Vector3, Matrix44
from render.shaders import Shaders
import moderngl
from typing import List, Tuple

MAX_LINE_BUFFER_SIZE = 2400


def build_lines(lines: List[Tuple[Matrix44, Matrix44]]) -> Tuple[np.ndarray, np.ndarray]:
    vertices = []
    indices = []
    index_counter = 0

    for line in lines:
        start, end = line
        vertices.extend(start)
        vertices.extend(end)

        indices.append(index_counter)
        indices.append(index_counter + 1)

        index_counter += 2

    vertex_data = np.array(vertices, dtype=np.float32)
    index_data = np.array(indices, dtype=np.uint32)

    return vertex_data, index_data


class Lines:
    def __init__(self, app, lineWidth: int = 1, color=None, lines=None) -> None:
        if lines is None:
            lines = []
        if color is None:
            color = [1, 0, 0, 1]
        self.app = app
        self.lineWidth = lineWidth
        self.color = color
        programs = Shaders.instance()
        self.line_prog = programs.get('lines')
        self.lines = lines

        vertices, indices = build_lines(lines)

        self.vbo = self.app.ctx.buffer(reserve=MAX_LINE_BUFFER_SIZE, dynamic=True)
        self.ibo = self.app.ctx.buffer(reserve=MAX_LINE_BUFFER_SIZE, dynamic=True)

        self.vbo.write(vertices)
        self.ibo.write(indices)

        self.vao = self.app.ctx.simple_vertex_array(self.line_prog, self.vbo, "position", index_buffer=self.ibo)

        self.translation = Vector3()
        self.rotation = Quaternion()
        self.scale = Vector3([1.0, 1.0, 1.0])

    def update(self, lines: List[Tuple[Matrix44, Matrix44]]) -> None:
        vertices, indices = build_lines(lines)
        self.vbo.clear()
        self.ibo.clear()
        self.vbo.write(vertices)
        self.ibo.write(indices)

    def get_model_matrix(self) -> np.ndarray:
        trans = Matrix44.from_translation(self.translation)
        rot = Matrix44.from_quaternion(self.rotation)
        scale = Matrix44.from_scale(self.scale)
        model = trans * rot * scale

        return np.array(model, dtype='f4')

    def draw(self, proj_matrix: Matrix44, view_matrix: Matrix44) -> None:

        self.line_prog["img_width"].value = self.app.window_size[0]
        self.line_prog["img_height"].value = self.app.window_size[1]
        self.line_prog["line_thickness"].value = self.lineWidth

        self.line_prog['model'].write(self.get_model_matrix())
        self.line_prog['view'].write(view_matrix)
        self.line_prog['projection'].write(proj_matrix)
        self.line_prog['color'].value = self.color

        self.vao.render(moderngl.LINES)
