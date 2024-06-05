#YouShare tool.py is script for labeling publications as youshare candidates in Pure-VU
#This script is based on the specific Taverne-workflow and related Pure-keyword classifications of Pure at the VU Amsterdam

#Run this script after you have updated:

    #1) Taverne-status person records in Pure (opt-out / implied)
    #2) Open Access-status (UNL-keywords) for Gold OA of the publication set in Pure

#What the script does is:

#get all person records from Pure and select IDs, affiliations, YouShare-status, earliest start dt, latest end dt

#get all publicaties that meet YouShare-criteria - published in a specific period - created after a specific date

#loop through publications and determine:

#1) if it has at least one internal author and internal organisation affiliation

#2) Open Access-classification Pure (VSNU-keyword)

#3) YouShare-status Pure (Taverne keyword)

#4) per author:
    #a) if (earliest) publication year not before earliest appointment year
    #b) if author is YouShare candidate
    
#5) determine if publication is eligible for Taverne:

    #a)publication has internal author(s) and internal affiliation(s)
    #b)publication is not Gold OA (UNL-cat A or B)
    #c)none of the authors has opted out
    #d)at least one of the authors is 'implied' under Taverne opt-out and was employed at the VU at the time of publication
    
#6) create csv-file for bulk-edit keywords in Pure (select by columns 'youshare eligible')
