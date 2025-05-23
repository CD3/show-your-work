import copy
import pathlib
import sys

# PRIVATE: DO NOT USE OUSIDE
import pint as __pint
import pyparsing as pp
import sympy
import sympy.parsing.latex

__ureg = __pint.UnitRegistry()
x__Q_ = __ureg.Quantity


class Parsers:
    latex_command_argument = pp.nested_expr("{", "}")
    latex_command_name = pp.Word("a-zA-Z")
    latex_command = r"\\" + latex_command_name + latex_command_argument

    def make_expression_variable_parser(variable_tag="v"):
        parser = rf"\{variable_tag}" + pp.original_text_for(
            Parsers.latex_command_argument
        )("argument")
        return parser

    def get_variables(text, variable_tag="v"):
        variables = []
        parser = Parsers.make_expression_variable_parser(variable_tag)
        for ev in parser.scan_string(text):
            variables.append(ev[0]["argument"][1:-1])
        return variables

    def get_sympy_compatible_variable_name_mapping(text, variable_tag="v"):
        mapping = dict(
            zip(
                Parsers.get_variables(text, variable_tag),
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            )
        )
        return mapping

    def make_sympy_compatible(text, variable_tag="v"):
        """
        Replace variables with names that sympy can handle (single letters)
        """
        mapping = Parsers.get_sympy_compatible_variable_name_mapping(text)
        parser = Parsers.make_expression_variable_parser(variable_tag)

        def f(toks):
            on = toks[1][1:-1]
            rn = mapping[on]
            return rn

        parser.set_parse_action(f)
        ttext = parser.transform_string(text)

        return ttext

    def make_plain_latex(text, variable_tag="v"):
        r"""
        Remove \v{} commands from variables
        """

        def f(toks):
            return toks[1][1:-1]

        parser = Parsers.make_expression_variable_parser(variable_tag)
        parser.set_parse_action(f)
        ttext = parser.transform_string(text)

        return ttext


class Expression:
    r"""
    A class representing one side of an equagtion (typically the right-hand side).

    An expression is defined in LaTeX. It can be _evaluated_, a numerical value is calculated by
    inserting numerical values in for each variable in the expression. But, it can also be
    rendered as latex with numerical values inserted for variables.

    Variables are identified by wrapping them in \v{}
    """

    def __init__(self, text, units=None, variable_tag="v"):
        self.__text = text
        self.__units = units
        self.__variable_tag = variable_tag
        self.__sympy_var_name_mapping = (
            Parsers.get_sympy_compatible_variable_name_mapping(
                text, self.__variable_tag
            )
        )
        self.__subs = {}

    def add_substitution(self, name, val):
        if name not in self.__sympy_var_name_mapping:
            raise RuntimeError(
                rf"No variabled named '{name}' found in expression. Is it wrapped with a \{self.__variable_tag}{{}} command"
            )
        self.__subs[name] = val

    @property
    def latex(self):
        return Parsers.make_plain_latex(self.__text, self.__variable_tag)

    @property
    def latex_unit(self):
        q = x__Q_(1, self.__units)
        return "{:Lx}".format(q.units)

    @property
    def latex_with_units(self):
        return self.latex + r" \," + self.latex_unit

    @property
    def latex_with_substitutions(self):
        text = self.__text
        for n, v in self.__subs.items():
            if hasattr(v, "magnitude") and hasattr(v, "units"):
                v = f"{v:Lx}"
            v = str(v)
            var_text = "\\" + self.__variable_tag + "{" + n + "}"
            val_text = "(" + v + ")"
            text = text.replace(var_text, val_text)
        return Parsers.make_plain_latex(text, variable_tag=self.__variable_tag)

    @property
    def sympy_expr(self):
        expr = sympy.parsing.latex.parse_latex(
            Parsers.make_sympy_compatible(self.__text)
        )
        return expr

    def eval(self, Q_=None):
        """
        Evaluate an expression.

        _Very_ limited unit suport.

        If substitutions are quantities, they are first converted to base units.
        Then the numerical value is used in the sympy evaluation as a substitution.
        The result of the evaluation is taken as the numerical value of the base unit
        of the expressions unit and then unit coverted to the expressions units.

        i.e. given expression

        x y

        with with units "km" and substitutions

        x: 10 mm/us
        y: 2 ms

        x will be converted to 10,000 m/s and y will be covnerted to 2,000 s. The values x = 10,000
        and y = 2,000 will be passed to sympy for the valuation, which will return 20,000,000, which
        is taken to be in meter. The result is then converted to 20,000 km.

        Currently _NO_ dimensional analysis...
        """
        sympy_subs = {}
        for name, sympy_name in self.__sympy_var_name_mapping.items():
            if name not in self.__subs:
                raise RuntimeError(
                    f"Cannot evaluate expression, no substitution for variable '{name}'."
                )

            val = self.__subs[name]
            if hasattr(val, "magnitude") and hasattr(val, "units"):
                # convert all quantities to base units.
                val = val.to_base_units()
                val = val.magnitude
            sympy_subs[sympy_name] = val

        sympy_expr = self.sympy_expr
        val = float(sympy_expr.evalf(subs=sympy_subs))
        if self.__units is None:
            return val
        else:
            if Q_ is None:
                raise RuntimeError(
                    "A quantity class must be passed as an argument to `evel(...)` function if the expression has units.\ni.e.\n\nimport pint\nureg = pint.UnitRegistry()\nQ_ = ureg.Quanttity\n...\nexpression.eval(Q_)\n\n"
                )
            # get the results units in base units
            base_units = Q_(1, self.__units).to_base_units().units
            val = Q_(val, base_units).to(self.__units)
            return val

    @property
    def symbols(self):
        pass


class Equation:
    """
    A class representing an equation.

    An equation is just two expressions that are equal to each other.

    LHS = RHS
    """

    def __init__(self, text, units=None):
        lhs_text, rhs_text = text.split("=")
        self.__lhs_expr = Expression(lhs_text.strip(), units)
        self.__rhs_expr = Expression(rhs_text.strip(), units)

    @property
    def lhs(self):
        return self.__lhs_expr

    @property
    def rhs(self):
        return self.__rhs_expr

    @property
    def latex(self):
        return self.__lhs_expr.latex + " = " + self.__rhs_expr.latex

    @property
    def latex_with_substitutions(self):
        return (
            self.__lhs_expr.latex_with_substitutions
            + " = "
            + self.__rhs_expr.latex_with_substitutions
        )
