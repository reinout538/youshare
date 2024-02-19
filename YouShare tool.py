#get all person records from Pure and select IDs, affiliations, YouShare-status, earliest start dt, latest end dt
#get all publicaties that meet YouShare-criteria - published in a specific period
#loop through publications and determine:
#1) if it has at least one internal author and internal organisation affiliation
#2) Open Access-classification Pure (VSNU-keyword)
#3) YouShare-status Pure (Taverne keyword)
#4) per author:
    #a) if (earliest) publication year not before earliest appointment year
    #b) if author is YouShare candidate
#5) determine if publication is eligible for YouShare
#6) create csv-file for bulk-edit keywords in Pure

import os, sys
import requests
import json
import csv
import xlrd
import math
import datetime
from IPython.display import clear_output

api_pure_pub = 'https://research.vu.nl/ws/api/524/research-outputs/'
api_pure_persons = 'https://research.vu.nl/ws/api/524/persons'
key_pure = input('enter pure api-key with admin rights: ')

from_date = "2023-01-01"
to_date = "2023-12-31"
created_after = "1900-10-01"
youshare_candidates = []
gold_oa_statuses = ["/dk/atira/pure/keywords/oa/a_open_article_in_open_journal","/dk/atira/pure/keywords/oa/b_open_article_in_toll_access_journal"]
youshare_types = ["/dk/atira/pure/researchoutput/researchoutputtypes/contributiontojournal/article", "/dk/atira/pure/researchoutput/researchoutputtypes/contributiontojournal/letter", "/dk/atira/pure/researchoutput/researchoutputtypes/contributiontojournal/book", "/dk/atira/pure/researchoutput/researchoutputtypes/contributiontojournal/editorial", "/dk/atira/pure/researchoutput/researchoutputtypes/contributiontojournal/systematicreview", "/dk/atira/pure/researchoutput/researchoutputtypes/contributiontojournal/shortsurvey", "/dk/atira/pure/researchoutput/researchoutputtypes/contributiontobookanthology/chapter", "/dk/atira/pure/researchoutput/researchoutputtypes/contributiontobookanthology/entry", "/dk/atira/pure/researchoutput/researchoutputtypes/contributiontobookanthology/conference", "/dk/atira/pure/researchoutput/researchoutputtypes/memorandum"]

#file_dir = 'G:/UBVU/Pure/py_tools/youshare/'
file_dir = sys.path[0]


def get_pure_persons():

    #get person affiliations and IDs from Pure
    global int_person_list
    global int_person_dict
    global pure_scopus_ids
    global scopus_id2affil
    int_person_list = []
    int_person_dict = {}
    pure_scopus_ids = []
    scopus_id2affil = {}
    
    size = 100
    offset = 0

    #get count
    response = requests.get(api_pure_persons, headers={'Accept': 'application/json'},params={'size': size, 'offset':offset, 'apiKey':key_pure})   
    #print (response.json())
    no_records = (response.json()['count'])
    cycles = (math.ceil(no_records/size))
    print(f"{no_records} persons found")
    
    #get person records
    for request in range (cycles)[0:]:
        response = requests.get(api_pure_persons+'?', headers={'Accept': 'application/json'},params={'size': size, 'offset':offset, 'apiKey':key_pure})
        offset += size
        print ('get person records from Pure:',request+1, 'of', cycles, 'x',size,'records')
        clear_output('wait')        

        #loop through items in response
        for count,item in enumerate(response.json()['items'][0:]):  
            count_scopus=1
            
            youshare_candidate = youshare_opt_out = "false"
            person_scopus_ids = []
            person_affil_list = []
            affil_first_dt = datetime.datetime(9999, 12, 31)
            affil_last_dt = datetime.datetime(1900, 1, 1)
            
            #get affiliations
            for affil in item['staffOrganisationAssociations']:
                    affil_start_dt = datetime.datetime.strptime(affil['period']['startDate'][:10], '%Y-%m-%d')
                    if 'endDate' in affil['period']:
                        affil_end_dt = datetime.datetime.strptime(affil['period']['endDate'][:10], '%Y-%m-%d')
                    else: affil_end_dt = datetime.datetime(9999, 12, 31)
                    if 'jobTitle' in affil:
                        job_title = affil['jobTitle']['uri'][affil['jobTitle']['uri'].rfind("/")+1:]
                    else: job_title = ''
                    if 'emails' in affil:
                        email = affil['emails'][0]['value']['value']
                    else: email = ''
                    person_affil_list.append({'af_id':affil['pureId'],'af_org_id':affil['organisationalUnit']['uuid'],'af_source_id':affil['organisationalUnit']['externalId'], 'af_start':affil_start_dt,'af_end':affil_end_dt, 'job_title':job_title,'e_mail':email})
                    #get affil range
                    if affil_start_dt < affil_first_dt:
                        affil_first_dt = affil_start_dt
                    if affil_end_dt > affil_last_dt:
                        affil_last_dt = affil_end_dt

            #get scopus-IDs
            if 'ids' in item:
                for count, extid in enumerate (item['ids']):
                    if item['ids'][count]['type']['term']['text'][0]['value'] == 'Scopus Author ID':
                        person_scopus_ids.append(item['ids'][count]['value']['value'])
                        pure_scopus_ids.append(item['ids'][count]['value']['value'])
                        #create index scopus-ID + affiliation_list
                        scopus_id2affil[item['ids'][count]['value']['value']] = person_affil_list
                        count_scopus += 1    
            
            #get youshare status
            if 'keywordGroups' in item:
                for keyword_group in item['keywordGroups']:
                    
                    if keyword_group['logicalName'] == "/dk/atira/pure/keywords/You_Share_Participant":
                        
                        for keyword in keyword_group['keywordContainers']:
                            
                            if keyword['structuredKeyword']['uri'] == "/dk/atira/pure/keywords/You_Share_Participant/you_share_opt_out":
                                youshare_opt_out = "true"
                            else:
                                youshare_candidate = "true"
                            
                    
            #int_person_list.append({'person_uuid':item['uuid'],'youshare':youshare_candidate,'scopus_ids':person_scopus_ids,'personaffiliations':person_affil_list, 'affil_first_dt': affil_first_dt, 'affil_last_dt': affil_last_dt})      
            int_person_dict[item['uuid']] = {'person_uuid':item['uuid'],'youshare_candidate':youshare_candidate, 'youshare_opt_out':youshare_opt_out,'scopus_ids':person_scopus_ids,'personaffiliations':person_affil_list, 'affil_first_dt': affil_first_dt, 'affil_last_dt': affil_last_dt}
                   
    return (int_person_dict)

"""
def get_youshare_candidates():
    
    data = {"employmentStatus":"ACTIVE","keywordUris":["/dk/atira/pure/keywords/You_Share_Participant/you_share_participant"]}
    response = requests.post(api_pure_persons, json=data, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, params={'apiKey':key_pure})
           
    json_record = response.json()
    count = json_record['count']
    print (f"getting {count} persons") 
    #print(json.dumps(json_record,indent=3))
    
    data = {"offset":0,"size":count,"employmentStatus":"ACTIVE","fields":["uuid"],"keywordUris":["/dk/atira/pure/keywords/You_Share_Participant/you_share_participant"]}
    response = requests.post(api_pure_persons, json=data, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, params={'apiKey':key_pure})
    json_record = response.json()
     
    for n, person in enumerate(json_record["items"]):
        youshare_candidates.append(person["uuid"])
"""

def get_pubs():
    
    offset = 0
    size = 100
    
    with open(os.path.join(file_dir,"log.csv"), 'w', newline='', encoding='utf-8') as file_log:
        write_log = csv.writer(file_log, delimiter=',', escapechar=' ', quoting=csv.QUOTE_ALL, lineterminator='\r\n')
        write_log.writerow(["uuid", "pureId", "publ type", "publ category", "peer-rev", "publ status", "publ year", "publ date", "current pub status", "current pub dt", "doi", "link", "filename", "pre-vu", "internal_affil", "oa-status", "youshare_author", "youshare_author_opt_out", "youshare eligible", "youshare status pure", "youshare_keyw_(new)"])
        
        #get count
        data = {"workflowSteps" : ["forApproval", "approved", "forRevalidation"],"typeUris":youshare_types,"publicationStatuses": ["/dk/atira/pure/researchoutput/status/published", "/dk/atira/pure/researchoutput/status/epub"],"publicationCategories":["/dk/atira/pure/researchoutput/category/academic"],"publishedAfterDate":from_date, "publishedBeforeDate":to_date, "createdAfter": created_after}
        response = requests.post(api_pure_pub, json=data, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, params={'apiKey':key_pure})
        json_record = response.json()
        count = json_record['count']
        cycles = (math.ceil(count/size))
        
        #get publ records
        for request in range (cycles)[0:]:
            
            data = {"offset":offset,"size":size,"workflowSteps" : ["forApproval", "approved"],"typeUris":youshare_types,"publicationStatuses": ["/dk/atira/pure/researchoutput/status/published", "/dk/atira/pure/researchoutput/status/epub"],"publicationCategories":["/dk/atira/pure/researchoutput/category/academic"],"publishedAfterDate":from_date, "publishedBeforeDate":to_date, "createdAfter": created_after}
            
            offset += size       
            response = requests.post(api_pure_pub, json=data, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, params={'apiKey':key_pure})
            
            json_record = response.json()
            
            clear_output('wait')
            print (f"getting {request+1} of {cycles} x {size} publications")
            #print(json.dumps(json_record,indent=3))    
            
            for pub in json_record["items"]:
                
                #parameters
                internal_affil = 'false'
                internal_person = 'false'
                pre_vu = 'true'
                youshare_author = 'false'
                youshare_author_opt_out = 'false'
                youshare = 'false'
                oa_status = None
                youshare_status = None
                                            
                #get publication statuses and dates                
                pub_year = 9999
                for pub_status in pub["publicationStatuses"]:
                    #get earliest publ year with status and date
                    if pub_status["publicationDate"]["year"] < pub_year:
                        pub_year = pub_status["publicationDate"]["year"]
                        pub_stat = pub_status["publicationStatus"]["uri"]
                        pub_dt = pub_status["publicationDate"]
                    #get current publication status
                    if pub_status["current"] == True:
                        pub_stat_curr = pub_status["publicationStatus"]["uri"]
                        pub_dt_curr = pub_status["publicationDate"]
                    else:
                        pub_stat_curr = None
                        pub_dt_curr = None
                
                #evaluate persons and affiliations
                for person_assoc in pub["personAssociations"]:
                    if "person" in person_assoc:
                        internal_person = 'true'
                        
                        #check if pub year before start affiliation
                        if int_person_dict[person_assoc["person"]["uuid"]]["affil_first_dt"].year <= int(pub_year):
                            pre_vu = 'false'
                        #check author youshare status
                        if int_person_dict[person_assoc["person"]["uuid"]]["youshare_candidate"] == 'true':
                            youshare_author = 'true'
                        if int_person_dict[person_assoc["person"]["uuid"]]["youshare_opt_out"] == 'true':
                            youshare_author_opt_out = 'true'
                                                               
                        #check for internal org
                        if "organisationalUnits" in person_assoc:                           
                            internal_affil = 'true'
                        
                #get OA-status and YouShare-status
                if "keywordGroups" in pub:
                    
                    for keyword_group in pub["keywordGroups"]:
                        if keyword_group["logicalName"] == '/dk/atira/pure/keywords/oa':
                            oa_status = keyword_group["keywordContainers"][0]['structuredKeyword']['uri']
                        if keyword_group["logicalName"] == '/dk/atira/pure/keywords/taverne':
                            youshare_status = keyword_group["keywordContainers"][0]['structuredKeyword']['uri']

                #get electr versions
                doi = link = file = ""
                if "electronicVersions" in pub:
                    for electr_version in pub["electronicVersions"]:
                        if "doi" in electr_version:
                            doi = electr_version.get("doi")
                        if "link" in electr_version:
                            link = electr_version.get("link")
                        if "file" in electr_version:
                            file = electr_version["file"].get("fileName")
                        else: pass
                
                #determine keyw
                if youshare_status != None:
                    youshare_keyw = None
                elif pre_vu == 'true' or internal_affil == 'false' or internal_person == 'false':
                    youshare_keyw = 'excl_non_vu'
                elif oa_status in gold_oa_statuses:
                    youshare_keyw = 'excl_oa'
                elif youshare_author_opt_out == 'true':
                    youshare_keyw = 'excl_auth_opt_out'
                elif youshare_author == 'false':
                    youshare_keyw = 'excl_no_opt_in'
                else:
                    youshare_keyw = 'unknown'
                    
                #determine YouShare status
                if youshare_author == 'true' and youshare_author_opt_out == 'false' and pre_vu == 'false' and internal_affil == 'true' and internal_person == 'true' and oa_status not in gold_oa_statuses and youshare_status == None:
                    youshare = 'true'
                else:
                    youshare = 'false'
                
                try:
                    write_log.writerow([pub["uuid"], pub["pureId"],pub["type"]["uri"],pub["category"]["uri"], pub["peerReview"], pub_stat, pub_year, pub_dt, pub_stat_curr, pub_dt_curr, doi, link, file, pre_vu, internal_affil, oa_status, youshare_author, youshare_author_opt_out,youshare, youshare_status, youshare_keyw])
                except:
                    print (pub["uuid"])
                

#main                
get_pure_persons()
get_pubs()

#get_youshare_candidates()
    
with open(os.path.join(file_dir,"person_log.csv"), 'w', newline='') as person_log:
        write_p_log = csv.writer(person_log, delimiter=',', escapechar=' ', quoting=csv.QUOTE_ALL, lineterminator='\r\n')
        write_p_log.writerow(['person_uuid','youshare_candidate', 'youshare_opt_out','scopus_ids','personaffiliations', 'affil_first_dt', 'affil_last_dt'])

        for person in int_person_dict:
            write_p_log.writerow([int_person_dict[person]['person_uuid'], int_person_dict[person]['youshare_candidate'], int_person_dict[person]['youshare_opt_out'], int_person_dict[person]['scopus_ids'], int_person_dict[person]['personaffiliations'], int_person_dict[person]['affil_first_dt'], int_person_dict[person]['affil_last_dt']])
            
