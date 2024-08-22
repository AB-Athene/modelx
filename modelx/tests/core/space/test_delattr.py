import pytest
import modelx as mx
from modelx import defcells, new_space
from modelx.core.errors import DeletedObjectError
from modelx.testing.testutil import ConfigureExecutor

@pytest.fixture
def testmodel():
    m = mx.new_model()
    yield m
    m._impl._check_sanity()
    m.close()


def test_delattr_cells(testmodel):
    """
        A---foo(x)
    """
    space = new_space("A")

    @defcells
    def foo(x):
        return 2 * x

    foo(3)
    del space.foo

    assert not foo._is_valid()

    with ConfigureExecutor():
        with pytest.raises(AttributeError):
            space.foo(3)
        with pytest.raises(DeletedObjectError):
            foo(3)


def test_delattr_space(testmodel):
    """
        A---Child
    """
    space = new_space("A")
    child = space.new_space("Child")
    del space.Child
    assert space.named_spaces == {}
    assert not child._is_valid()


def test_delattr_ref(testmodel):

    s = testmodel.new_space("A")
    s.x = 3
    assert s.x == 3
    del s.x

    with ConfigureExecutor():
        with pytest.raises(AttributeError):
            s.x


def test_delattr_ref_interface(testmodel):

    s = testmodel.new_space("A")
    t = testmodel.new_space("B")
    t.x = s
    assert t.x is s
    del t.x

    with ConfigureExecutor():
        with pytest.raises(AttributeError):
            t.x


def test_delattr_null_space(testmodel):
    """
        A---B---C---foo
          |
          +-b <-- B
    """
    A = testmodel.new_space('A')
    B = A.new_space('B')
    C = B.new_space('C')

    @mx.defcells
    def foo(x):
        return x

    A.b = B
    del A.B

    assert not A.b._is_valid()
    assert not foo._is_valid()
    assert not C._is_valid()
