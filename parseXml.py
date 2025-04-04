
# get the zip file
# send to Merritt
#
# open xml file
# extract data including ID from proquest
# call api to get xml
# extract the marcxml from the response

# use the information in the attrs to create marc records
# use the information to create json for eschol deposit


import lxml.etree as ET
import json
from dbIntf import etdDb

class etdParseXml:
    _data = {}
    _dbparams = []
    _xpatheval = None
    def __init__(self):
        print("get the path to the folder where content lives")
        self._data = {}
        self._xpatheval = None

    def convertToJson(self, pqfile):
        print("convert from proquest to marc")
        # run xslt on the given file
        dom = ET.parse(pqfile)
        self._xpatheval = ET.XPathEvaluator(dom)
        self.getpubNumber()
        self.addAuthSet()
        self.addAdvisorSet()
        self.addMemberSet()
        self.addDescription()
        self.addDegreeInfo()
        self.addAbstract()
        self.addContent()
        self.addRights()
        self.addKeywordsDiscipline()
        print(self._data)
        print("Done")

    def getFirstValue(self, element, path):
        print("get first value if present")
        values = element.findall(path)
        if values and len(values) > 0:
            return values[0].text
        return None

    def getpubNumber(self):
        identifiers = self._xpatheval("/DISS_submission/DISS_description/DISS_identifiers")[0]
        self._data["pubNumber"] = self.getFirstValue(identifiers, "pubNumber")
        assert(self._data["pubNumber"])
        return

    def addAuthSet(self):
        authors = self._xpatheval("/DISS_submission/DISS_authorship/DISS_author")
        self._data["authset"] = []
        for author in authors:
            authinfo = {}
            authinfo["surname"] = self.getFirstValue(author, "DISS_name/DISS_surname")
            authinfo["fname"] = self.getFirstValue(author, "DISS_name/DISS_fname")
            authinfo["middle"] = self.getFirstValue(author, "DISS_name/DISS_middle")
            authinfo["suffix"] = self.getFirstValue(author, "DISS_name/DISS_suffix")

            authinfo["email"] = self.getFirstValue(author, "DISS_contact/DISS_email")
            authinfo["school_email"] = self.getFirstValue(author, "DISS_contact/DISS_school_email")
            authinfo["orcid"] = self.getFirstValue(author,"DISS_orcid")
            self._data["authset"].append(authinfo)
        return

    def addAdvisorSet(self):
        advisors = self._xpatheval("/DISS_submission/DISS_description/DISS_advisor")
        self._data["advisors"] = []
        for advisor in advisors:
            info = {}
            info["surname"] = self.getFirstValue(advisor, "DISS_name/DISS_surname")
            info["fname"] = self.getFirstValue(advisor, "DISS_name/DISS_fname")
            info["middle"] = self.getFirstValue(advisor, "DISS_name/DISS_middle")
            info["suffix"] = self.getFirstValue(advisor, "DISS_name/DISS_suffix")

            self._data["advisors"].append(info)
        return

    def addMemberSet(self):
        members = self._xpatheval("/DISS_submission/DISS_description/DISS_cmte_member")
        self._data["members"] = []
        for member in members:
            info = {}
            info["surname"] = self.getFirstValue(member, "DISS_name/DISS_surname")
            info["fname"] = self.getFirstValue(member, "DISS_name/DISS_fname")
            info["middle"] = self.getFirstValue(member, "DISS_name/DISS_middle")
            info["suffix"] = self.getFirstValue(member, "DISS_name/DISS_suffix")

            self._data["members"].append(info)
        return

    def addDescription(self):
        submission = self._xpatheval("/DISS_submission")[0]
        self._data["embargo_code"] = submission.attrib["embargo_code"]
        self._data["publishing_option"] = submission.attrib["publishing_option"]
        self._data["third_party_search"] = submission.attrib["third_party_search"]
        description =  self._xpatheval("/DISS_submission/DISS_description")[0]
        self._data["page_count"] = description.attrib["page_count"]
        self._data["type"] = description.attrib["type"]
        self._data["external_id"] = description.attrib["external_id"]
        self._data["apply_for_copyright"] = description.attrib["apply_for_copyright"]
        return

    def addDegreeInfo(self):
        description =  self._xpatheval("/DISS_submission/DISS_description")[0]
        self._data["title"] = self.getFirstValue(description, "DISS_title")
        self._data["degree"] = self.getFirstValue(description, "DISS_degree")
        self._data["comp_date"] = self.getFirstValue(description, "DISS_dates/DISS_comp_date")
        self._data["accept_date"] = self.getFirstValue(description, "DISS_dates/DISS_accept_date")
        self._data["inst_code"] = self.getFirstValue(description, "DISS_institution/DISS_inst_code")
        self._data["inst_name"] = self.getFirstValue(description, "DISS_institution/DISS_inst_name")
        self._data["inst_contact"] = self.getFirstValue(description, "DISS_institution/DISS_inst_contact")
        return

    def addAbstract(self):
        lines = self._xpatheval("/DISS_submission/DISS_content/DISS_abstract/DISS_para")
        self._data["abstractLines"] = []
        for line in lines:
            self._data["abstractLines"].append(line.text)
        return

    def addContent(self):
        # get the binary
        print("add content info here")
        content = self._xpatheval("/DISS_submission/DISS_content")[0]
        # get all the attachments
        binary = content.findall("DISS_binary")[0]
        self._data["binary-name"] = binary.text
        self._data["binary-type"] = binary.attrib["type"]
        attachments = self._xpatheval("/DISS_submission/DISS_content/DISS_attachment")
        self._data["attachset"] = []
        for attachment in attachments:
            attachinfo = {}
            attachinfo["name"] = self.getFirstValue(attachment, "DISS_file_name")
            attachinfo["category"] = self.getFirstValue(attachment, "DISS_file_category")
            attachinfo["descr"] = self.getFirstValue(attachment, "DISS_file_descr")
            self._data["attachset"].append(attachinfo)
        return

    def addRights(self):
        print("add rights")
        repo = self._xpatheval("/DISS_submission/DISS_repository")[0]
        self._data["agreement_decision_date"] = self.getFirstValue(repo, "DISS_agreement_decision_date")
        self._data["repo_acceptance"] = self.getFirstValue(repo, "DISS_acceptance")
        self._data["delayed_release"] = self.getFirstValue(repo, "DISS_delayed_release")
        self._data["access_option"] = self.getFirstValue(repo, "DISS_access_option")
        cclic = self._xpatheval("/DISS_submission/DISS_creative_commons_license/DISS_abbreviation")
        if cclic:
            self._data["access_option"] = self.getFirstValue(repo, "DISS_access_option")
        restriction = self._xpatheval("/DISS_submission/DISS_restriction/DISS_sales_restriction")
        if restriction:
            self._data["sales_restriction_code"] = restriction[0].attrib["code"]
            self._data["sales_restriction_remove"] = restriction[0].attrib["remove"]
        return

    def addKeywordsDiscipline(self):
        print("add keywords discipline")
        cat_desc =  self._xpatheval("/DISS_submission/DISS_description/DISS_categorization/DISS_category/DISS_cat_desc")
        if cat_desc:
            self._data["discipline"] = cat_desc[0].text
        # there are multiple keywords
        self._data["keywords"] = []
        keywords = self._xpatheval("/DISS_submission/DISS_description/DISS_categorization/DISS_keyword")
        for keyword in keywords:
            if keyword:
                self._data["keywords"].append(keyword[0].text)

        lang = self._xpatheval("/DISS_submission/DISS_description/DISS_categorization/DISS_language")
        if lang:
            self._data["language"] = lang[0].text



    def saveToDb(self):
        print("save the xml extracted data in ")
        # save - xmlmetadata table
        db = etdDb()
        metadata = json.dumps(self._data,ensure_ascii=False)
        packageid = db.getPackageId(self._data["pubNumber"])
        db.savexmlMetadata(packageid, metadata)
        return


print("Start")
a = etdParseXml()
a.convertToJson("C:/Temp/Bartke_berkeley_0028E_22277_DATA.xml")
a.saveToDb() 
print("End")

