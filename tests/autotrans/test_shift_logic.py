from autotrans.transmission import Gear, Gearbox
from pytest import raises
from transitions import MachineError


def test_initial_gear():
    gearbox = Gearbox()
    assert gearbox.state is Gear.FIRST

    gearbox = Gearbox(Gear.SECOND)
    assert gearbox.state is Gear.SECOND

    with raises(ValueError):
        Gearbox("gear1")


def test_shift_up():
    gearbox = Gearbox()

    gearbox.shift_up()
    assert gearbox.state is Gear.SECOND

    gearbox.shift_up()
    assert gearbox.state is Gear.THIRD

    gearbox.shift_up()
    assert gearbox.state is Gear.FOURTH

    with raises(MachineError):
        gearbox.shift_up()


def test_shift_down():
    gearbox = Gearbox(Gear.FOURTH)

    gearbox.shift_down()
    assert gearbox.state is Gear.THIRD

    gearbox.shift_down()
    assert gearbox.state is Gear.SECOND

    gearbox.shift_down()
    assert gearbox.state is Gear.FIRST

    with raises(MachineError):
        gearbox.shift_down()
