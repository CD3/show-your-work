import copy

import sympy
import sympy.parsing.latex
from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity


class Expression:
    """
    A class representing one side of an equagtion (typically the right-hand side).

    An expression is defined in LaTeX. It can be _evaluated_, a numerical value is calculated by
    inserting numerical values in for each variable in the expression. But, it can also be
    rendered as latex with numerical values inserted for variables.

    Variables are identified by wrapping them in \mathit{}
    """

    def __init__(self, text, units=None):
        self.__text = text
        self.__units = units
        if self.__units is not None:
            self.__units = Q_(self.__units).units
        self.__expr = sympy.parsing.latex.parse_latex(self.__text)
        self.__subs = {}

    def add_sub(self, name, val):
        self.__subs[name] = val

    @property
    def latex(self):
        if self.__units is not None:
            return self.__text + " {:Lx}".format(self.__units)
        else:
            return self.__text

    @property
    def expr(self):
        return self.__expr

    def eval(self, **kwargs):
        kwargs.update(self.__subs)
        val = float(self.__expr.evalf(subs=kwargs))
        if self.__units is None:
            return val
        else:
            return Q_(val, self.__units)

    def sub_latex(self, **kwargs):
        kwargs.update(self.__subs)
        text = self.latex
        for symbol in self.__expr.free_symbols:
            if str(symbol) in kwargs:
                val = kwargs[str(symbol)]
                if type(val) is Q_:
                    val = f"{val:Lx}"
                else:
                    val = str(val)
                text = text.replace(
                    r"\mathit{" + str(symbol) + "}", rf"\left({val}\right)"
                )

        return text

    @property
    def symbols(self):
        pass
