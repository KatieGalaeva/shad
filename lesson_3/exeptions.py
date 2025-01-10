class CalculationError(Exception):
    """check our own"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = 400
        