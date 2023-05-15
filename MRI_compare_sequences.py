#!/usr/bin/env python

from lxml import etree
from xmldiff import main, formatting
from collections import OrderedDict

import dictdiffer
import sys
import os
import re
import xlsxwriter
import argparse
import functools
import time
import pandas as pd
import protocoltree as pt
import helper

from argparse import RawTextHelpFormatter

#get xmlfile
parser = argparse.ArgumentParser(description='Find differences between MRI sequences with the same name. Use with Siemens xml protocol print.\n\n (c) 2019 Pim Pullens, PhD and Pieter Devolder\n dept. of Radiology, UZ Gent, Gent, Belgium\n pim.pullens@uzgent.be',formatter_class=RawTextHelpFormatter)
parser.add_argument('xmlfile', type=str, help='Input xml file')
parser.add_argument('outdir', type=str, help='Output dir for xlsx files')

args = parser.parse_args()
tree=etree.parse(args.xmlfile)

opath = args.outdir
wdir = os.getcwd()
    
#get header
root = tree.getroot()
header = root.findall(".//PrintTOC/TOC/HeaderTitle")
scanner = header[0].text
scanner = scanner.strip()
scanner = re.sub(r' ','_',scanner)

#define master tree
m_tree = pt.ProtocolTree(tree,scanner)

#create tree.TOC_dict
m_tree.toTOC()
#create tree.prog
m_tree.toprogram()
#create tree.param_list and tree.param_set
m_tree.toparamlist()
#create tree.protocol_dict and tree.protocols
m_tree.toprotocols()

#write TOC to df
TOCdf = pd.DataFrame.from_dict(m_tree.TOC_dict).T
timestr = time.strftime("%Y%m%d-%H%M%S")
toc_name =  "TOC_%s_%s.xlsx" %(scanner,timestr) 
toc_xls= os.path.join(opath, toc_name) 
TOCdf.to_excel(toc_xls)
print(TOCdf)

#write all protocols to file
oname = "output_%s_%s.csv" %(scanner,timestr)
f=open(os.path.join(opath,oname),"w+")
headerbase="id|HeaderProtPath|HeaderProperty|Region|Exam|Program|Sequence"
#Region|Exam|Program
headerparamline="|".join(m_tree.param_set)
headerline= ("%s|%s" %(headerbase,headerparamline))
f.write(headerline + "\r\n")

sequence_list=[]
for protocol in m_tree.protocols:
    line="%s|%s|%s|%s|%s|%s|%s" %(protocol['id'],protocol['HeaderProtPath'],protocol['HeaderProperty'],protocol['Region'],protocol['Exam'],protocol['Program'],protocol['Sequencename'])
    sequence_list.append(protocol['Sequencename'])
    paramline="|".join('%s' % (v)for k,v in protocol['parameters'].items())
    outputline= "%s|%s" %(line,paramline)
    f.write(outputline + "\r\n")
f.close()
#end write to file

sequence_set=set(sequence_list)

#build region, exam, program list

# use the Id column as index
TOCdf.set_index('Id', inplace = True)

program_set = set(TOCdf.Program.unique())
region_set = set(TOCdf.Region.unique())
exam_set = set(TOCdf.Exam.unique())

for region in region_set:
    #open file for writing
    clean_region = re.sub(r'[^a-zA-Z0-9\._-]', '', region)
    fname = "Differences_%s_%s_%s.txt" %(scanner,clean_region,timestr)
    logfile2=open(os.path.join(opath,fname),"w+")
    xlsxname = "Differences_%s_%s_%s.xlsx" %(scanner,clean_region,timestr) 
    oxls= os.path.join(opath, xlsxname) 
    if os.path.isfile(oxls):
        os.remove(oxls)
    
    workbook = xlsxwriter.Workbook(oxls)
    workbook, base_worksheet, row = helper.write_region_to_workbook(region, workbook, None)
    protocols_in_region_dict, protocols_which_contain_sequence_dict = helper.get_protocols_in_region(m_tree, region)     
    base_row = row+1

    #the main function
    helper.compare_tree(m_tree, region, workbook, logfile2)
    logfile2.close()
#workbook.close()
print("Done!")
