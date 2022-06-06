import moderngl
from array import array
from PIL import Image

ctx = moderngl.create_context(standalone=True, backend='egl')
fbo = ctx.simple_framebuffer((1000, 1000))
fbo.use()

vao = ctx.vertex_array(ctx.program(
    vertex_shader="""
    #version 330
    in vec2 in_vert;
    void main() {
        gl_Position = vec4(in_vert, 0.0, 1.0);
    }
    """,
    fragment_shader="""
    #version 330
    out vec4 fragColor;
    void main() {
        fragColor = vec4(gl_FragCoord.xy / 1000.0, 0.0, 1.0);
    }
    """,
), ctx.buffer(data=array('f', [1, 1, -1, 1, -1, -1, 1, 1, 1, -1, -1, -1])), "in_vert")

fbo.clear()
vao.render(mode=moderngl.TRIANGLES)

image = Image.frombytes('RGBA', fbo.size, fbo.read(components=4))
image.save("fbo.png", format='png')

ctx.release()