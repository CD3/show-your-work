import copy

import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

from show_your_work import Expression


def test_simple_expression_without_units():
    expr = Expression(r"\v{m}\v{x} + \v{b}")

    assert expr.latex == "mx + b"
    assert expr.latex_with_substitutions == "mx + b"

    expr.add_substitution("m", 10)
    assert expr.latex_with_substitutions == "(10)x + b"

    expr.add_substitution("x", 2)
    assert expr.latex_with_substitutions == "(10)(2) + b"

    expr.add_substitution("b", 5)
    assert expr.latex_with_substitutions == "(10)(2) + (5)"

    assert expr.eval() == 25


def test_simple_expression_with_no_units_in_subs_but_units_in_result():
    """
    This works, but is not very good...
    """
    expr = Expression(r"\v{m}\v{x} + \v{b}", "m")

    assert expr.latex == "mx + b"
    assert expr.latex_with_units == r"mx + b \,\si[]{\meter}"
    assert expr.latex_with_substitutions == "mx + b"

    expr.add_substitution("m", 10)
    assert expr.latex_with_substitutions == "(10)x + b"

    expr.add_substitution("x", 2)
    assert expr.latex_with_substitutions == "(10)(2) + b"

    expr.add_substitution("b", 5)
    assert expr.latex_with_substitutions == "(10)(2) + (5)"

    val = expr.eval(Q_)
    assert val.magnitude == 25
    assert val.to("cm").magnitude == 2500


def test_simple_expression_with_units_in_subs_and_result():
    """
    This is better. Unfortunately we don't have any way to check dimensions.
    """
    expr = Expression(r"\v{m}\v{x} + \v{b}", "m")
    assert expr.latex_with_substitutions == "mx + b"

    expr.add_substitution("m", Q_(10, "m/s"))
    assert expr.latex_with_substitutions == r"(\SI[]{10}{\meter\per\second})x + b"

    expr.add_substitution("x", Q_(2, "s"))
    assert (
        expr.latex_with_substitutions
        == r"(\SI[]{10}{\meter\per\second})(\SI[]{2}{\second}) + b"
    )

    expr.add_substitution("b", Q_(5, "m"))
    assert (
        expr.latex_with_substitutions
        == r"(\SI[]{10}{\meter\per\second})(\SI[]{2}{\second}) + (\SI[]{5}{\meter})"
    )

    val = expr.eval(Q_)
    assert val.magnitude == 25
    assert val.to("cm").magnitude == 2500


def test_simple_expression_with_in_units_and_unit_conversion():

    expr = Expression(r"\v{m}\v{x} + \v{b}", "cm")
    expr.add_substitution("m", Q_(10, "m/s"))
    expr.add_substitution("x", Q_(2000, "ms"))
    expr.add_substitution("b", Q_(5000, "mm"))

    val = expr.eval(Q_)
    assert val.magnitude == 2500
