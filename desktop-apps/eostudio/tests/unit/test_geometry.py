"""Unit tests for geometry primitives, vectors, matrices, and mesh operations."""

from __future__ import annotations

import math
import unittest

from eostudio.core.geometry.primitives import (
    Vec2, Vec3, Vec4, Matrix4, BoundingBox, Mesh,
    create_cube, create_sphere, create_cylinder, create_cone, create_torus, create_plane,
)
from eostudio.core.geometry.transforms import Quaternion, Transform
from eostudio.core.geometry.curves import BezierCurve, BSplineCurve


class TestVec2(unittest.TestCase):
    def test_add(self) -> None:
        a = Vec2(1.0, 2.0)
        b = Vec2(3.0, 4.0)
        c = a + b
        self.assertAlmostEqual(c.x, 4.0)
        self.assertAlmostEqual(c.y, 6.0)

    def test_sub(self) -> None:
        a = Vec2(5.0, 3.0)
        b = Vec2(2.0, 1.0)
        c = a - b
        self.assertAlmostEqual(c.x, 3.0)
        self.assertAlmostEqual(c.y, 2.0)

    def test_length(self) -> None:
        v = Vec2(3.0, 4.0)
        self.assertAlmostEqual(v.length(), 5.0)

    def test_normalize(self) -> None:
        v = Vec2(0.0, 5.0)
        n = v.normalized()
        self.assertAlmostEqual(n.length(), 1.0)
        self.assertAlmostEqual(n.x, 0.0)
        self.assertAlmostEqual(n.y, 1.0)

    def test_dot(self) -> None:
        a = Vec2(1.0, 0.0)
        b = Vec2(0.0, 1.0)
        self.assertAlmostEqual(a.dot(b), 0.0)


class TestVec3(unittest.TestCase):
    def test_add(self) -> None:
        a = Vec3(1.0, 2.0, 3.0)
        b = Vec3(4.0, 5.0, 6.0)
        c = a + b
        self.assertAlmostEqual(c.x, 5.0)
        self.assertAlmostEqual(c.y, 7.0)
        self.assertAlmostEqual(c.z, 9.0)

    def test_cross(self) -> None:
        x = Vec3(1.0, 0.0, 0.0)
        y = Vec3(0.0, 1.0, 0.0)
        z = x.cross(y)
        self.assertAlmostEqual(z.x, 0.0)
        self.assertAlmostEqual(z.y, 0.0)
        self.assertAlmostEqual(z.z, 1.0)

    def test_length(self) -> None:
        v = Vec3(1.0, 2.0, 2.0)
        self.assertAlmostEqual(v.length(), 3.0)

    def test_scale(self) -> None:
        v = Vec3(1.0, 2.0, 3.0)
        s = v * 2.0
        self.assertAlmostEqual(s.x, 2.0)
        self.assertAlmostEqual(s.y, 4.0)
        self.assertAlmostEqual(s.z, 6.0)

    def test_dot(self) -> None:
        a = Vec3(1.0, 2.0, 3.0)
        b = Vec3(4.0, 5.0, 6.0)
        self.assertAlmostEqual(a.dot(b), 32.0)


class TestVec4(unittest.TestCase):
    def test_creation(self) -> None:
        v = Vec4(1.0, 2.0, 3.0, 1.0)
        self.assertAlmostEqual(v.x, 1.0)
        self.assertAlmostEqual(v.w, 1.0)


class TestMatrix4(unittest.TestCase):
    def test_identity(self) -> None:
        m = Matrix4.identity()
        for i in range(4):
            for j in range(4):
                expected = 1.0 if i == j else 0.0
                self.assertAlmostEqual(m.data[i][j], expected)

    def test_multiply_identity(self) -> None:
        m = Matrix4.identity()
        a = Matrix4.translation(1.0, 2.0, 3.0)
        result = m * a
        for i in range(4):
            for j in range(4):
                self.assertAlmostEqual(result.data[i][j], a.data[i][j])

    def test_translation(self) -> None:
        m = Matrix4.translation(5.0, 10.0, 15.0)
        self.assertAlmostEqual(m.data[0][3], 5.0)
        self.assertAlmostEqual(m.data[1][3], 10.0)
        self.assertAlmostEqual(m.data[2][3], 15.0)

    def test_scaling(self) -> None:
        m = Matrix4.scaling(2.0, 3.0, 4.0)
        self.assertAlmostEqual(m.data[0][0], 2.0)
        self.assertAlmostEqual(m.data[1][1], 3.0)
        self.assertAlmostEqual(m.data[2][2], 4.0)


class TestBoundingBox(unittest.TestCase):
    def test_contains_point(self) -> None:
        bb = BoundingBox(Vec3(0, 0, 0), Vec3(10, 10, 10))
        self.assertTrue(bb.contains(Vec3(5, 5, 5)))
        self.assertFalse(bb.contains(Vec3(15, 5, 5)))

    def test_size(self) -> None:
        bb = BoundingBox(Vec3(-1, -2, -3), Vec3(1, 2, 3))
        size = bb.size()
        self.assertAlmostEqual(size.x, 2.0)
        self.assertAlmostEqual(size.y, 4.0)
        self.assertAlmostEqual(size.z, 6.0)

    def test_center(self) -> None:
        bb = BoundingBox(Vec3(0, 0, 0), Vec3(10, 10, 10))
        center = bb.center()
        self.assertAlmostEqual(center.x, 5.0)
        self.assertAlmostEqual(center.y, 5.0)
        self.assertAlmostEqual(center.z, 5.0)


class TestMeshCreation(unittest.TestCase):
    def test_create_cube(self) -> None:
        mesh = create_cube(2.0)
        self.assertIsInstance(mesh, Mesh)
        self.assertGreater(len(mesh.vertices), 0)
        self.assertGreater(len(mesh.faces), 0)

    def test_create_sphere(self) -> None:
        mesh = create_sphere(1.0, segments=8, rings=6)
        self.assertIsInstance(mesh, Mesh)
        self.assertGreater(len(mesh.vertices), 0)

    def test_create_cylinder(self) -> None:
        mesh = create_cylinder(1.0, 2.0, segments=12)
        self.assertIsInstance(mesh, Mesh)
        self.assertGreater(len(mesh.vertices), 0)

    def test_create_cone(self) -> None:
        mesh = create_cone(1.0, 3.0, segments=12)
        self.assertIsInstance(mesh, Mesh)
        self.assertGreater(len(mesh.vertices), 0)

    def test_create_torus(self) -> None:
        mesh = create_torus(2.0, 0.5)
        self.assertIsInstance(mesh, Mesh)
        self.assertGreater(len(mesh.vertices), 0)

    def test_create_plane(self) -> None:
        mesh = create_plane(5.0, 5.0)
        self.assertIsInstance(mesh, Mesh)
        self.assertGreater(len(mesh.vertices), 0)


class TestQuaternion(unittest.TestCase):
    def test_identity(self) -> None:
        q = Quaternion(0, 0, 0, 1)
        self.assertAlmostEqual(q.w, 1.0)
        self.assertAlmostEqual(q.length(), 1.0)

    def test_from_axis_angle(self) -> None:
        q = Quaternion.from_axis_angle(Vec3(0, 1, 0), math.pi / 2)
        self.assertAlmostEqual(q.length(), 1.0)

    def test_multiply(self) -> None:
        q1 = Quaternion.from_axis_angle(Vec3(0, 1, 0), math.pi / 4)
        q2 = Quaternion.from_axis_angle(Vec3(0, 1, 0), math.pi / 4)
        q3 = q1 * q2
        expected = Quaternion.from_axis_angle(Vec3(0, 1, 0), math.pi / 2)
        self.assertAlmostEqual(q3.w, expected.w, places=5)


class TestTransform(unittest.TestCase):
    def test_identity(self) -> None:
        t = Transform()
        self.assertAlmostEqual(t.position.x, 0.0)
        self.assertAlmostEqual(t.scale.x, 1.0)

    def test_apply_to_point(self) -> None:
        t = Transform(position=Vec3(10, 0, 0))
        p = t.apply_to_point(Vec3(1, 0, 0))
        self.assertAlmostEqual(p.x, 11.0)


if __name__ == "__main__":
    unittest.main()
