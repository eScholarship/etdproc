import json
from dbIntf import etdDb, jscholDb, silsmap
from xml.sax.saxutils import escape
from datetime import datetime, date, timedelta
import dateparser
from maps import pq_lang_mapping

# need to move these to const
db = etdDb()
campusinfo = db.getCampusInfo()

class etdcomputeValues:
    campusinfo = None
    _pubNum = None
    _gwAttrs = None
    _xmlAttrs = None
    _compAttrs = {}
    def __init__(self, pubnum):
        self._pubNum = pubnum
        (gwAttrs, xmlAttrs) = db.getAttrs(pubnum)
        self._gwAttrs = json.loads(gwAttrs)
        self._xmlAttrs = json.loads(xmlAttrs)

    # Update to publication date when xml is populated with that
    def computeDecisionDate(self):
        print("Compute all dates - acceptance and decision dates")
        # get the decision date and use that as publication date
        if "agreement_decision_date" in self._xmlAttrs and self._xmlAttrs["agreement_decision_date"]:
            decision_date = self._xmlAttrs["agreement_decision_date"]
        elif "comp_date" in self._xmlAttrs and self._xmlAttrs["comp_date"]:
            decision_date = self._xmlAttrs["comp_date"]
        else:
            decision_date = self._xmlAttrs["accept_date"]

        decision = dateparser.parse(decision_date)
        if decision:
            decision = decision.date()
        else:
            decision = date.today()
         # if data is Jan 1st - change to Dec 31st
        if decision.month == 1 and decision.day == 1:
            decision = datetime.date(decision.year, 12, 31)

        return decision

    def computeDates(self):
        print("compute publication date and year")
        decision = self.computeDecisionDate()
        self._compAttrs["pub_date"] = decision.strftime('%Y-%m-%d')
        self._compAttrs["pub_year"] = decision.strftime('%Y')
        self._compAttrs["pubyear"] = self._compAttrs["pub_year"] + "."
        return decision

    def computeIfEmbargoed(self):
        self._compAttrs["isEmbargoed"] = False
        self._compAttrs["isPermEmbargoed"] = False
        decision = self.computeDates()
        # UCSB specific rule
        if self._xmlAttrs["inst_code"] == "0035":
            if self._xmlAttrs["access_option"] != "Open access":
                self._compAttrs["isPermEmbargoed"] = True

        if self._xmlAttrs["delayed_release"] == "never deliver":
            self._compAttrs["isPermEmbargoed"] = True

        if self._compAttrs["isPermEmbargoed"]:
            self._compAttrs["isEmbargoed"] = True
            return

        if self._xmlAttrs["embargo_code"] == '0':
            # not embargoed
            return 
        end_date = None
        if self._xmlAttrs["embargo_code"] == '1' or self._xmlAttrs["delayed_release"] == '6 months':
            end_date = decision + timedelta(days=180)
        if self._xmlAttrs["embargo_code"] == '2' or self._xmlAttrs["delayed_release"] == '1 years':
            end_date = decision + timedelta(days=365)
        if self._xmlAttrs["embargo_code"] == '3' or self._xmlAttrs["delayed_release"] == '2 years':
            end_date = decision + timedelta(days=730)

        if self._xmlAttrs["embargo_code"] == '4':
            end_date = dateparser.parse(self._xmlAttrs["sales_restriction_remove"])
            if end_date:
                end_date = end_date.date()
            else:
                self._compAttrs["isPermEmbargoed"] = True

        if end_date:
            self._compAttrs["embargoEndDate"] = end_date.strftime('%Y-%m-%d')
        return

    def getLanguage(self):
        lang = 'en' # default
        if self._xmlAttrs["language"]:
            lang = self._xmlAttrs["language"]
        return pq_lang_mapping[lang]

    def computeRecInfo(self):
        # 240507s2021\\\\cau|||||obm\\||||\||eng\d
        # date1 when the record was generated
        # year of ETD publication
        # {date}s{year}\\\\cau|||||obm\\||||\||{lang}\d
        print("create record info")
        date = datetime.now().strftime('%y%m%d')

        # xml language need to convert en to eng
        lang = self.getLanguage()
        self._compAttrs["recinfo"]  = f'{date}s{self._compAttrs["pub_year"]}\\\\cau|||||obm\\||||\||{lang}\d'.replace('\\',' ')
        return

    def splitTile(self, title):
        # need to split at : but only is it is not in middle of bracket
        maintitle = title
        subtitle = None
        bracket_level = 0
        current = []

        for c in title:
            if c == ":" and bracket_level == 0:
                # just need one split
                maintitle = "".join(current)
                subtitle = title[len(maintitle)+1:] 
                return maintitle, subtitle.strip()
            else:
                if c == "{" or c == "(" or c == "[":
                    bracket_level += 1
                elif c == "}" or c == ")" or c == "]":
                    bracket_level -= 1
                current.append(c)

        return maintitle, subtitle

    def computeTitleComps(self):
        print("break the title by colon")
        title = self._xmlAttrs["title"]
        maintitle, subtitle = self.splitTile(title)
        # add additional space and colon in case of a split
        if subtitle:
            maintitle = maintitle + " :"
            subtitle = subtitle + ' /' # need to add for marc
        else:
            maintitle = maintitle + ' /' # need to add for marc
        
        titleIndicator = '0'
        if title.startswith("The "):
            titleIndicator = '4'
        if title.startswith("An "):
            titleIndicator = '3'
        if title.startswith("A "):
            titleIndicator = '2'

        self._compAttrs["maintitle"] = maintitle
        self._compAttrs["subtitle"] = subtitle
        self._compAttrs["titleIndicator"] = titleIndicator
        return

    def computeCampusInfo(self):
        print("get campus location and name from db")
        schoolcode = self._xmlAttrs["inst_code"]

        self._compAttrs["campuslocation"] = campusinfo[schoolcode].instloc + ", California :"
        self._compAttrs["campusfullname"] = "University of California, " + campusinfo[schoolcode].namesuffix + ","
        self._compAttrs["control655"] = campusinfo[schoolcode].nameinmarc
        return

    # this needs to go away from here and moved to when we do eschol and merritt interaction
    def computeEscholMerritt(self):
        print("get the eschol url")
        self._compAttrs["escholark"] = "qt5cq8c801"
        self._compAttrs["escholurl"] = "uhttps://escholarship.org/uc/item/qt5cq8c801"
        self._compAttrs["merrittark"] = "ark:/13030/m51086wv"
        escholid = None
        #escholurl = "https://escholarship.org/uc/item/"

        return

    def computeNotes(self):
        # need to create notes based on xml info about advisors 
        advisors = "Advisors: "
        members = " Committee members: "
        for advisor in self._xmlAttrs["advisors"]:
            advisors = advisors + f'{advisor["surname"]},{advisor["fname"]}; '
        for member in self._xmlAttrs["members"]:
            members = members + f'{member["surname"]},{member["fname"]}; '
       
        #strip and add full stop if needed
        notes = advisors.strip('; ').strip() + '.'
        notes = notes + members.strip('; ').strip() + '.'
        self._compAttrs["notes"] = notes

    # skip for now and see later how multilanguages are going to be represented in xml
    # May need a mapping for language code to language   
    # # iso639 should works 
    def computeLanguages(self, languages):
        # less important - open text list of languages
        if languages and languages != "English":
            return languages

        return None

    def computeAdvisor(self):
        # need to compile the list from xml information - lastname, first middle format
        # need a comma at the end for marc record sake
        self._compAttrs["advisor"] = []
        for advisor in self._xmlAttrs["advisors"]:
            name = f'{advisor["surname"]},{advisor["fname"]}'
            self._compAttrs["advisor"].append(name)

        return

    def computeDept(self):
        # Start with this and see if something needs to change
        self._compAttrs["dept"] = self._xmlAttrs["discipline"]

        return

    # read a marc attr set along with the package id it is associated with
    # start a json and add the following vales
    def saveComputedValues(self):
        print("generate computed values for one record")
        # get the json version of the attrs
        self.computeIfEmbargoed()
        self.computeRecInfo()
        self.computeTitleComps()
        self.computeCampusInfo()
        self.computeEscholMerritt()
        
        self.computeNotes()
        self.computeAdvisor()
        self.computeDept()
        packageid = db.getPackageId(self._pubNum)
        db.saveComputedValues(packageid, json.dumps(self._compAttrs,ensure_ascii=False))
        return

print("start")
x = etdcomputeValues("30492756")
x.saveComputedValues()
#campuses = ["UCD","UCI","UCM","UCR","UCSC","UCSB","UCSD","UCLA","UCB","UCSF"]
##campuses = ["UCSF"]
#for code in campuses:
#    x.generateComputedValules(code)
print("end")