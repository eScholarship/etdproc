
# ============================================================
# A number of small class that organize mapping settings from DB   
# ============================================================
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

class escholmap:
    field = None
    typedata = None
    info = None
    def __init__(self, p1,p2,p3):
        self.field = p1
        self.typedata = p2
        self.info = p3


class silsmap:
    tag = None
    indicator1 = None
    indicator2 = None
    field = None
    sourcefield = None
    action = None
    info = None

    def __init__(self, p1,p2,p3,p4,p5,p6,p7):
        self.tag = p1
        self.indicator1 = p2
        self.indicator2 = p3
        self.field = p4
        self.sourcefield = p5
        self.action = p6
        self.info = p7


class harvestmap:
    tag = None
    indicator1 = None
    indicator2 = None
    field = None
    destfield = None
    action = None
    escholfield = None

    def __init__(self, p1,p2,p3,p4,p5,p6,p7):
        self.tag = p1
        self.indicator1 = p2
        self.indicator2 = p3
        self.field = p4
        self.destfield = p5
        self.action = p6
        self.escholfield = p7

class harvestEntry: 
    identifier = None 
    datestamp = None 
    attrs = None 
    isProcessed = None
    def __init__(self, p1,p2,p3,p4):
        self.identifier = p1
        self.datestamp = p2
        self.attrs = p3
        self.isProcessed = p4

class campusmap:
    code = None 
    instloc = None 
    namesuffix = None
    nameinmarc = None
    localid = None
    def __init__(self, p1,p2,p3,p4, p5):
        self.code = p1 
        self.instloc = p2 
        self.namesuffix = p3
        self.nameinmarc = p4
        self.localid = p5


cc_url_mapping = {
        'cc by':'https://creativecommons.org/licenses/by/4.0/',
        'cc by-nc':'https://creativecommons.org/licenses/by-nc/4.0/',
        'cc by-nc-nd':'https://creativecommons.org/licenses/by-nc-nd/4.0/',
        'cc by-nc-sa':'https://creativecommons.org/licenses/by-nc-sa/4.0/',
        'cc by-nd':'https://creativecommons.org/licenses/by-nd/4.0/',
        'cc by-sa':'https://creativecommons.org/licenses/by-sa/4.0/'
		}

marc_language_overrides = {
    "zh": "chi",
    "cs": "cze",
    "de": "ger",
    "el": "gre",
    "is": "ice",
    "mk": "mac",
    "mi": "mao",
    "ms": "may",
    "fa": "per",
    "ro": "rum",
    "sk": "slo",
    "bo": "tib",
    "cy": "wel",
}

