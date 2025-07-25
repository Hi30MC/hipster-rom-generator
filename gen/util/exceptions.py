class MissingParameterError(Exception):
    def __init__(self, path: str, param: str):
        self.path = path
        self.param = param
        super().__init__(self.__str__())

    def __str__(self):
        return f"No value '{self.param}' defined in '{self.path}/rom_params.txt'."

class ParameterValueError(Exception):
    def __init__(self, path: str, param: str):
        self.path = path
        self.param = param
        super().__init__(self.__str__())

    def __str__(self):
        return f"Invalid value of '{self.param}' defined in '{self.path}/rom_params.txt'."

class KeyOverloadError(Exception):    
    def __init__(self):
        super().__init__(self.__str__())

    def __str__(self):
        return "No wait move defined and is unable to be automatically created to pad the sequence to length. Maybe try defining one or making your sequence longer?"

