from exeptions import CalculationError

__all__ = ["add","divider_2"]

def add(x, y):
    """Sum function"""
    return x + y


def divider(x, y):
    try:
        return x/y
    except ZeroDivisionError:
        print("Devizion by zero!")


def divider_2(x, y):
    if y !=0:
        return x/y
    raise CalculationError()
