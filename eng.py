import pygame
import math
import numpy as np

def toVec(p): return pygame.math.Vector3(*p)  # (Float, Float, Float) -> Vector3

class Tag:  # Abstract class; must be implemented by user!
    def ondraw(self): return None, None  # must return (fill color, outline color)

class SimpleTag(Tag):  # Simple tag implementation
    def __init__(self, c): self.c = c
    def ondraw(self): return self.c, None

class Polygon:
    def __init__(self, tag, a, b, c):
        if not isinstance(tag, Tag): raise Exception("Error: Polygon tag must be a Tag object")
        self.tag = tag
        self.a = a
        self.b = b
        self.c = c

    def isThickEnough(self):
        return (round((self.a[0] - self.b[0]).length(), 5) > 0
            and round((self.b[0] - self.c[0]).length(), 5) > 0
            and round((self.c[0] - self.a[0]).length(), 5) > 0)

    # (in-place)
    def orient(self, center, reverse=False):  # flip polygon so that it's invisible from a view point (usually the center of a solid shape)
        s = BSP.mkD(self).distf(toVec(center))
        if s == 0:
            raise Exception("[orient] A polygon passes through the center and its orientation cannot be determined")
        if reverse != (s < 0): return  # already oriented correctly
        # if not -> flip
        self.a, self.b = self.b, self.a

    def render(self):  # return whether polygon was drawn
        coords = (
            BSP.pointProject(self.a[0]),
            BSP.pointProject(self.b[0]),
            BSP.pointProject(self.c[0]))
        fill, outline = self.tag.ondraw()
        if fill:
            pygame.draw.polygon(BSP.window, fill, coords)
        if outline:
            if self.a[1]: pygame.draw.line(BSP.window, outline, coords[1], coords[2], 3)
            if self.b[1]: pygame.draw.line(BSP.window, outline, coords[2], coords[0], 3)
            if self.c[1]: pygame.draw.line(BSP.window, outline, coords[0], coords[1], 3)

    def crossesZ(self):  # returns whether polygon crosses the Z axis or not
        s1 = self.a[0].x*self.b[0].y - self.a[0].y*self.b[0].x
        s2 = self.b[0].x*self.c[0].y - self.b[0].y*self.c[0].x
        s3 = self.c[0].x*self.a[0].y - self.c[0].y*self.a[0].x
        if round(s1, 5) == 0 or round(s2, 5) == 0 or round(s3, 5) == 0: return True
        if max(s1, s2, s3, 0) == 0 or min(s1, s2, s3, 0) == 0: return True
        return False

class Matrix:
    zero = pygame.math.Vector3(0, 0, 0)
    unitX = pygame.math.Vector3(1, 0, 0)
    unitY = pygame.math.Vector3(0, 1, 0)
    unitZ = pygame.math.Vector3(0, 0, 1)

    @staticmethod
    def applyTo(matrix, v):
        return pygame.math.Vector3(
            round(matrix[0][0]*v.x + matrix[0][1]*v.y + matrix[0][2]*v.z + matrix[0][3], 5),
            round(matrix[1][0]*v.x + matrix[1][1]*v.y + matrix[1][2]*v.z + matrix[1][3], 5),
            round(matrix[2][0]*v.x + matrix[2][1]*v.y + matrix[2][2]*v.z + matrix[2][3], 5))

    @staticmethod
    def traslationT(p=zero):
        return np.array([
            [1, 0, 0, p[0]],
            [0, 1, 0, p[1]],
            [0, 0, 1, p[2]],
            [0, 0, 0,   1]])
    @staticmethod
    def scaleT(f=1):
        return np.array([
            [f, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, f, 0],
            [0, 0, 0, 1]])
    @staticmethod
    def rotationT(rad, pivot):  # rotate rad around a pivot vector
        normal = pivot.normalize()
        skew = np.array([
            [0,          normal.z, -normal.y],
            [-normal.z,         0,  normal.x],
            [ normal.y, -normal.x,         0]])
        square = math.sin(rad)*skew + (1 - math.cos(rad))*(skew @ skew)  # rodrigues' rotation skew symmetric matrix formula
        augmented = np.array([
            [1+square[0][0],   square[0][1],   square[0][2], 0],
            [  square[1][0], 1+square[1][1],   square[1][2], 0],
            [  square[2][0],   square[2][1], 1+square[2][2], 0],
            [             0,              0,              0, 1]])
        return augmented

class Plane:
    def __init__(self, distf, dotpf):
        self.distf = distf
        self.dotpf = dotpf

class BSP:
    camera = pygame.math.Vector3(0, 0, -1)
    # camera point; change Z to adjust FOV (must always be negative; the closer to 0 the wider and more distorted)
    windowPlane = Plane(lambda x: x[2], lambda x: x[2])

    @staticmethod
    def pointProject(p):
        factor = BSP.camera.z / (BSP.camera.z - p.z)
        point = p*factor + BSP.camera*(1 - factor)
        m = min(BSP.dims[0], BSP.dims[1])
        return (point.x*m + BSP.dims[0]/2, point.y*m + BSP.dims[1]/2)

    @staticmethod
    def mkD(tp):
        np = -1 * tp.a[0]
        normal = (tp.b[0] + np).cross(tp.c[0] + np)  # normal vector
        dotpf = lambda v: normal.dot(v)  # dotpf(v) returns the dot product of the normal vector and v
        distf = lambda x: dotpf(x + np)  # distf(p) returns the distance from p to the plane
        return Plane(distf, dotpf)

    @staticmethod
    def polySlice(plane, tp):  # (Plane, Polygon) -> Polygon
        cA = round(plane.distf(tp.a[0]), 5)
        cB = round(plane.distf(tp.b[0]), 5)
        cC = round(plane.distf(tp.c[0]), 5)
        if max(cA, cB, cC, 0) == 0:  # all distances are negative -> polygon is fully behind
            return (), (tp,)
        elif min(cA, cB, cC, 0) == 0:  # all distances are positive or zero -> polygon is fully in front
            return (tp,), ()
        else:  # mixed -> polygon needs to be split
            # Note: this algorithm assumes neither (cA, cB, cC) are zero. For that cases a faster approach exists,
                # but this is almost never the case since one of the points must lie exactly on the plane.
            blackSheep = ((cA > 0) == (cB > 0)) == (cC > 0)  # sign of isolated tip

            # Note: I have no idea what this was supposed to do, but it works as is right now
            if (cA > 0) == blackSheep:
                pa, pb, pc = tp.a, tp.b, tp.c  # no cycle
            elif (cB > 0) == blackSheep:
                pa, pb, pc = tp.b, tp.c, tp.a  # clockwise cycle
            else:
                pa, pb, pc = tp.c, tp.a, tp.b  # counter-clockwise cycle

            va, oa = pa
            vb, ob = pb
            vc, oc = pc

            fac = plane.distf(va)
            rQb = vb - va
            rQc = vc - va
            Kb = va - rQb*(fac/plane.dotpf(rQb))  # intersection point of line (R, Q1) and plane
            Kc = va - rQc*(fac/plane.dotpf(rQc))  # intersection point of line (R, Q2) and plane

            tip = (
                Polygon(tp.tag, (va, False), (Kb, ob), (Kc, oc)),)
            par = (
                Polygon(tp.tag, (vb, False), (Kc, oc), (Kb, False)),
                Polygon(tp.tag, (vc, False), (Kc, oa), (vb, ob)))

            return (tip, par) if blackSheep else (par, tip)

    @staticmethod
    def makeBSP(taggedPolygons):
        if len(taggedPolygons) == 0: return None  # no polygons -> no tree

        pivot = taggedPolygons[0]
        plane = BSP.mkD(pivot)
        if plane.distf(BSP.camera) == 0:
            print(f"! A polygon is invisible from the camera. This might cause floating point shenanigans.")

        fb = [BSP.polySlice(plane, tp) for tp in taggedPolygons[1:]]
        fronts = [i for f, b in fb for i in f if i.isThickEnough()]
        backs = [i for f, b in fb for i in b if i.isThickEnough()]

        return (BSP.makeBSP(backs), pivot, BSP.makeBSP(fronts))

    @staticmethod
    def consultBSP(bsp, matrix, results):
        if not bsp: return
        back, tp, front = bsp

        transTP = Polygon(tp.tag,  # calculate P'
            (Matrix.applyTo(matrix, tp.a[0]), tp.a[1]),
            (Matrix.applyTo(matrix, tp.b[0]), tp.b[1]),
            (Matrix.applyTo(matrix, tp.c[0]), tp.c[1]))

        if BSP.mkD(transTP).distf(BSP.camera) > 0:  # camera is in front of polygon -> render back ones, then polygon, then front ones
            BSP.consultBSP(back, matrix, results)
            f, _ = BSP.polySlice(BSP.windowPlane, transTP)
            for p in f:
                p.render()
                results.count += 1
                if p.crossesZ(): results.cursor = p.tag
            BSP.consultBSP(front, matrix, results)
        else:  # camera is behind polygon -> render front ones, then back ones (skip polygon itself; back-face culling)
            BSP.consultBSP(front, matrix, results)
            BSP.consultBSP(back, matrix, results)


    def __init__(self):
        self.count = 0
        self.cursor = None
        self.tree = None

    def build(self, polygons):
        self.tree = BSP.makeBSP(polygons)
    
    def render(self, matrix):
        self.count = 0
        self.cursor = None
        BSP.consultBSP(self.tree, matrix, self)

class Bases:
    @staticmethod
    def trigle(t, c1, c2, c3):
        return [
            Polygon(t, (toVec(c1), True), (toVec(c2), True), (toVec(c3), True))]

    @staticmethod
    def paralog(t, mid, c1, c2):  # create parallelogram given three of its corners
        mid = toVec(mid)
        c1 = toVec(c1)
        c2 = toVec(c2)
        if (c1 - mid).cross(c2 - mid).length() == 0: raise Exception("[paralog] The points are collinear and do not form a parallelogram")
        opp = c1 + c2 - mid  # calculate corner opposite to mid
        return [
            Polygon(t, (mid, False), (c1, True), (c2, True)),
            Polygon(t, (opp, False), (c1, True), (c2, True))]

