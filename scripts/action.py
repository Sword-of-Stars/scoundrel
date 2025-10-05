class Action():
    def __init__(self, func, arg, msg):
        self.func = func
        self.arg = arg

        self.msg = msg
    
    def execute(self):
        return self.func(self.arg)
    
    def __repr__(self):
        return f"{self.msg} {self.arg}"