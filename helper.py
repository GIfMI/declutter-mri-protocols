#!/usr/bin/env python

#helper.py
'''helper functions for compare sequences'''
import xlsxwriter
import pandas as pd
import re
import dictdiffer
import os


#global bold, cell_format_blue, cell_format_green, cell_format_red, cell_format_right

# def format_workbook(workbook):
    
#     cell_format = workbook.add_format()
#     bold = cell_format.set_bold()
#     cell_format_blue = cell_format.set_font_color('blue')
#     cell_format_red = cell_format.set_font_color('red')
#     cell_format_green = cell_format.set_font_color('green')
#     cell_format_right = cell_format.set_align('right')

#     return bold, cell_format_blue, cell_format_red, cell_format_green, cell_format_right

def get_protocols_in_region(tree, region): 
    TOCdf = pd.DataFrame.from_dict(tree.TOC_dict).T
    program_set = set(TOCdf.Program.unique())
    region_set = set(TOCdf.Region.unique())
    exam_set = set(TOCdf.Exam.unique())
    sequence_list=[]
    for protocol in tree.protocols:
        sequence_list.append(protocol['Sequencename'])
        sequence_set=set(sequence_list)

    for exam in exam_set:
        exams_in_region = list(filter(lambda d: d['Exam'] in exam, tree.protocols))
        
    list_of_protocols = []
    for exam in range(len(exams_in_region)):
        list_of_protocols.append(exams_in_region[exam]['id'])
    protocols_which_contain_sequence_dict = {}
    protocols_in_region_dict = {}
    protocols_no_duplicate_dict = {}

    for exam in exam_set:
        for program in program_set:
            for sequence in sequence_set:
                list_of_protocols=[]
                for protocol in tree.protocols:
                    #if protocol['Sequencename'].casefold() == sequence.casefold() and protocol['Region'] == region and protocol['Exam'] == exam and protocol['Program'] == program:
                    if protocol['Sequencename'].casefold() == sequence.casefold() and protocol['Region'] == region:
                        list_of_protocols.append(protocol['id'])
                if len(list_of_protocols)>1:
                    protocols_which_contain_sequence_dict[sequence]=list_of_protocols
                    protocols_in_region_dict[sequence] = list_of_protocols
                elif len(list_of_protocols)==1: 
                    #print("No duplicates of sequence %s: %s found." %(list_of_protocols, sequence))
                    protocols_no_duplicate_dict[sequence] = list_of_protocols
                    protocols_in_region_dict[sequence] = list_of_protocols

    return protocols_in_region_dict, protocols_which_contain_sequence_dict

def write_region_to_workbook(region, workbook, cell_format=None):
    #bold, cell_format_blue, cell_format_red, cell_format_green, cell_format_right = format_workbook(workbook)
    bold = workbook.add_format({'bold': True})
    if workbook.get_worksheet_by_name(region[0:30]) == None:
        base_worksheet = workbook.add_worksheet(region[0:30])
        row = 0
    else:
        base_worksheet = workbook.get_worksheet_by_name(region[0:30])
        row = base_worksheet.dim_rowmax+1
            
            #base_worksheet = workbook.add_worksheet(clean_region)
    if row == 0:
        base_worksheet.set_column(0,3,25)
        base_worksheet.set_column(4,5,60) 
        #bold = cell_format.set_bold()
                # base_worksheet.write(0,0,'PROTOCOL LIST',bold);row+=1
                # base_worksheet.write(row,0,'All protocols for this region are listed here.');row+=1
                # base_worksheet.write(row,0,'Only protocols with duplicates are written to a worksheet.');row+=2
                #base_worksheet.write(row,0,'Duplicate sequences are listed below!',cell_format_red);row+=1
        base_worksheet.write(row,0,'Sequence',bold)
        base_worksheet.write(row,1,'Region',bold)
        base_worksheet.write(row,2,'Exam',bold)
        base_worksheet.write(row,3,'Program',bold)
        base_worksheet.write(row,4,'Info',bold)
        base_worksheet.write(row,5,'Location',bold)
        row+=2
    
    return workbook, base_worksheet, row

def compare_tree(master_tree, region, workbook, logfile2, **compare_tree):
    red = workbook.add_format({'font_color': 'red'})
    blue = workbook.add_format({'font_color': 'blue'})
    green = workbook.add_format({'font_color': 'green'})
    bold = workbook.add_format({'bold': True})
    right = workbook.add_format({'align': 'right'})
    # bold = cell_format.set_bold()
    # cell_format_blue = cell_format.set_font_color('blue')
    #cell_format_red = cell_format.set_font_color('red')
    # cell_format_green = cell_format.set_font_color('green')
    # cell_format_right = cell_format.set_align('right')
    #bold, cell_format_blue, cell_format_red, cell_format_green, cell_format_right = format_workbook(workbook)
    #create worksheet
    if workbook.get_worksheet_by_name('Duplicates') == None:
        duplicate_worksheet = workbook.add_worksheet('Duplicates')
        duplicate_worksheet.set_column(0,0,25)
        duplicate_row = 0
    else: 
        duplicate_worksheet = workbook.get_worksheet_by_name('Duplicates')
        duplicate_row = duplicate_worksheet.dim_rowmax+1
        
    TOCdf = pd.DataFrame.from_dict(master_tree.TOC_dict).T
    protocols_in_region_dict, protocols_which_contain_sequence_dict = get_protocols_in_region(master_tree, region)

    for k,v in protocols_which_contain_sequence_dict.items(): #v contains sequence ids
        current_sequence=k
        if '*' in current_sequence:
            current_sequence = current_sequence.replace('*','')
        
        duplicate_worksheet.write(duplicate_row,1,len(v),red)
        logfile2.write("Sequence: '%s' appears in %s protocols\n" % (k,len(v)))
        #clean up sequence names
        
        print(current_sequence)
        clean_current_sequence = re.sub(r'[^a-zA-Z0-9\._-]', '', current_sequence) 
        clean_current_sequence = clean_current_sequence.lower()
        duplicate_worksheet.write(duplicate_row,0,clean_current_sequence)
        # url = "\"internal:'%s'!A1\"" %current_sequence
        # base_worksheet.write_url(base_row,0,url)
        #open worksheet per sequence to compare
        if workbook.get_worksheet_by_name(clean_current_sequence[0:30]) == None:
            worksheet = workbook.add_worksheet(clean_current_sequence[0:30])
            row = 0
        else:
            worksheet = workbook.get_worksheet_by_name(clean_current_sequence[0:30])
            row = worksheet.dim_rowmax+1
            
        worksheet.set_column(0,0,38)
        worksheet.set_column(1,2,25)
        
        #gather master protocol and current protocol (k) data
        current_protocol_list=v
        master_param_protocol_id=current_protocol_list[0]
        master_param_dict=master_tree.protocols_dict[master_param_protocol_id]["parameters"]
        master_headerprotpath=master_tree.protocols_dict[master_param_protocol_id]['HeaderProtPath']
        master_headerproperty = master_tree.protocols_dict[master_param_protocol_id]['HeaderProperty']
        TAend = master_headerproperty.find('PM')-1
        master_aqcTime = master_headerproperty[0:TAend]
        voxStart = master_headerproperty.find('Voxel')
        voxEnd = master_headerproperty.find('mm')-1
        master_voxSize = master_headerproperty[voxStart:voxEnd]

        out_str="\tMaster sequence to be found in %s at %s" % (master_param_protocol_id,master_headerprotpath)
        logfile2.write(out_str + "\n\n")
#        row = 0
        col = 0
        for i in range (1,len(current_protocol_list)):
            compare_protocol_id=current_protocol_list[i]
            compare_param_dict=master_tree.protocols_dict[compare_protocol_id]["parameters"]
            compare_headerprotpath=master_tree.protocols_dict[compare_protocol_id]['HeaderProtPath']
            compare_headerproperty = master_tree.protocols_dict[compare_protocol_id]['HeaderProperty']
            TAend = compare_headerproperty.find('PM')-1
            compare_aqcTime = compare_headerproperty[0:TAend]
            voxStart = compare_headerproperty.find('Voxel')
            voxEnd = compare_headerproperty.find('mm')-1
            compare_voxSize = compare_headerproperty[voxStart:voxEnd]
            out_str="\tComparing %s at %s, %s %s \n\twith %s at %s, %s %s" % (master_param_protocol_id,master_headerprotpath,\
                                                                              master_aqcTime,master_voxSize,compare_protocol_id,\
                                                                              compare_headerprotpath,compare_aqcTime,compare_voxSize)
            logfile2.write(out_str + "\n")
            row+=2
            worksheet.write_string(row,0,'Comparing',bold)
            worksheet.write_string(row,1,str(master_param_protocol_id));row += 1
            master_str = "%s, %s %s" %(master_headerprotpath,master_aqcTime,master_voxSize)
            worksheet.write_string(row,0,master_str,blue);row += 1
            worksheet.write_string(row,0,'with',bold)
            worksheet.write_string(row,1,str(compare_protocol_id));row+=1
            compare_str = "%s, %s %s" %(compare_headerprotpath,compare_aqcTime,compare_voxSize)
            worksheet.write_string(row,0,compare_str,red);row += 2
            difflist=list(dictdiffer.diff(master_param_dict,compare_param_dict))
            if difflist:
                duplicate_worksheet.write_string(duplicate_row,2,"Differences found!",red)
                worksheet.write_string(row,0,'Parameter to change',bold)
                worksheet.write_string(row,1,'From',bold)
                worksheet.write_string(row,2,'To',bold);row+=1
                for diff in difflist:
                    # if 'AutoAlign' in diff[1]:
                    #     None
                    # elif 'Adjust' in diff[1]:
                    #     None
                    # else:
                        logfile2.write("\t\t%s\t%sfrom %s to %s\n" % (diff[0],str(diff[1]).ljust(55),str(diff[2][1]).ljust(30),str(diff[2][0]).ljust(30)))                     
                        worksheet.write_string(row,0,str(diff[1]))
                        diff21 = diff[2][1].strip()
                        if diff21.isnumeric() == True:
                            worksheet.write_number(row,1,int(diff21),right) 
                        else:    
                            worksheet.write_string(row,1,diff[2][1].strip(),right)
                        diff20 = diff[2][0].strip()
                        if diff20.isnumeric() == True:
                            worksheet.write_number(row,2,int(diff20),right);row+=1 
                        else:    
                            worksheet.write_string(row,2,diff[2][0].strip(),right);row+=1
            else:
                worksheet.write_string(row,0,"No differences",green);row+=1
                duplicate_worksheet.write_string(duplicate_row,2,"No differences",green)
                logfile2.write("\t\tNo changes\n")
            logfile2.write("\n")
        duplicate_row+=1
        logfile2.write("------------------------------------------------------------------------------------------------------------------------------\n")
    workbook.close()
    
def compareTwoTOCs(m_TOCdf, c_TOCdf, opath):
    # use the Id column as index
    c_TOCdf.set_index('Id', inplace = True)
    m_TOCdf.set_index('Id', inplace = True)
    #concatenate based on Id index
    TOC_combined = pd.concat([m_TOCdf,c_TOCdf], axis=1)
    TOC_excel = os.path.join(opath,'TOC_combined.xlsx')
    with pd.ExcelWriter(TOC_excel,mode='A') as writer:
        TOC_combined.to_excel(writer,sheet_name='TOC_combined')

    #get programs
    

#def compareSets(master_set, compare_set, level):
def compareSets(m_TOCdf, c_TOCdf, level, opath):
    TOC_excel2 = os.path.join(opath,'TOC_combined2.xlsx')
    i = 0
    if level == 'program':
        master_set = set(m_TOCdf.Program.unique())
        compare_set = set(c_TOCdf.Program.unique())
        set_on_both = master_set.intersection(compare_set)
    if level == 'region':
        master_set = set(m_TOCdf.Region.unique())
        compare_set = set(c_TOCdf.Region.unique())
        set_on_both = master_set.intersection(compare_set)
    if level == 'exam':
        master_set = set(m_TOCdf.Exam.unique())
        compare_set = set(c_TOCdf.Exam.unique())
        set_on_both = master_set.intersection(compare_set)

    for item in set_on_both:
        if level == 'program':
            master_subset = m_TOCdf.query('Program ==@ item')
            compare_subset = c_TOCdf.query('Program ==@ item')
        if level == 'region':
            master_subset = m_TOCdf.query('Region ==@ item')
            compare_subset = c_TOCdf.query('Region ==@ item')
        if level == 'exam':
            master_subset = m_TOCdf.query('Exam ==@ item')
            compare_subset = c_TOCdf.query('Exam ==@ item')

        set_intersection = master_subset.merge(compare_subset, how = 'inner',indicator = True, on = ["Region", "Exam", "Program", "Step"])
        set_not_in_compare = master_subset.merge(compare_subset,how = 'outer',indicator=True, on = ["Region", "Exam", "Program", "Step"]).loc[lambda x : x['_merge']=='left_only']
        set_not_in_master = master_subset.merge(compare_subset,how = 'outer',indicator=True, on = ["Region", "Exam", "Program", "Step"]).loc[lambda x : x['_merge']=='right_only']

        #%%
        total_sets = pd.concat([set_intersection,set_not_in_compare,set_not_in_master],axis=0)

        if i==0:
            with pd.ExcelWriter(TOC_excel2, mode="a" ,engine="openpyxl") as writer:
            # fix line
                writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
                total_sets.to_excel(writer,sheet_name=level)
                i=1
        else:
            with pd.ExcelWriter(TOC_excel2, engine='openpyxl', mode='a') as writer:
                # fix line
                writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
                total_sets.to_excel(writer,sheet_name=level)
                writer.close()

    return total_sets
# %%
