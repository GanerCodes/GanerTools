import numpy as np
from PIL import Image
import moderngl_window, moderngl
import os

os.environ['DISPLAY'] = ':0'

class Renderer(moderngl_window.WindowConfig):
    window_size = 1920, 1080
    aspect_ratio = 1
    def generate_vao(self):
        self.vao = self.ctx.simple_vertex_array(
            self.ctx.program(
                vertex_shader="""\
                    #version 400
                    in vec2 in_vert;
                    out vec2 pos;
                    void main() {
                        gl_Position = vec4(in_vert, 0.0, 1.0);
                        pos = in_vert;
                    }""",
                fragment_shader=f"""\
                    #version 400
                    in vec2 pos;
                    {Renderer.shader}"""
            ),
            self.ctx.buffer(
                np.array([-1,-1,-1,1,1,-1,1,1]).astype('f4')),
            'in_vert')
    
    def __init__(self, **kwargs):
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
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
        self.ctx.finish()

        image = Image.frombytes('RGBA',
            Renderer.window_size,
            self.wnd.fbo.read(components=4))
        image.save(Renderer.filename, format='png')

        self.wnd.close()

BLOCK = """\
#define ret return
#define f float
#define v2 vec2
#define v3 vec3
#define v4 vec4
#define len length
#define PI 3.14159265359
#define TWO_PI 6.28318530718
float sq(float x){return x*x;}
float angle(vec2 p){return atan(p.g,p.r);}
float angle_between(vec2 p1,vec2 p2){return atan(p2.g-p1.g,p2.r-p1.r);}
float pml(float x,float a,float b){float t=abs(b-a);return mod(-x*sign(mod(floor(x/t),2.0)-0.5),t)+a;}
vec2 ptc(float d,float a){return vec2(d*cos(a),d*sin(a));}
vec3 hsv(vec3 c){vec4 K=vec4(0.0,-1.0/3.0,2.0/3.0,-1.0),p=mix(vec4(c.bg,K.ab),vec4(c.gb,K.rg),step(c.b,c.g)),q=mix(vec4(p.rga,c.r),vec4(c.r,p.gbr),step(p.r,c.r));float d=q.r-min(q.a,q.g),e=1e-10;return vec3(abs(q.b+(q.a-q.g)/(6.0*d+e)),d/(q.r+e),q.r);}
vec3 rgb(vec3 c){vec4 K=vec4(1.0,0.66666,0.33333,3.0);vec3 p=abs(fract(c.rrr+K.rgb)*6.0-K.aaa);return c.b*mix(K.rrr,p-K.rrr,c.g);}"""

# Renderer.exec("""
# MAIN:
# ret v4(abs(p.x),abs(p.y),0,1);
# """, "output.png")