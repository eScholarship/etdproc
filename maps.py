

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

pq_lang_mapping = {
     'en': 'eng',
	 'af': 'afr',
	 'as': 'afr',
	 'an': 'ang',
	 'ar': 'ara',
	 'ae': 'ara',
	 'ah': 'ara',
	 'bq': 'baq',
	 'ca': 'cat',
	 'ch': 'chi',
	 'ce': 'chi',
	 'cr': 'hrv',
	 'cz': 'cze',
	 'da': 'dan',
	 'du': 'dum',
	 'de': 'dum',
	 'dl': 'dum',
	 'es': 'est',
	 'ef': 'est',
	 'ez': 'est',
	 'fi': 'fin',
	 'fn': 'fin',
	 'fl': 'dut',
	 'fr': 'fre',
	 'fe': 'fre',
	 'fs': 'fre',
	 'ga': 'glg',
	 'ge': 'ger',
	 'gn': 'ger',
	 'gr': 'gre',
	 'hi': 'haw',
	 'hn': 'haw',
	 'he': 'heb',
	 'hg': 'heb',
	 'hy': 'heb',
	 'hu': 'hun',
	 'eh': 'hun',
	 'ic': 'ice',
	 'ir': 'gle',
	 'it': 'ita',
	 'ie': 'ita',
	 'ja': 'eng',
	 'je': 'jpn',
	 'jp': 'jpr',
	 'ko': 'kor',
	 'ke': 'kor',
	 'la': 'lat',
	 'el': 'lat',
	 'lv': 'lav',
	 'li': 'lit',
	 'me': 'enm',
	 'no': 'nor',
	 'ne': 'nor',
	 'pn': 'per',
	 'pl': 'pol',
	 'ph': 'pol',
	 'pr': 'por',
	 'pe': 'por',
	 'ro': 'rum',
	 'ru': 'rus',
	 're': 'rus',
	 'sa': 'san',
	 'sd': 'nso',
	 'so': 'sot',
	 'sp': 'spa',
	 'sr': 'spa',
	 'sb': 'spa',
	 'se': 'spa',
	 'sl': 'spa',
	 'sw': 'swe',
	 'sg': 'swe',
	 'ss': 'syr',
	 'te': 'tha',
	 'to': 'nai',
	 'ts': 'ven',
	 'tu': 'tur',
	 'tw': 'tsn',
	 'uk': 'ukr',
	 'ue': 'ukr',
	 'we': 'wel',
	 'yi': 'yid',
}




