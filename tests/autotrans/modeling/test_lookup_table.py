from autotrans.modeling.lookup_table import LookupTable2D
from autotrans.engine import THROTTLE_BREAKPOINTS, RPM_BREAKPOINTS, ENGINE_TORQUE_TABLE_VALUES
from pytest import approx


def test_lookup_table_2d():
    table = LookupTable2D(THROTTLE_BREAKPOINTS, RPM_BREAKPOINTS, ENGINE_TORQUE_TABLE_VALUES)

    assert table.lookup(60.0000, 1000.0000) == approx(278.5000, abs=0.01)
    assert table.lookup(59.9463, 1383.2808) == approx(291.3155, abs=0.01)
    assert table.lookup(59.8926, 1685.3620) == approx(293.7103, abs=0.01)
    assert table.lookup(59.8389, 1907.2317) == approx(295.7509, abs=0.01)
