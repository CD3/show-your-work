import copy

from show_your_work import Parsers


def test_parsers():

    res = Parsers.make_expression_variable_parser().parse_string(r"\v{m}")
    assert res["argument"] == "{m}"

    var_name_mapping = {"m": "a"}

    def f(toks):
        on = toks[1][1:-1]
        rn = var_name_mapping[on]
        return rn

    parser = Parsers.make_expression_variable_parser()
    parser.set_parse_action(f)
    text = parser.transform_string(r"\v{m}")

    assert text == "a"

    var_name_mapping = {"m": "a", "x": "b", "b": "c"}

    parser.set_parse_action(f)
    text = parser.transform_string(r"\v{m}\v{x} + \v{b}")
    parser.set_parse_action(None)

    assert text == "ab + c"


def test_parsers_get_vars():
    variables = Parsers.get_variables(r"\v{m}\v{x} + \v{b}")
    assert len(variables) == 3
    assert variables[0] == "m"
    assert variables[1] == "x"
    assert variables[2] == "b"


def test_parsers_transform_to_sympy_compatible():
    text = Parsers.make_sympy_compatible(r"\v{m}\v{x} + \v{b}")
    assert text == "ab + c"

    text = Parsers.make_sympy_compatible(r"\pi \v{r}^2")
    assert text == r"\pi a^2"

    text = Parsers.make_sympy_compatible(r"1.8 \times \v{t}^{0.75} \times 10^{-3}")
    assert text == r"1.8 \times a^{0.75} \times 10^{-3}"


def test_parsers_transform_to_plain_latex():
    text = Parsers.make_plain_latex(r"\v{m}\v{x} + \v{b}")
    assert text == "mx + b"


def test_complex_var_names():
    text = r"\frac{1}{\v{\phi}} \sqrt{ \frac{ 4 \v{\Phi} } {\pi \v{\text{MPE:E}}} - \v{D_0}}"

    sympy_text = Parsers.make_sympy_compatible(text)
    plain_text = Parsers.make_plain_latex(text)

    assert sympy_text == r"\frac{1}{a} \sqrt{ \frac{ 4 b } {\pi c} - d}"
    assert (
        plain_text == r"\frac{1}{\phi} \sqrt{ \frac{ 4 \Phi } {\pi \text{MPE:E}} - D_0}"
    )
