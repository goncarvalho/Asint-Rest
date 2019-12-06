class Office:
    def __init__(self, name, op_h, loc, description):
        self.name = name
        self.opening_hours = op_h
        self.location = loc
        self.description = description

    def __str__(self):
        return "%d - %s - %s - %s - %s" % (self.id, self.author, self.title, self.year, self.likes)
