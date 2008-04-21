from graph import Graph
from tryton.common import hex2rgb
import locale
import math


class Line(Graph):

    def updateGraph(self):

        self.points = []
        i = 0
        keys = self.datas.keys()
        keys.sort()
        for xfield in keys:
            j = 0
            for yfield in self.datas[xfield]:
                xval = i
                yval = self.datas[xfield][yfield]

                x = (xval - self.minxval) * self.xscale
                y = 1.0 - (yval - self.minyval) * self.yscale

                point = Point(x, y, xval, yval, xfield, yfield)
                if (0.0 <= point.x <= 1.0) and (0.0 <= point.y <= 1.0):
                    self.points.append(point)

                j += 1
            i += 1

    def drawGraph(self, cr, width, height):
        key2fill = {}
        for yfield in self.yfields:
            key2fill[yfield.get('key', yfield['name'])] = \
                    bool(eval(yfield.get('fill', '0')))

        def preparePath(key):
            cr.new_path()
            cr.move_to(self.area.x, self.area.y + self.area.h)
            for point in self.points:
                if point.yname == key:
                    cr.line_to(point.x * self.area.w + self.area.x,
                            point.y * self.area.h + self.area.y)
            cr.line_to(self.area.x + self.area.w, self.area.y + self.area.h)
            cr.move_to(self.area.x, self.area.y + self.area.h)

            if key2fill[key]:
                cr.close_path()
            else:
                cr.set_source_rgb(*self.colorScheme[key])
                cr.stroke()

        cr.save()
        cr.set_line_width(2)
        for key in self._getDatasKeys():
            if key2fill[key]:
                cr.save()
                cr.set_source_rgba(0, 0, 0, 0.15)
                cr.translate(2, -2)
                preparePath(key)
                cr.fill()
                cr.restore()

                cr.set_source_rgb(*self.colorScheme[key])
                preparePath(key)
                cr.fill()
            else:
                preparePath(key)
        for point in self.points:
            if point.highlight:
                cr.set_line_width(2)
                cr.set_source_rgb(*hex2rgb('#000000'))
                cr.arc(point.x * self.area.w + self.area.x,
                        point.y * self.area.h + self.area.y,
                        3, 0, 2 * math.pi)
                cr.stroke()
                cr.set_source_rgb(*self.colorScheme['__highlight'])
                cr.arc(point.x * self.area.w + self.area.x,
                        point.y * self.area.h + self.area.y,
                        3, 0, 2 * math.pi)
                cr.fill()
        cr.restore()

    def motion(self, widget, event):
        nearest = None
        for point in self.points:
            x = point.x * self.area.w + self.area.x
            y = point.y * self.area.h + self.area.y

            l = (event.x - x) ** 2 + (event.y - y) ** 2

            if not nearest or l < nearest[1]:
                nearest = (point, l)

        dia = self.area.w ** 2 + self.area.h ** 2

        for point in self.points:
            if point == nearest[0] and nearest[1] < dia / 100:
                if not point.highlight:
                    point.highlight = True
                    label = locale.format('%.2f', point.yval, True)
                    label += '\n'
                    label += str(self.labels[point.xname])
                    self.popup.set_text(label)
                    self.queue_draw()
            else:
                if point.highlight:
                    point.highlight = False
                    self.queue_draw()
        highlight = False
        for point in self.points:
            if point.highlight:
                self.popup.set_position(self,
                        point.x * self.area.w + self.area.x,
                        point.y * self.area.h + self.area.y)
                highlight = True
        if highlight:
            self.popup.show()
        else:
            self.popup.hide()

    def updateXY(self):
        super(Line, self).updateXY()
        if self.xrange != 0:
            self.xrange -= 1
            if self.xrange == 0:
                self.xscale = 1.0
            else:
                self.xscale = 1.0 / self.xrange

    def drawAxis(self, cr, width, height):
        super(Line, self).drawAxis(cr, width, height)
        self.drawLine(cr, 1.0, 0)


class Point(object):

    def __init__(self, x, y, xval, yval, xname, yname):
        self.x, self.y = x, y
        self.xval, self.yval = xval, yval
        self.xname = xname
        self.yname = yname
        self.highlight = False
