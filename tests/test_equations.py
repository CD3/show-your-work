import copy

import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

from show_your_work import Equation


def test_simple_equation_without_units():
    eq = Equation(r"\v{x(t)} = \v{v}\v{t} + \v{x_0}")

    assert eq.latex == "x(t) = vt + x_0"
    eq.rhs.add_substitution("t", Q_(10, "ms"))
    assert eq.latex == "x(t) = vt + x_0"
    assert eq.latex_with_substitutions == r"x(t) = v(\SI[]{10}{\milli\second}) + x_0"
