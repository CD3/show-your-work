
import copy
import pytest

import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

from show_your_work import Expression


def test_expression_with_units_that_is_not_dimensionally_correct():
    # an example from the Z136.1 laser safety standard
    expr = Expression(r"1.8\v{t}^{0.75} \times 10^{-3}", "J/cm**2")
    expr.add_substitution("t", Q_(0.25,'s'))

    val = expr.eval(Q_)
    assert val.magnitude == pytest.approx(6.36396193e-8) # WRONG

    val = expr.eval(Q_,no_unit_conversions=True)
    assert val.magnitude == pytest.approx(6.36396193e-4) # CORRECT
