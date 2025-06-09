import pint
import pytest

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

from show_your_work import (Equation, UnphysicalEquation,
                            eval_and_show_work_latex)


def test_simple_equation_without_units():
    eq = Equation(r"\v{x(t)} = \v{v}\v{t} + \v{x_0}")

    assert eq.latex == "x(t) = vt + x_0"
    eq.rhs.add_substitution("t", 10)
    assert eq.latex == "x(t) = vt + x_0"
    assert eq.latex_with_substitutions == r"x(t) = v(10) + x_0"

    eq.rhs.add_substitution("v", 2)
    eq.rhs.add_substitution("x_0", 3)
    assert eq.latex_with_substitutions == r"x(t) = (2)(10) + (3)"

    assert eq.rhs.eval() == 23


def test_simple_equation_with_units():
    eq = Equation(r"\v{x(t)} = \v{v}\v{t} + \v{x_0}", "m")

    assert eq.latex == "x(t) = vt + x_0"
    assert eq.latex_with_units == "x(t) = vt + x_0 \,\si[]{\meter}"
    eq.rhs.add_substitution("t", Q_(10, "ms"))
    assert eq.latex == "x(t) = vt + x_0"
    assert eq.latex_with_substitutions == r"x(t) = v(\SI[]{10}{\milli\second}) + x_0"

    eq.rhs.add_substitution("v", Q_(2, "m/s"))
    eq.rhs.add_substitution("x_0", Q_(3, "cm"))
    assert (
        eq.latex_with_substitutions
        == r"x(t) = (\SI[]{2}{\meter\per\second})(\SI[]{10}{\milli\second}) + (\SI[]{3}{\centi\meter})"
    )

    assert eq.rhs.eval(Q_).units == Q_(1, "m").units
    assert eq.rhs.eval(Q_).magnitude == pytest.approx(3e-2 + 2 * 10e-3)

    assert eq.rhs.eval(Q_, no_unit_conversions=True).units == Q_(1, "m").units
    assert eq.rhs.eval(Q_, no_unit_conversions=True).magnitude == pytest.approx(23)


def test_simple_unphysical_equation_with_units():
    """
    An unphysical equation is an equation that is not dimensionally correct. Rather than
    including proptionality constants that would just be the value 1 with a unit, they
    assume that the quantities are expressed in a specific unit and the answer will then
    be in a specific unit.

    We can't try to do unit conversions with these equations, we have to just take the magnitude
    of all quantities, compute a numerical value, and return it as the value of a quantity with units
    equal to the equations units.
    """

    eq = UnphysicalEquation(r"\v{x(t)} = \v{a}\v{t}^2 + \v{b}", "m")

    assert eq.latex == "x(t) = at^2 + b"
    assert eq.latex_with_units == "x(t) = at^2 + b \,\si[]{\meter}"
    eq.rhs.add_substitution("t", Q_(2, "s"))
    assert eq.latex == "x(t) = at^2 + b"
    assert eq.latex_with_substitutions == r"x(t) = a(\SI[]{2}{\second})^2 + b"

    eq.rhs.add_substitution("a", 2)
    eq.rhs.add_substitution("b", 3)
    assert eq.latex_with_substitutions == r"x(t) = (2)(\SI[]{2}{\second})^2 + (3)"

    assert eq.rhs.eval(Q_).units == Q_(1, "m").units
    assert eq.rhs.eval(Q_).magnitude == pytest.approx(2 * 2 * 2 + 3)


def test_eval_equation_with_work():
    eq = Equation(r"\v{x(t)} = \v{v}\v{t} + \v{x_0}", "m")

    eq.rhs.add_substitution("v", Q_(2, "m/s"))
    eq.rhs.add_substitution("t", Q_(3, "s"))
    eq.rhs.add_substitution("x_0", Q_(4, "m"))

    assert (
        eval_and_show_work_latex(eq, Q_)
        == r"x(t) = vt + x_0 = (\SI[]{2}{\meter\per\second})(\SI[]{3}{\second}) + (\SI[]{4}{\meter}) = \SI[]{10.0}{\meter}"
    )


def test_add_substitution_equation():
    eq = Equation(r"\v{x(t)} = \v{v}\v{t} + \v{x_0}", "m")

    eq.add_substitution("v", Q_(2, "m/s"))
    eq.add_substitution("t", Q_(3, "s"))
    eq.add_substitution("x_0", Q_(4, "m"))

    assert eq.latex == r"x(t) = vt + x_0"
    assert (
        eq.latex_with_substitutions
        == "x(t) = (\SI[]{2}{\meter\per\second})(\SI[]{3}{\second}) + (\SI[]{4}{\meter})"
    )
    eq.add_substitution("x(t)", Q_(5, "m"))
    assert (
        eq.latex_with_substitutions
        == "(\SI[]{5}{\meter}) = (\SI[]{2}{\meter\per\second})(\SI[]{3}{\second}) + (\SI[]{4}{\meter})"
    )
