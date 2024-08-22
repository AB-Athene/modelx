import modelx as mx
from modelx.testing.testutil import ConfigureExecutor
import pytest


@pytest.fixture
def refmodel():
    """
    m------SpaceA----bar
        +--baz    +--foo
    """
    m = mx.new_model()
    m.baz = 1
    s = m.new_space("SpaceA")

    def foo():
        return bar * baz

    s.new_cells(formula=foo)
    s.bar = 3
    assert s.foo() == 3
    yield m
    m._impl._check_sanity()
    m.close()


@pytest.fixture(params=[True, False])
def refspace(request, refmodel, tmpdir_factory):

    model = refmodel
    if request.param:
        file = str(tmpdir_factory.mktemp("data").join("refmodel.mx"))
        model.write(file)
        model.close()
        model = mx.read_model(file)

    yield model.SpaceA


def test_update_ref(refspace):

    refspace.bar = 5
    assert refspace.foo() == 5


def test_delete_ref(refspace):

    del refspace.bar

    with ConfigureExecutor():
        with pytest.raises(NameError):
            refspace.foo()


def test_override_global(refspace):

    assert refspace.foo() == 3
    refspace.baz = 5
    assert refspace.foo() == 15


def test_delete_global(refspace):

    assert refspace.foo() == 3
    del refspace.model.baz
    with ConfigureExecutor():
        with pytest.raises(NameError):
            refspace.foo()

