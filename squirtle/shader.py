import ctypes

from pyglet import gl

activeShader = None


class Shader(object):
    """An OpenGL shader object"""

    def __init__(self, shader_type, name="(unnamed shader)"):
        self.shaderObject = gl.glCreateShaderObjectARB(shader_type)
        self.name = name
        self.program = None

    def __del__(self):
        if self.program:
            try:
                self.program.detachShader(self)
            except ImportError:
                # Python loudly "ignores" this error on shutdown - explicitly ignore here
                pass
            self.program = None

        try:
            gl.glDeleteShader(self.shaderObject)
        except ImportError:
            # Python loudly "ignores" this error on shutdown - explicitly ignore here
            pass

    def source(self, source_string):
        c = ctypes
        buff = c.create_string_buffer(source_string)
        c_text = c.cast(c.pointer(c.pointer(buff)),
                        c.POINTER(c.POINTER(gl.GLchar)))
        gl.glShaderSourceARB(self.shaderObject, 1, c_text, None)

    def compileShader(self):
        gl.glCompileShader(self.shaderObject)
        rval = ctypes.c_long()
        gl.glGetObjectParameterivARB(self.shaderObject, gl.GL_OBJECT_COMPILE_STATUS_ARB, ctypes.pointer(rval))
        if rval:
            print(f"{self.name} compiled successfuly.")
        else:
            print(f"Compile failed on shader {self.name}: ")
            self.printInfoLog()

    def infoLog(self):
        c = ctypes
        infoLogLength = c.c_long()
        gl.glGetObjectParameterivARB(self.shaderObject,
                                     gl.GL_OBJECT_INFO_LOG_LENGTH_ARB,
                                     ctypes.pointer(infoLogLength))
        buffer = c.create_string_buffer(infoLogLength.value)
        c_text = c.cast(c.pointer(buffer),
                        c.POINTER(gl.GLchar))
        gl.glGetInfoLogARB(self.shaderObject, infoLogLength.value, None, c_text)
        return c.string_at(c_text)

    def printInfoLog(self):
        print(self.infoLog())


class UniformVar(object):
    def __init__(self, set_function, name, *args):
        self.setFunction = set_function
        self.name = name
        self.values = args

    def set(self):
        self.setFunction(self.name, *self.values)


class Program(object):
    """An OpenGL shader program"""

    def __init__(self):
        self.programObject = gl.glCreateProgramObjectARB()
        self.shaders = []
        self.uniformVars = {}

    def __del__(self):
        try:
            gl.glDeleteObjectARB(self.programObject)
        except ImportError:
            # Python loudly "ignores" this error on shutdown - explicitly ignore here
            pass

    def attachShader(self, shader):
        self.shaders.append(shader)
        shader.program = self
        gl.glAttachObjectARB(self.programObject, shader.shaderObject)

    def detachShader(self, shader):
        self.shaders.remove(shader)
        gl.glDetachObjectARB(self.programObject, shader.shaderObject)
        print("Shader detached")

    def link(self):
        gl.glLinkProgramARB(self.programObject)

    def use(self):
        global activeShader
        activeShader = self
        gl.glUseProgramObjectARB(self.programObject)
        self.setVars()

    def stop(self):
        global activeShader
        gl.glUseProgramObjectARB(0)
        activeShader = None

    def uniformi(self, name, *args):
        argf = {1: gl.glUniform1iARB,
                2: gl.glUniform2iARB,
                3: gl.glUniform3iARB,
                4: gl.glUniform4iARB}
        f = argf[len(args)]

        def _set_uniform(name, *args):
            location = gl.glGetUniformLocationARB(self.programObject, name)
            f(location, *args)

        self.uniformVars[name] = UniformVar(_set_uniform, name, *args)
        if self == activeShader:
            self.uniformVars[name].set()

    def uniformf(self, name, *args):
        argf = {1: gl.glUniform1fARB,
                2: gl.glUniform2fARB,
                3: gl.glUniform3fARB,
                4: gl.glUniform4fARB}
        f = argf[len(args)]

        def _set_uniform(name, *args):
            location = gl.glGetUniformLocationARB(self.programObject, name)
            f(location, *args)

        self.uniformVars[name] = UniformVar(_set_uniform, name, *args)
        if self == activeShader:
            self.uniformVars[name].set()

    def uniformMatrixf(self, name, transpose, values):
        argf = {4: gl.glUniformMatrix2fvARB,
                9: gl.glUniformMatrix3fvARB,
                16: gl.glUniformMatrix4fvARB}
        f = argf[len(values)]

        def _set_uniform(name, values):
            location = gl.glGetUniformLocationARB(self.programObject, name)
            matrix_type = ctypes.c_float * len(values)
            matrix = matrix_type(*values)
            f(location, 1, transpose, ctypes.cast(matrix, ctypes.POINTER(ctypes.c_float)))

        self.uniformVars[name] = UniformVar(_set_uniform, name, values)
        if self == activeShader:
            self.uniformVars[name].set()

    def setVars(self):
        for name, var in self.uniformVars.items():
            var.set()

    def printInfoLog(self):
        print(gl.glGetInfoLogARB(self.programObject))


def MakePixelShaderFromSource(src):
    return MakeShaderFromSource(src, gl.GL_FRAGMENT_SHADER_ARB)


def MakeVertexShaderFromSource(src):
    return MakeShaderFromSource(src, gl.GL_VERTEX_SHADER_ARB)


def MakeShaderFromSource(src, shader_type):
    shader = Shader(shader_type)
    shader.source(src)
    shader.compileShader()
    return shader


def MakeProgramFromSourceFiles(vertex_shader_name, pixel_shader_name):
    file = open(vertex_shader_name, "r")
    vs_src = file.tostring()
    file.close()
    file = open(pixel_shader_name, "r")
    ps_src = file.tostring()
    file.close()
    return MakeProgramFromSource(vs_src, ps_src)


def MakeProgramFromSource(vertex_shader_src, pixel_shader_src):
    vs = MakeVertexShaderFromSource(vertex_shader_src)
    ps = MakePixelShaderFromSource(pixel_shader_src)

    p = Program()
    p.attachShader(vs)
    p.attachShader(ps)
    p.link()
    p.use()
    return p


def DisableShaders():
    global activeShader
    gl.glUseProgramObjectARB(0)
    activeShader = None
