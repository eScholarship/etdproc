
import json
import dateparser
import consts
from creds import base_urls
from datetime import datetime, date, timedelta
from maps import pq_lang_mapping, cc_url_mapping
from urllib.parse import quote


class etdcomputeValues:
    _xmlAttrs = None
    _packageId = None
    _compAttrs = {}
    def __init__(self, packageId):
        self._packageId = packageId
        self._compAttrs = {}
        # get all attributes and then use the already populated info as appropriate
        (_, _, xmlAttrs, compAttrs) = consts.db.getAttrs(packageId)
        self._xmlAttrs = json.loads(xmlAttrs)
        if compAttrs:
            self._compAttrs = json.loads(compAttrs)

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
                self._compAttrs["isEmbargoed"] = True
                self._compAttrs["embargodate"] = "2999-12-31"

        if end_date:
            self._compAttrs["embargodate"] = end_date.strftime('%Y-%m-%d')
            self._compAttrs["isEmbargoed"] = True
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
        # correct:   250528s2025####cau|||||obm|||||| ||eng|d
        # check:     250627s2025####cau|||||obm|||||| ||eng|d
        # incorrect: 250603s2025  cau|||||obm |||| ||eng d

        print("create record info")
        date = datetime.now().strftime('%y%m%d')

        # xml language need to convert en to eng
        lang = self.getLanguage()
        self._compAttrs["lang"] = lang
        self._compAttrs["recinfo"]  = f'{date}s{self._compAttrs["pub_year"]}####cau|||||obm|||||| ||{lang}|d'
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

        self._compAttrs["campuslocation"] = consts.campusinfo[schoolcode].instloc + ", California :"
        self._compAttrs["campusname"] = "University of California, " + consts.campusinfo[schoolcode].namesuffix
        self._compAttrs["campusshort"] = consts.campusinfo[schoolcode].code.lower()
        self._compAttrs["control655"] = consts.campusinfo[schoolcode].nameinmarc
        self._compAttrs["merrittbucket"] = self._compAttrs["campusshort"] + "_lib_etd"
        return

    def computeNotes(self):
        # need to create notes based on xml info about advisors 
        advisors = "Advisors: "
        members = "Committee members: "
        for advisor in self._xmlAttrs["advisors"]:
            advisors = advisors + f'{advisor["surname"]}, {advisor["fname"]}; '
        for member in self._xmlAttrs["members"]:
            members = members + f'{member["surname"]}, {member["fname"]}; '
       
        #strip and add full stop if needed
        notes = advisors.strip('; ') + '. '
        notes = notes + members.strip('; ') + '.'
        self._compAttrs["notes"] = notes

    # skip for now and see later how multilanguages are going to be represented in xml
    # May need a mapping for language code to language   
    # # iso639 should works 
    def computeLanguages(self, languages):
        self._compAttrs["languages"] = None
        # less important - open text list of languages
        if languages and languages != "English":
            return languages

        return None

    def computeAuthorsAdvisor(self):
        # need to compile the list from xml information - lastname, first middle format
        # need a comma at the end for marc record sake
        self._compAttrs["advisor"] = []
        for advisor in self._xmlAttrs["advisors"]:
            name = f'{advisor["surname"]}, {advisor["fname"]}'
            self._compAttrs["advisor"].append(name)
        names = ""
        creators = []
        for author in self._xmlAttrs["authset"]:
            name = f'{author["fname"]} {author["surname"]},' # note sure if it comma separated or not
            creators.append(f'{author["surname"]}, {author["fname"][0]}.')
            names = names + name

        self._compAttrs["creators"] = ';'.join(creators)
        self._compAttrs["authors"] = names.strip(',')
        self._compAttrs["mainauthor"] = f'{self._xmlAttrs["authset"][0]["surname"]},{self._xmlAttrs["authset"][0]["fname"]}'
        return

    def computeDept(self):
        # Start with this and see if something needs to change
        self._compAttrs["dept"] = self._xmlAttrs["discipline"]
        return

    def getescholAuthors(self):
        authors = []
        for author in self._xmlAttrs["authset"]:
            values = {}
            values["nameParts"] = {"fname":author["fname"],"lname":author["surname"], "mname": author["middle"]}
            values["email"] = author["email"]
            values["orcid"] = author["orcid"]
            authors.append(values)
        return authors

    def getescholIds(self):
        localIds = []
        #API doesn't allow ark
        #localIds.append({"id":self._compAttrs["merrittark"], "scheme":"ARK"})
        # what other ids can I provide
        localIds = {"id": self._xmlAttrs["external_id"], "scheme":"OTHER_ID", "subScheme":"proquest"}
        return localIds

    def getescholunits(self):
        units = []
        # get unit from campus settings
        units.append(self._compAttrs["campusshort"] + "_etd")
        # inst_contact in xml can be used to determine other units the article should go to
        return units

    def getcontributors(self):
        contribs = []
        # authinfo["middle"]
        for advisor in self._xmlAttrs["advisors"]:
            nameparts = {"fname": advisor["fname"],
                         "lname": advisor["surname"],
                         "mname": advisor["middle"]}
            contribs.append({"role":"ADVISOR", "nameParts": nameparts})

        return contribs

    def getsupplementaryFiiles(self):
        if not self._xmlAttrs["attachset"]:
            return None
        suppFiles = []
        linkbase = f'{base_urls.depositUrlBase}/{self._xmlAttrs["depositfolder"]}'
        for attachment in self._xmlAttrs["attachset"]:
            filename = attachment['name']
            # encode the link name
            link = f'{linkbase}/{filename}'    
            entry = { "file": filename, 
                     "fetchLink": quote(link, safe=":/?=&"), 
                     "title": attachment["descr"],
                     "size": "TBD" # TBD: need to get this from fileattrs
                     }
            # os.path.getsize(file_path)
            suppFiles.append(entry)
        return suppFiles

    def getcclicense(self):
        # get the actual license if present
        if "cclicense" in self._xmlAttrs and self._xmlAttrs["cclicense"]:
            abbr = self._xmlAttrs["cclicense"].lower()
            if abbr in cc_url_mapping:
                return cc_url_mapping[abbr]
            else:
                print("CC lincese not found in mapping " + abbr )

        return None

    def computeEscholValues(self):
        print("compute for eschol deposit json")   
        self._compAttrs["isPeerReviewed"] = True
        link = f'{base_urls.depositUrlBase}/{self._xmlAttrs["depositfolder"]}/{self._xmlAttrs["binary-name"]}'
        self._compAttrs["contentLink"] = quote(link, safe=":/?=&")
        self._compAttrs["escholauthors"] = self.getescholAuthors()
        self._compAttrs["escholIds"] = self.getescholIds()
        self._compAttrs["escholunits"] = self.getescholunits()
        self._compAttrs["escholadvisors"] = self.getcontributors()
        self._compAttrs["escholsupp"] = self.getsupplementaryFiiles() 
        self._compAttrs["cclicence"] = self.getcclicense()
        

    # read a marc attr set along with the package id it is associated with
    # start a json and add the following vales
    def saveComputedValues(self):
        print("generate computed values for one record")
        # get the json version of the attrs
        self.computeIfEmbargoed()
        self.computeRecInfo()
        self.computeTitleComps()
        self.computeCampusInfo()      
        self.computeNotes()
        self.computeAuthorsAdvisor()
        self.computeDept()
        self.computeLanguages(None) #TBD
        self.computeEscholValues()
        # does this depend upon the degree?
        self._compAttrs["genre"] = "Dissertations, Academic"
        consts.db.saveComputedValues(self._packageId, json.dumps(self._compAttrs,ensure_ascii=False))
        return



#x = "this is the link with space"
#print(quote(x))