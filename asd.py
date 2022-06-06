import moderngl
from PIL import Image

ctx = moderngl.create_context(standalone=True, backend='egl')
fbo = ctx.simple_framebuffer((1000, 1000))
fbo.use()

# draw stuff
fbo.clear(1, 0, 0, 1)

# dump screenshot
image = Image.frombytes('RGBA', fbo.size, fbo.read(components=4))
image.save("fbo.png", format='png')

ctx.release()