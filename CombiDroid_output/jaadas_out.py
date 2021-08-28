import os
import csv
import logging
import sys
import json
import glob
import pathlib
import subprocess
import traceback
import re

if __name__ == '__main__':
    
    output_file_total = pathlib.Path(r'/../jaadas_kotlin.csv')
    
    
    total_array = []
    total_head = ['name','md5hash','score','vuln_kind_0','vuln_kind_1','vuln_kind_2','vuln_kind_3']
    
    rules_cat = {}
    
    directory = r'/../CombiDroid-parallel/Tools/jaadas/output'
    path = directory + "/*"
    loop = 0
    filelist = glob.glob(path)
    total_row = []
    for apk_path in sorted(filelist):
        name = os.path.splitext(os.path.basename(os.path.normpath(apk_path)))[0]
        print(name)
        
        loop += 1
        if loop >= 0:
            if name != 'stdout':
                output_list = glob.glob(apk_path + "/*.txt")
            
                for filename in output_list:
                    filename = pathlib.Path(filename)
                    print(filename)
                    vuln_kind_0 = 0
                    vuln_kind_1 = 0
                    vuln_kind_2 = 0
                    vuln_kind_3 = 0

                    data = None
                    with filename.open('r') as f:
                        try:
                            data = json.load(f)
                        except Exception as e:
                            logging.error(traceback.format_exc())
                            data = None
                            #continue
                            
                    if not data:
                        print("There was an error in Super with number: ")
                        continue
                        
                    for x in rules_cat:
                        rules_cat[x] = 0
                        
                    score = data['score']
                    md5 = data['md5hash']
                    for results in data.get('results'):
                        description = results.get('desc')
                        vuln_kind = results.get('vulnKind')

                        if vuln_kind == 0:
                            vuln_kind_0 += 1
                        elif vuln_kind == 1:
                            vuln_kind_1 += 1
                        elif vuln_kind == 2:
                            vuln_kind_2 += 1
                        elif vuln_kind == 3:
                            vuln_kind_3 += 1
                        #print(description)
                        
                        
                        if 'FragmentInjection exist!' in description:
                            description = 'FragmentInjection'
                            
                        if description not in rules_cat:
                            rules_cat[description] = 1
                        else:
                            rules_cat[description] += 1
                        
                    total = []
                    total.extend([name,md5,score,vuln_kind_0,vuln_kind_1,vuln_kind_2,vuln_kind_3])
                    total.extend(list(rules_cat.values()))
                total_row.append(total)
                
    total_head.extend(list(rules_cat))
    
    total_array.append(total_head)
    
    total_array.extend(total_row)
    
    print(total_array)
    
    with open(output_file_total, "a", newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        try:
            writer.writerows(total_array)
        except Exception as e:
            logging.error(traceback.format_exc())
            print("There was an error with writing to the aggregated csv file")
            