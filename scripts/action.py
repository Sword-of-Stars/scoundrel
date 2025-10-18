class Action():
    def __init__(self, func, arg, msg, rev=lambda *args, **kwargs: None):
        self.func = func
        self.arg = arg

        self.msg = msg

        self.rev = rev
        self.mem = []

    def reverse(self):
        self.rev(self.arg, *self.mem[1:]) # idx 0 is a string for all actions
    
    def execute(self):
        self.mem = self.func(self.arg)
        return self.mem[0]
    
    def __repr__(self):
        return f"{self.msg} {self.arg}"