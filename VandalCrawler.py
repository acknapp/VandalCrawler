""" VandalCrawler crawls through a webpage and recursively goes through eachlink 
on that page, identifying and making a list of any vandalized websites as it goes."""
# Uses BeautifulSoup for it's web parser: http://www.crummy.com/software/BeautifulSoup/

# And now for some legal:
# Copyright (c) 2011, Andrew Knapp

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:

#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.

#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.

#  * Neither the name of VandalCrawler nor the names of its contributors may be
#    used to endorse or promote products derived from this software
#    without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

import urllib2
import urlparse
import BeautifulSoup
import time
import sys

#Data Structure City!
complexSite = sys.argv[1]
brokenLinks = []
allLinks = []
vandalizedSites = []
siteConnection = {}

#Log files
outputFile = open('urlOutput.log', 'w')
summaryFile = open('summary.log', 'w')
vandalSites = open('vandalizedSites.log', 'w')
connectionMap = open('siteConnectionsMap.map', 'w')

#keyword filter to identify bad sites, may need to be customized to domain
badKeyWords = {'poker' : 15, 'viagra': 5, 'cialis': 5, 'buy viagra': 1, 'amateur sex': 1, 'milf': 3, 'xenical' : 3, 'lisinopril' : 6}

#If extra domains beyond the main one should be included add them here
extraDomains = []

def checkBadContent(site, page):
    """Checks a website for bad content noting the url"""
    for key in badKeyWords.keys():
	if page.count(key) > badKeyWords[key]:
	    vandalizedSites.append(site)
  
def baseSite(site):
    """Identifies the base domain given a url and returns it"""
    n = site.count('.') 
    if n <= 1:
	if site.count('/') > 0:
	  temp2 = site.split('/')
	  site = temp2[0]
	return site
    else:
	temp = site.split('.', 1)
	i = len(temp) - 1
	site = baseSite(temp[i])
	return site

def checkDomain(site, rootSite):
    """Checks to see if a site is within the given domain"""
    oSite = urlparse.urlparse(rootSite)
    regDomain = baseSite(oSite.netloc)
    siteBase = urlparse.urlparse(site)
    siteDomain = baseSite(siteBase.netloc)
    return regDomain in site or siteDomain in extraDomains

def checkAllLinks(site):
    """Checks to see if site is in sites already scanned"""
    return site not in allLinks

def findLinks(page, site, soup):
    """Retrieves all the urls from a website and returns them as a list"""
    siteLinks = []
    for page in soup.findAll("a"):
	try:
	    lnk = page['href'].encode('latin-1')
	    newSite = urlparse.urljoin(site, lnk)
	    siteLinks.append(newSite)
	except:
	    pass
    for page in soup.findAll("img"):
	try:
	    lnk2 = page['src'].encode('latin-1')
	    newLnk = urlparse.urljoin(site, lnk2)
	    siteLinks.append(newLnk)
	except:
	    pass
    return siteLinks

def crawlSites(rootSite): 
	"""Main crawler function"""
	siteLinks = []
	print rootSite #see link collection in action!
	try:
	    page = urllib2.urlopen(rootSite).read()
	    allLinks.append(rootSite)
	    checkBadContent(rootSite, page)
	    soup = BeautifulSoup.BeautifulSoup(page)
	    siteLinks = findLinks(page, rootSite, soup)
	    siteConnection[rootSite] = siteLinks
	    for site in siteLinks:
		if checkAllLinks(site) and len(siteLinks) > 0 and site.startswith('http://') and checkDomain(site, complexSite):
		    crawlSites(site)
	except:
	    brokenLinks.append(rootSite)

#Log Writing Functions
def summaryOutput(ofile):
    line1 = "Summary: "
    line2 = "Total runtime: " + str(y - x) + " seconds"
    line3 = "Total Sites: " + str(len(allLinks))
    line4 = "Potential bad sites: " + str(len(vandalizedSites))
    line5 = "Percent of bad sites: " + str(100.00 * len(vandalizedSites)/len(allLinks)) + "%"  
    summaryLines = [line1, line2, line3, line4]
    for line in summaryLines:
	print line
	ofile.write(line + "\n")
    ofile.close()
    
def output(ofile):
    lineHeader = "All Domain Sites Scanned: "
    ofile.write(lineHeader + "\n")
    for site in allLinks:
	ofile.write(site + "\n")
    ofile.close()
    
def saveVandalizedSites(ofile):
    lineHeader = "Potentially Vandalized or Compromised Sites: "
    ofile.write(lineHeader + "\n")
    for site in vandalizedSites:
	ofile.write(site + "\n")
    ofile.close()
    
def saveMap(dtn, mapFile):
    for k in dtn:
	z = k, dtn[k]
	mapFile.write(z)

#Program Run Area
x = time.time()
crawlSites(complexSite)
output(outputFile)
saveVandalizedSites(vandalSites)
saveMap(siteConnection, connectionMap)
y = time.time()
summaryOutput(summaryFile)
