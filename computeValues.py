import json
from dbIntf import etdDb, jscholDb, silsmap
from xml.sax.saxutils import escape
from datetime import datetime
from maps import pq_lang_mapping

# need to move these to const
db = etdDb()


class etdcomputeValues:
    campusinfo = None
    _pubNum = None
    _gwAttrs = None
    _xmlAttrs = None
    def __init__(self, pubnum):
        self.campusinfo = db.getCampusInfo()
        self._pubNum = pubnum
        (gwAttrs, xmlAttrs) = db.getAttrs(pubnum)
        self._gwAttrs = json.loads(gwAttrs)
        self._xmlAttrs = json.loads(xmlAttrs)


    def computeRecInfo(self):
        # 240507s2021\\\\cau|||||obm\\||||\||eng\d
        # date1 when the record was generated
        # year of ETD publication
        # {date}s{year}\\\\cau|||||obm\\||||\||{lang}\d
        print("create record info")
        date = datetime.now().strftime('%y%m%d')
        # get the date from xml.acceptdate (-4:) or comp date[:4] 
        year = "01/01/2023"[-4:]
        # xml language need to convert en to eng
        lang = 'eng'
        recinfo = f'{date}s{year}\\\\cau|||||obm\\||||\||{lang}\d'.replace('\\',' ')
        return recinfo

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

    def computeTitleComps(self, title):
        print("break the title by colon")
        maintitle, subtitle = self.splitTile(title)
        # add additional space and colon in case of a split
        if subtitle:
            maintitle = maintitle + " :"
        
        titleIndicator = '0'
        if title.startswith("The "):
            titleIndicator = '4'
        if title.startswith("An "):
            titleIndicator = '3'
        if title.startswith("A "):
            titleIndicator = '2'

        return maintitle, subtitle, titleIndicator

    def computeCampusInfo(self, schoolcode):
        print("get campus location and name from db")
        # for now just hardcode
        # get all the campus inf
        location = self.campusinfo[schoolcode].instloc + ", California :"
        fullname = "University of California, " + self.campusinfo[schoolcode].namesuffix + ","
        control655 = self.campusinfo[schoolcode].nameinmarc

        return location, fullname, control655


    def computeIfEmbargoed(self, escholid):
        # look at delayed and sales fields to determine embargo date
        # also determine if permanently embargoed
        # don't know which field has embargo info - maybe from xml
        print("get embargo date from eschol db")
        status, embargodate = jdb.getEmbargoDates(escholid)
        if embargodate:
            print("Found embargoed item")
            embargodate = json.loads(embargodate)
            return embargodate

        return None


    def computeEscholMerritt(self, title):
        print("get the eschol url")
        escholid = None
        escholurl = "https://escholarship.org/uc/item/"
        merrittark = ''
        # clear up title to search
        titleforeschol = escape(title.strip(" /"))
        localids = jdb.getEscholIds(titleforeschol)
        assert(len(localids) < 2)

        for id in localids:
            escholid = id
            escholurl += id
            for others in json.loads(localids[id]):
                if others["type"] == "merritt":
                    merrittark = others["id"]
        
        # get id and list of local_ids

        # make url and merrittark

        return escholid, escholurl, merrittark

    def computekeywords(self, escholid):
        # get keywords from xml
        print("compute keywords")
        kws = jdb.getKeywords(escholid)
        if kws:
            return json.loads(kws)
        else:
            return None

    def processNotes(self, note):
        # need to create notes based on xml info about advisors and committee members
        # may need additional rules in future
        print("check for committee member and add dot")
        
        if "Committee members" in note:
            parts = note.split("Committee members")
            note = ". Committee members".join(part.strip().strip(".") for part in parts)

        #strip and add full stop if needed
        pnote = note.strip('.').strip() + '.'
        return pnote

    def computeNotes(self, pqNotes):
        print("process the notes and create new")
        compNotes = []
        for note in pqNotes:
            if note.startswith("Source:") == False:
                compNotes.append(self.processNotes(note))

        return compNotes
        
    def computeLanguages(self, languages):
        # less important - open text list of languages
        if languages and languages != "English":
            return languages

        return None

    def computeAdvisor(self, pqadvisor):
        # need to compile the list from xml information - lastname, first middle format
        # need a comma at the end for marc record sake
        compadvisor = []

        for advisors in pqadvisor:
            compadvisor.append(advisors + ',') 

        return compadvisor

    def computeDept(self, dept):
        # break the dept string by space - split only 
        # this needs to come from xml
        parts = dept.rsplit(" ",1)
        if len(parts) > 1 and parts[1][0].isdigit():
            # return the part without the last. make sure to add fullstop
            return parts[0] + '.'
        return dept

    # read a marc attr set along with the package id it is associated with
    # start a json and add the following vales
    def generateForOneRecord(self):
        print("generate computed values for one record")
        # get the json version of the attrs
        compattrs = {}
        attrs = json.loads(pqAttrs)
        #isbn = attrs["isbn"]
        compattrs["recinfo"] = self.computeRecInfo(attrs["recinfo"])
        compattrs["maintitle"], compattrs["subtitle"], compattrs["titleIndicator"] = self.computeTitleComps(attrs["title"])
        compattrs["campuslocation"], compattrs["campusfullname"], compattrs["control655"] = self.computeCampusInfo(attrs["schoolcode"])
        #compattrs["pagecount"] = self.computePagecount(attrs["pagecount"]) - not needed
        compattrs["escholark"], compattrs["escholurl"], compattrs["merrittark"] = self.computeEscholMerritt(attrs["title"])
        # if the item was not found in eschol skip this
        if not compattrs["escholark"]:
            return None
        compattrs["embargodate"] = self.computeIfEmbargoed(compattrs["escholark"])
        compattrs["keywords"] = self.computekeywords(compattrs["escholark"])
        compattrs["genre"] = "Dissertations, Academic"
        compattrs["notes"] = self.computeNotes(attrs["notes"])
        compattrs["languages"] = self.computeLanguages(attrs["languages"])
        compattrs["pubyear"] = attrs["pubyear"] + "."
        compattrs["advisor"] = self.computeAdvisor(attrs["advisor"])
        compattrs["mainauthor"] = attrs["mainauthor"].strip(',').strip() + ',' #remove trailing space before comma
        compattrs["dept"] = self.computeDept(attrs["dept"])
        return compattrs

    # read one package
    def generateComputedValules(self, campus):
        print("generate record")
        campusId = db.getCampusId(campus)
        # read all marc metadata rows
        attrs = db.getAttrs(campusId)

        for pid in attrs:
            # return value of attrs is a tuple
            record = self.generateForOneRecord(attrs[pid])
            if record:
                print(record)
                db.saveCompMarcValues(pid, json.dumps(record,ensure_ascii=False))

print("start")
x = etdcomputeValues("30492756")
#campuses = ["UCD","UCI","UCM","UCR","UCSC","UCSB","UCSD","UCLA","UCB","UCSF"]
##campuses = ["UCSF"]
#for code in campuses:
#    x.generateComputedValules(code)
print("end")