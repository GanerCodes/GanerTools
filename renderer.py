import numpy as np
from PIL import Image
import moderngl_window, moderngl
import os

os.environ['DISPLAY'] = ':0'

BLOCK = """"""

vertex_shader = """\
#version 330
in vec2 in_vert;
out vec2 pos;
void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    pos = in_vert;
}"""

fragment_shader = "#version 330\nin vec2 pos;\n{}"

class Renderer(moderngl_window.WindowConfig):
    window_size = 1024, 1024
    aspect_ratio = 1
    def generate_vao(self):
        self.vao = self.ctx.simple_vertex_array(
            self.ctx.program(
                vertex_shader=vertex_shader,
                fragment_shader=fragment_shader.format(Renderer.shader)),
            
            self.ctx.buffer(
                np.array([ 1, 1,
                          -1, 1,
                          -1,-1,
                           
                           1, 1,
                           1,-1,
                          -1,-1]).astype('f4')),
            'in_vert')
    
    def __init__(self, **kwargs):
        kwargs['ctx'] = moderngl.create_context(standalone=True, backend='egl')
        super().__init__(**kwargs)
        self.generate_vao()
    
    def parse_shader(q):
        body = f"""\
        vec4 func(vec2 p) {{
            {q[(l:=q.find('MAIN:'))+5:]}
        }}
        void main() {{
            gl_FragColor = func(pos);
        }}"""
        head = q[:l]

        return f"""{BLOCK}\n{head}\n{body}"""
    
    def exec(shader, filename="output.png"):
        Renderer.filename = filename
        Renderer.shader = Renderer.parse_shader(shader)
        moderngl_window.run_window_config(Renderer)
    
    def render(self, time, frame_time):
        self.ctx.clear(0, 0, 0, 0)
        self.vao.render(mode=moderngl.TRIANGLES)
        self.ctx.finish()

        image = Image.frombytes('RGBA',
            Renderer.window_size,
            self.wnd.fbo.read(components=4))
        image.save(Renderer.filename, format='png')

        self.wnd.close()

if __name__ == "__main__":
    Renderer.exec("MAIN:\nreturn vec4(abs(p.x),abs(p.y),0,1);", "output.png")