import sys
from collections import namedtuple
from math import (sin, pi, cos)
from struct import pack

import bezier
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow)
from PyQt5.uic import loadUi

# genShapes result is a set of colors(rgb) and bezier coords in a named tuple
CoordsColor = namedtuple('CoordsColors', ['Coords', 'Colors'])


class PIdigits:
    filePI = 'piFile.pickle'
    pairs, n, nd = None, None, None

    def __init__(self, n=1000, nd=2):
        self.n = n
        self.nd = nd

    def __piIter(self):
        q, r, t, k, m, x = 1, 0, 1, 1, 3, 3
        while True:
            if 4 * q + r - t < m * t:
                yield m
                q, r, t, k, m, x = 10 * q, 10 * (r - m * t), t, k, (10 * (3 * q + r)) // t - 10 * m, x
            else:
                q, r, t, k, m, x = q * k, (2 * q + r) * x, t * x, k + 1, (q * (7 * k + 2) + r * x) // (t * x), x + 2

    def digits(self, n):
        pit = self.__piIter()
        return ''.join([str(next(pit)) for i in range(n)])

    def pairsDD(self) -> list:
        'dd pi digits in a int list'
        if self.pairs is None:
            dd = self.str2dd(self.digits(self.n))
            self.pairs = list(map(lambda x: [x[0], x[1]], zip(dd[:-1:2], dd[1:-1:2])))
        return self.pairs

    def digitSets(self, nDigits) -> list:
        'nDigits pi digits in a int list'
        if self.pairs is None:
            dd = self.str2digits(self.digits(self.n), nDigits)
            self.pairs = list(map(lambda x: [x[0], x[1]], zip(dd[:-1:nDigits], dd[1:-1:nDigits])))
        return self.pairs

    def str2dd(self, s: str) -> list:
        return list(map(lambda x: int(x[0] + x[1]), zip(s[:-1:2], s[1:-1:2])))

    def str2digits(self, s: str, nd: int) -> list:
        return [int(s[i:i + nd]) for i in range(0, len(s), nd)]


def genShapes():
    'generate 3d bezier link between sphere coordinates indexed by 2 digits pi decimals'

    def polygon(n, scale=1.0, z=0.0):
        ' list w/ n sided 3d polygon'
        pi2n = 2 * pi / n
        return [[scale * sin(i * pi2n), scale * cos(i * pi2n), z]
                for i in range(0, n)]

    def sphere(slices):
        '3d sphere coords'
        return [polygon(slices, scale=sin(pi * s / (slices + 1)), z=2. * (s / (slices + 1) - 0.5))
                for s in range(1, (slices + 1))]

    def evalBezier(c, n=20):
        return c.evaluate_multi(np.linspace(0, 1, n))

    def interpolateColor(ratio, _from=0x0000ff, _to=0xff0000):
        'return a list of r,g,b from interpolation of color'
        return list(pack('=i', int(int((_to - _from) / ratio + _from))))

    nSlices = 10  # must be 10 for a 2d pi digits 10x10=100 -> 00..99
    pd = PIdigits(nSlices ** 3)
    sphCoords = sphere(nSlices)  # 10x10 = 100 coords 00..99

    sphcfzt = [
        [interpolateColor(ratio=(p[0] + p[1]) / 200.),  # 0.01 * (p0+p1)/2
         sphCoords[p[0] // nSlices][p[0] % nSlices],
         [0, 0, 0],  # insert the [0,0,0] coord to 'curve' bezier
         sphCoords[p[1] // nSlices][p[1] % nSlices]]
        for p in pd.pairsDD()]  # color, from-zero-to coords

    return [CoordsColor(Colors=c, Coords=evalBezier(bezier.Curve(np.asfortranarray([f, z, t]), degree=2)))
            for c, f, z, t in sphcfzt]  # color, from, zero, to
    # list w/ color, bezier.Curve


class PIart(QMainWindow):
    'load ui'

    def __init__(self, *args):
        super(PIart, self).__init__(*args)
        loadUi('piArt.ui', self)  # contains PiArtWidget openglwidget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = PIart()
    mainWin.show()
    mainWin.widgetGL.setShapes(genShapes())
    sys.exit(app.exec_())
