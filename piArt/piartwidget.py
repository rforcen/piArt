'''
promoted class in .ui

'''

from rendererGL import RendererGL

class PiArtWidget(RendererGL):
    cBez = None

    def __init__(self, parent=None):
        super(PiArtWidget, self).__init__(parent)

    def setShapes(self, cBez):  # namedtuples (Colors, Coords)
        self.cBez = cBez
        self.repaint()

    def draw(self, gl):
        if self.cBez is not None:
            for cs in self.cBez:
                gl.glBegin(self.gl.GL_LINE_STRIP)
                gl.glColor3ubv(cs.Colors)
                for c in cs.Coords:
                    gl.glVertex3fv(list(c * 0.45))
                gl.glEnd()
