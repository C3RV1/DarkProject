

class HilbertCurve:
    def __init__(self, order):
        self.order = order

    def xy2d(self, x, y):
        s = int(self.order / 2)
        d = 0

        while s > 0:
            rx = int((x & s) > 0)
            ry = int((x & s) > 0)
            d += s * s * ((3 * rx) ^ ry)
            x, y = self.__rot(x, y, rx, ry)
            s = int(s / 2)
        return d

    def d2xy(self):
        pass

    def __rot(self, x, y, rx, ry):
        new_x = x
        new_y = y
        if ry == 0:
            if rx == 1:
                new_x = self.order - 1 - new_x
                new_y = self.order - 1 - new_y

            tmp = new_x
            new_x = new_y
            new_y = tmp
        return new_x, new_y
