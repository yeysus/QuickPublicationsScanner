# For fetching internet data.
# http://docs.python.org/library/urllib.html
# From http://www.boddie.org.uk/python/HTML.html
import urllib2
# For accessing argument variables.
# http://docs.python.org/library/sys.html
import sys
# For handling arguments passed to the python script.
# http://docs.python.org/library/getopt.html
import getopt
import string
# For manipulation of json documents.
# http://docs.python.org/library/json.html
import json
# For manipulating a xml structure.
# http://docs.python.org/library/xml.etree.elementtree.html
import xml.etree.ElementTree as ElementTree
# For pretty printing of xml.
# http://docs.python.org/library/xml.dom.minidom.html
import xml.dom.minidom as minidom
# Python implementation of Yaml: PyYAML: http://pyyaml.org/
# For handling of yaml objects.
# Install PyYAML under windows 64-Bit: Dec 2011: Some registry keys are missing.
#   Solution: From http://stackoverflow.com/questions/3652625/installing-setuptools-on-64-bit-windows
#   Copy HKLM\SOFTWARE\Python to HKLM\SOFTWARE\wow6432node\Python, but 
#       this will cause problems with binary distributions.
# Install PyYAML under linux:
#    cd /opt/python2.7.2/bin/
#    ./easy_install PyYAML
# import yaml

class PubScanner:

    def __init__ (self, name):
    	# _debug = 0: Do not print partial results.
        # _downloadUrls = 0: Do not look for the download urls of the new versions
        global _debug, _thisappname, _version, _termCounts, _basisUrl
        self.name = name
        _debug = 0
        _thisappname = "Quick Publications Scanner"
        _version = "0.1"
        # Build an empty dictionary for the terms (key) and counts (value).                     
        _termCounts = {}
        # pubmed search:
        # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?
        #     db=pubmed&rettype=count&term=software&mindate=2009&maxdate=2009
        _basisUrl = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"

    def fetchCounts (self, myUrl):
       
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib2.install_opener(opener)
            
            openUrl = urllib2.urlopen (myUrl)
            
        except IOError, (errno):
            return "%s" % (errno)
        
        rawContent = openUrl.read ()
        openUrl.close ()

        rawCount = rawContent.partition('<Count>')[2].partition('</Count>')[0]

        if (_debug == 1):
            print myUrl
            print "rawContent: " + rawContent        
            print rawCount
            print "\n"
        
        return rawCount

    def outputToConsole (self, outputString):
        print outputString    
    
    def outputToFile (self, outputFile, outputString):
        f = open (outputFile, 'w')
        f.write (outputString)
        f.close ()

    def start (self, terms, syear, eyear, outputFormat, outputFile):

        terms = terms.lower ()
        
        if (_debug == 1):
            print "Terms String: " + terms
        
        # TODO: +++ Eliminate duplicates in the passed argument list (terms). 
        # TODO: +++ syear and eyear must be a year.        
    
        if (terms != ''):
            termsArray = terms.split(",")
        
        _termCounts['all'] = ''
        _termCounts['years'] = ''
        # j ist used only instead of checking if _termCounts[termsElement] is empty or not.
        j = 0
        for i in range(int(syear), int(eyear) + 1):
            # TODO: myUrl as variable.
            midUrl = _basisUrl + 'db=pubmed&rettype=count' + '&mindate=' + str(i) + '&maxdate=' + str(i)

            if (_termCounts['years'] == ''):
                _termCounts['years'] = str(i)
            else:
                _termCounts['years'] = _termCounts['years'] + "," + str(i)

            if (terms != ''):
                for termsElement in termsArray:
                    myUrl = midUrl + '&term=' + termsElement 
                    if (j == 0):
                        _termCounts[termsElement] = self.fetchCounts (myUrl)
                    else:
                        _termCounts[termsElement] = _termCounts[termsElement] + "," + self.fetchCounts (myUrl)
            else:
                myUrl = midUrl
                if (_termCounts['all'] == ''):
                    _termCounts['all'] = self.fetchCounts (myUrl)
                else:
                    _termCounts['all'] = _termCounts['all'] + "," + self.fetchCounts (myUrl) 
            j = j + 1                    
        
        # Check:
        if (_debug == 1):
            # Print all counts.
            print "\nCounts:"
            for key, value in _termCounts.items ():
                print key, value              
    
        # Output:
        outputString = ''
        if (outputFormat == "json"):
            outputString = json.dumps(_termCounts, sort_keys = True, indent = 4)        
        elif (outputFormat == 'xml'):
            # Create the root element. 
            # For valid xml, the names cannot contain white spaces,
            # e.g. "Software Versions" would not work with xml parsers.
            xmlTree = ElementTree.Element ("TermCounts") 
            # Create the elements of the Tree.
            for key in _termCounts: 
                ElementTree.SubElement(xmlTree, key).text = _termCounts[key]
        
            # xmlTree has already a xml-like structure, and it can be printed with
            # print ElementTree.tostring (xmlTree)
            # giving back everything in one line e.g.
            # <root><a>A</a><b>B</b></root>
            # and it misses the declaration
            # <?xml version="1.0" encoding="UTF-8" ?>
        
            # Use minidom for prettyfying the xml output
            # introducing line breaks.
            outputString = minidom.parseString (ElementTree.tostring (xmlTree)).toprettyxml ()
        elif (outputFormat == 'csv'):
            for key, value in _termCounts.items ():
                outputString += key + "," + value + "\n"
        elif (outputFormat == 'yaml'):
            outputString = yaml.dump (_termCounts, width=80, indent=4)
        else:
            # Includes outputFormat == ''
            outputString = "\nOutput format " + outputFormat + " not recognized.\n" 
            
            for key, value in _termCounts.items ():
                outputString = outputString + "\n" + key + ": " + value 
    
        if (outputFile == ''):
            self.outputToConsole (outputString)
        else:
            self.outputToFile (outputFile, outputString)
        return       

    def print_version (self):
        print _version
        return
    
    def print_name (self):
        print _thisappname
        return

    def usage (self):
        print _thisappname + " " + _version
        print "Script to count all pubmed publications in year x with term y."
        print "Arguments:"
        print "-t          Terms. Comma-separated, case-insensitive list of" 
        print "            terms. Each term means one query."
        print "            Do not add spaces after the comma,"
        print "            e.g. -t software,computer is OK." 
        print "-s          Start Year. All years will be tried, each one with"
        print "            a separate query, until the end year is reached."
        print "-e          End Year."
        print "-o          Output. File name with the results."
        print "            If nothing indicated results will be printed to "
        print "            the standard output."
        print "-f          Format. Output format. One of json, xml, yaml, csv."
        print "-d          Debug. Prints some information on the console."
        print "-v          Version. Print version number of this script."
        print "-n          Name. Print name of this script."
        print "-h          Help. Print this help screen."
        print "--terms     Same as -t."
        print "--syear     Same as -s."
        print "--eyear     Same as -e."
        print "--output    Same as -o."
        print "--format    Same as -f."
        print "--debug     Same as -d."
        print "--version   Same as -v."
        print "--name      Same as -n."
        print "--help      Same as -h."
    
    # How to handle command-line arguments in Python:
    # http://www.faqs.org/docs/diveintopython/kgp_commandline.html
    def main (self, argv): 
        terms = ''
        syear = ''
        eyear = ''
        outputFormat = ''
        outputFile = '' 
                
        try:                                
            opts, args = getopt.getopt (sys.argv[1:], "t:s:e:o:f:dvnh", ["terms=", "syear=", "eyear=", "output=", "format=", "debug", "version", "name", "help"]) 
        except getopt.GetoptError:           
            self.usage ()                          
            sys.exit (2)
        
        for opt, arg in opts:                
            if opt in ("-h", "--help"):      
                self.usage ()                     
                sys.exit ()                  
            elif opt in ("-d", "--debug"):                
                global _debug               
                _debug = 1
            elif opt in ("-v", "--version"):
                self.print_version ()
                sys.exit ()
            elif opt in ("-n", "--name"):
                self.print_name ()
                sys.exit ()            
            elif opt in ("-t", "--terms"): 
                terms = arg
            elif opt in ("-s", "--syear"): 
                syear = arg
            elif opt in ("-e", "--eyear"): 
                eyear = arg
            elif opt in ("-o", "--output"):
                outputFile = arg
            elif opt in ("-f", "--format"):
                outputFormat = arg
    
        if ((syear != '') & (eyear != '')):
            self.start (terms, syear, eyear, outputFormat, outputFile)
        else:
            print "Please supply the start and end year." 
            self.usage ()
            sys.exit ()

# About Python and Reflection: http://bit.ly/zVc7Us   
o = PubScanner ('my object')
o.main (sys.argv[1:])
