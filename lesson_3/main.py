"""This is a main module for our app."""
import logging
import math as mt
from math import (
    cos, 
    sqrt, 
    pow, 
    sin, 
    tan,
    )
from array import array

import pandas as pd

from exeptions import CalculationError
from math_operators import divider_2, factorial


logger = logging.getLogger(__name__)


def main():
    try:
        print(divider_2(1, 0))
        print(factorial(8))
    except CalculationError as e:
        print(e.status)
    result = mt.factorial(8)
    result_2 = factorial(8)

    

if __name__=='__main__':
    main()



