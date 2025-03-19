

class pqmap:
    tag = None
    field = None
    attr = None
    isMulti = None

    def __init__(self, p1,p2,p3,p4):
        self.tag = p1
        self.field = p2
        self.attr = p3
        self.isMulti = True if p4 == "True" else False

class silsmap:
    tag = None
    indicator1 = None
    indicator2 = None
    field = None
    sourcefield = None
    info = None

    def __init__(self, p1,p2,p3,p4,p5,p6):
        self.tag = p1
        self.indicator1 = p2
        self.indicator2 = p3
        self.field = p4
        self.sourcefield = p5
        self.info = p6


class campusmap:
    code = None 
    instloc = None 
    namesuffix = None
    nameinmarc = None
    def __init__(self, p1,p2,p3,p4):
        self.code = p1 
        self.instloc = p2 
        self.namesuffix = p3
        self.nameinmarc = p4
