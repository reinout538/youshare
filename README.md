#YouShare tool.py is script for labeling publications as youshare candidates in Pure

#get all person records from Pure and select IDs, affiliations, YouShare-status, earliest start dt, latest end dt

#get all publicaties that meet YouShare-criteria - published after a specific date

#loop through publications and determine:

#1) if it has at least one internal author and internal organisation affiliation

#2) Open Access-classification Pure (VSNU-keyword)

#3) YouShare-status Pure (Taverne keyword)

#4) per author:

    #a) if (earliest) publication year not before earliest appointment year
    #b) if author is YouShare candidate
    
#5) determine if publication is eligible for YouShare

#6) create log as csv-file which can be used as source for bulk-edit keywords in Pure
