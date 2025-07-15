

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


def cleanResponse(text):
    # Remove single and double quotes
    text = text.replace("'", "").replace('"', "")
    # Limit string length to 900 characters
    return text[:900]


cc_url_mapping = {
        'cc by':'https://creativecommons.org/licenses/by/4.0/',
        'cc by-nc':'https://creativecommons.org/licenses/by-nc/4.0/',
        'cc by-nc-nd':'https://creativecommons.org/licenses/by-nc-nd/4.0/',
        'cc by-nc-sa':'https://creativecommons.org/licenses/by-nc-sa/4.0/',
        'cc by-nd':'https://creativecommons.org/licenses/by-nd/4.0/',
        'cc by-sa':'https://creativecommons.org/licenses/by-sa/4.0/'
		}


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




