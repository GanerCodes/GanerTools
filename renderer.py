import moderngl
from array import array
from PIL import Image
import os

os.environ['DISPLAY'] = ':0'

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

vertex_shader = """\
#version 330
in vec2 in_vert;
void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
}"""

def parse_shader(q, size):
    return f"""\
#version 330
#define HALF_RES vec2({0.5*size[0]}, {0.5*size[1]})
#define TWO_INV_MIN_RES {2.0/min(size)}
{BLOCK}\n
{q[:(l:=q.find('MAIN:'))]}\n
out vec4 fragColor;
vec3 func(vec2 p) {{
    {q[l+5:]}
}}
void main() {{
    gl_FragColor = vec4(func(TWO_INV_MIN_RES*(gl_FragCoord.xy - HALF_RES)), 1.0);
}}"""

def render(shader, filename="output.png", size=(1000, 1000)):
    shader = parse_shader(shader, size)
    
    ctx = moderngl.create_context(standalone=True, backend='egl')
    fbo = ctx.simple_framebuffer(size)
    fbo.use()

    vao = ctx.vertex_array(ctx.program(
        vertex_shader=vertex_shader,
        fragment_shader=shader
    ), ctx.buffer(data=array('f', [1,1,-1,1,-1,-1,1,1,1,-1,-1,-1])), "in_vert")

    fbo.clear()
    vao.render(mode=moderngl.TRIANGLES)

    image = Image.frombytes('RGBA', fbo.size, fbo.read(components=4))
    image.save(filename, format='png')

    ctx.release()

if __name__ == "__main__":
    render("MAIN:\nret v3(abs(p.x),abs(p.y),0);", "output.png")