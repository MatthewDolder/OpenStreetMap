from bs4 import BeautifulSoup
import re

def scrapeAbbreviations():
    #This module uses BeautifulSoup to parse an HTML page containing a list of postal abbreviations.
    #notice the page is downloaded to the filesystem.  Attempting to use requests to grab the file real-time
    #let to http redirect errors.
    page = open('usps.html', "r")
    # page = requests.get("https://pe.usps.com/text/pub28/28apc_002.htm")
    data = []
    # print(page.read())
    page = page.read()
    soup = BeautifulSoup(page,"html.parser")

    # The followging block was sourced from thread: https://stackoverflow.com/questions/23377533/python-beautifulsoup-parsing-table
    table = soup.find('table', attrs={'id': 'ep533076'})
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])  # Get rid of empty values
    ######### reference ###############

        # this table parses rather ugly because it was designed to be human read.
    # The first row in suffixname has three columns then the list of abbreviations are on seperate rows with the first and last column empty.
    # Like so:
    # [['PrimaryStreet SuffixName', 'CommonlyUsed StreetSuffix orAbbreviation', 'Postal ServiceStandardSuffixAbbreviation'],
    # ['ALLEY',                                      'ALLEE',                                    'ALY'],
    #                                                ['ALLEY'],
    #                                                ['ALLY'],
    #                                                ['ALY'],
    # ['ANEX',                                        'ANEX',                                    'ANX'],
    #                                                ['ANNEX'],
    # and so on...

    # so we'll get creative.
    # we'll create a dictionary of abbreviations and corresponding suffix.
    # throw away the postal service standard.  We don't care.

    abbrevs = {}
    row = 0
    suffix = ''
    abbr = ''
    for d in data:
        if row > 0:  #throwaway header
            if len(d) == 3:  #if it's a 3 column row, the first column is our preffered suffix
                suffix = d[0]  #preffered
                abbr = d[1]    #abbreviation
            elif len(d) == 1:  #if it's a 1 column row, then the previous record contains our preffered suffix
                abbr = d[0]    #abbreviatoin
            abbrevs[abbr] = suffix.lower().capitalize()
        row += 1

    return (abbrevs)

def cleanAbbreviations(abbrevs):
    #after testing against the San Antonio streetmap dump, I found a postal abbreviation that caused more problems than it fixed.
    #The remainder looked ok.  This function can be used to remove others if desired.

    #Arc changed the street "Bois D Arc" to "Bois D Arcade" which is incorrect.
    #Arc also changed "Mission Arc" to "Mission Arcade".
    abbrevs.pop("ARC")


    return (abbrevs)

def getReplacements():
    #This function calls scrapeAbbreviations to get a list of values to search and replace.
    #It then creates compiled regex to be run by the replace procedure in main.

    abbrevs = scrapeAbbreviations()  #grab abbreviations from USPS page
    #print(abbrevs)
    abbrevs = cleanAbbreviations(abbrevs)  #remove any unwanted as desired.

    regFind = {}
    regReplace = {}
    i = 0
    for a in abbrevs.keys():
        # https://www.guru99.com/python-regular-expressions-complete-tutorial.html
        regFind[i] = re.compile(' ' + a + '\.*$', re.IGNORECASE)  # space plus abbreviation plus period at end of line
        ###used for debugging...
        #regFind[i] = re.compile(' WAY\.*$', re.IGNORECASE)  # space plus abbreviation plus period at end of line
        ##############
        regReplace[i] = ' ' + abbrevs[a]
        i += 1

    #print(regFind)
    #print(regReplace)

    Replacements = [regFind, regReplace]

    return Replacements


def UNITTEST_regex():
    #This was used to test and troubleshoot regex.  It is not part of the program flow from main.py
    streetbad = ['Saddle Way Drive','Matt St.', 'Matt St', 'Matt street', 'Matt STREET', 'Matt ST.', 'Matt st.']
    streetnew = []
    streetgood = ['Saddle Way Drive','Matt Street', 'Matt Street', 'Matt Street', 'Matt Street', 'Matt Street', 'Matt Street']
    replacements = getReplacements()
    regFind = replacements[0]
    regReplace = replacements[1]


    for s in streetbad:
        for i, r in regFind.items():
            # p = re.compile(r,re.IGNORECASE)
            fixed = r.sub(regReplace[i], s)
            if s != fixed:
                print(s, " : ", fixed)
                break  # only fix it once.
        streetnew.append(fixed)

    print(streetgood)
    print(streetnew)
    assert streetnew == streetgood

def replaceOne(bad, replacements):
    #This function is called from main.py for each unique street name found in the database.
    #it loops through the list of regex and makes a replacement if it finds an issue.
    #it does not attempt to fix multiple issues for a single name.

#    replacements = getReplacements()
    regFind = replacements[0]
    regReplace = replacements[1]

    for i, r in regFind.items():
        fixed = r.sub(regReplace[i], bad)
        if bad != fixed:
            print(bad, " : ", fixed)
            break  # only fix it once.

    return fixed

if __name__ == "__main__":
    UNITTEST_regex()
