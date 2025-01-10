"""Module for our own calculations"""

from math import factorial as factorial_
from exeptions import CalculationError

__all__=['factorial']
def factorial(num):
    try:
        return factorial_(num)
    except ValueError:
        raise CalculationError()