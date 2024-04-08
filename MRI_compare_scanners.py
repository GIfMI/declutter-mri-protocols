#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 14:02:25 2019

@author: pimpullens, pieterdevolder, nathansennesael
"""

import dictdiffer
import sys
import os
import time
import re
import xlsxwriter
import argparse
from pandas import DataFrame
import pandas as pd
import protocoltree as pt
import helper

from enum import unique
from lxml import etree
from xmldiff import main, formatting
from collections import OrderedDict
from argparse import RawTextHelpFormatter

#get xmlfiles
parser = argparse.ArgumentParser(description='Find differences in Regions, Exams and Programs. Use with Siemens xml protocol print.\n\n (c) 2019 Pim Pullens, PhD and Pieter Devolder\n dept. of Radiology, UZ Gent, Gent, Belgium\n pim.pullens@uzgent.be',formatter_class=RawTextHelpFormatter)
parser.add_argument('outdir', type=str, help='Output dir for xlsx files')
parser.add_argument('m_file', type=str, help='Master xml file')
parser.add_argument('c_file', nargs='+', type=str, help='Compare xml files')
#parser.add_argument('c_xmlfile2', type=str, help='Compare xml file 2')


# args in launch.json
args = parser.parse_args()
m_xmlfile = [os.path.join(os.getcwd(), args.m_file)]
c_files = [os.path.join(os.getcwd(), c_file) for c_file in args.c_file]

c_xmlfiles = set()
for c_file in c_files:
    c_xmlfiles.add(c_file)

opath=args.outdir

# get all info from master_tree

m_tree=etree.parse(str(m_xmlfile[0]))
m_root = m_tree.getroot()
m_header = m_root.findall(".//PrintTOC/TOC/HeaderTitle")
m_scanner = m_header[0].text
m_scanner = m_scanner.strip()
m_scanner = re.sub(r' ','_',m_scanner)
m_scanner = re.sub(r'/','_',m_scanner)

#get master tree
m_tree = pt.ProtocolTree(m_tree,m_scanner)
#create tree.TOC_dict
m_tree.toTOC()
#create tree.prog
m_tree.toprogram()
#create tree.param_list and tree.param_set
m_tree.toparamlist()
#create tree.protocol_dict and tree.protocols
m_tree.toprotocols()
#write TOC to df
m_tree.todf(lowercase=1) #creates mtree.df
m_TOCdf = m_tree.df

timestr = time.strftime("%Y%m%d-%H%M%S")
toc_name =  "TOC_%s_%s.xlsx" %(m_scanner,timestr) 
toc_xls= os.path.join(opath, toc_name) 
m_TOCdf.to_excel(toc_xls)
print(m_TOCdf)

#loop over compare files and find differences with master file
for c_xmlfile in c_xmlfiles:
    
    c_tree=etree.parse(c_xmlfile)
    c_root = c_tree.getroot()
    c_header = c_root.findall(".//PrintTOC/TOC/HeaderTitle")
    c_scanner = c_header[0].text
    c_scanner = c_scanner.strip()
    c_scanner = re.sub(r' ','_',c_scanner)
    c_tree = pt.ProtocolTree(c_tree,m_scanner)
    #create tree.TOC_dict
    c_tree.toTOC()
    #create tree.prog
    c_tree.toprogram()
    #create tree.param_list and tree.param_set
    c_tree.toparamlist()
    #create tree.protocol_dict and tree.protocols
    c_tree.toprotocols()
    c_tree.todf(lowercase=1)
    c_TOCdf = c_tree.df
    level = 'exam'
    total_sets = helper.compareSets(m_TOCdf, c_TOCdf, level, opath)
    
xlsxname='TOC_total_sets_%s.xlsx' %(level)
total_sets.to_excel(os.path.join(opath,xlsxname))


# old stuff 13/4/23================
# convert dictionary to pandas dataframe and transpose
df_compare = pd.DataFrame.from_dict(c_tree.TOC_dict).T
df_master = pd.DataFrame.from_dict(m_tree.TOC_dict).T

# use the Id column as index
df_compare.set_index('Id', inplace = True)
df_master.set_index('Id', inplace = True)
#concatenate based on Id index
TOC_combined = pd.concat([df_master,df_compare], axis=1)
TOC_combined.to_excel(os.path.join(opath,'TOC_combined.xlsx'))

program_sets = helper.compareSets(m_TOCdf,c_TOCdf,'program',opath)
program_sets.to_excel(os.path.join(opath,'TOC_combined3.xlsx'))
# 6 april hier klopt iets niet
#================

#get sets of programs, regions and exams
m_program_set = set(df_master.Program.unique())
m_region_set = set(df_master.Region.unique())
m_exam_set = set(df_master.Exam.unique())

c_program_set = set(df_compare.Program.unique())
c_region_set = set(df_compare.Region.unique())
c_exam_set = set(df_compare.Exam.unique())

xlsxname='differences_%s_and_%s.xlsx' %(m_scanner,c_scanner)
workbook = xlsxwriter.Workbook(os.path.join(opath,xlsxname))
bold = workbook.add_format({'bold': True})
region_diff_m_not_c = m_region_set.difference(c_region_set)
region_diff_m_not_c=sorted(region_diff_m_not_c,key=str.lower)
region_diff_c_not_m = c_region_set.difference(m_region_set)
region_diff_c_not_m=sorted(region_diff_c_not_m,key=str.lower)
region_inter_m_c = m_region_set.intersection(c_region_set)
region_inter_m_c=sorted(region_inter_m_c,key=str.lower)
row = 0
worksheet = workbook.add_worksheet('Region')
worksheet.autofilter(0,0,3,0)
worksheet.set_column(0,2,30)
ostr = 'In %s not in %s' %(m_scanner,c_scanner)
worksheet.write(row,1,ostr,bold)
ostr = 'In %s not in %s' %(m_scanner,c_scanner)
worksheet.write(row,0   ,ostr,bold)
ostr = 'In %s and in %s' %(m_scanner,c_scanner)
worksheet.write(row,2,ostr,bold)

row+=1
for d in region_diff_c_not_m:
    worksheet.write(row,0,d)
    row+=1
row=1
for d in region_diff_m_not_c:
    worksheet.write(row,1,d)
    row+=1
row=1
for d in region_inter_m_c:
    worksheet.write(row,2,d)
    row+=1

row=0
exam_diff_m_not_c = m_exam_set.difference(c_exam_set)
exam_diff_m_not_c=sorted(exam_diff_m_not_c,key=str.lower)
exam_diff_c_not_m = c_exam_set.difference(m_exam_set)
exam_diff_c_not_m=sorted(exam_diff_c_not_m,key=str.lower)
exam_inter_m_c = m_exam_set.intersection(c_exam_set)
exam_inter_m_c=sorted(exam_inter_m_c,key=str.lower)

worksheet = workbook.add_worksheet('Exam')
worksheet.autofilter(0,0,3,0)
worksheet.set_column(0,2,30)
ostr = 'In %s not in %s' %(m_scanner,c_scanner)
worksheet.write(row,1,ostr,bold)
ostr = 'In %s not in %s' %(c_scanner,m_scanner)
worksheet.write(row,0,ostr,bold)
ostr = 'In %s and in %s' %(m_scanner,c_scanner)
worksheet.write(row,2,ostr,bold)
row+=1
for d in exam_diff_c_not_m:
    worksheet.write(row,0,d)
    row+=1
row=1
for d in exam_diff_m_not_c:
    worksheet.write(row,1,d)
    row+=1
row=1
for d in exam_inter_m_c:
    worksheet.write(row,2,d)
    row+=1

row=0
program_diff_m_not_c = m_program_set.difference(c_program_set)
program_diff_m_not_c=sorted(program_diff_m_not_c,key=str.lower)
program_diff_c_not_m = c_program_set.difference(m_program_set)
program_diff_c_not_m=sorted(program_diff_c_not_m,key=str.lower)
program_inter_m_c = m_program_set.intersection(c_program_set)
program_inter_m_c=sorted(program_inter_m_c,key=str.lower)

worksheet = workbook.add_worksheet('Program')
worksheet.autofilter(0,0,3,0)
worksheet.set_column(0,2,30)
ostr = 'In %s not in %s' %(m_scanner,c_scanner)
worksheet.write(row,1,ostr,bold)
ostr = 'In %s not in %s' %(c_scanner,m_scanner)
worksheet.write(row,0,ostr,bold)
ostr = 'In %s and in %s' %(m_scanner,c_scanner)
worksheet.write(row,2,ostr,bold)
row+=1
for d in program_diff_c_not_m:
    worksheet.write(row,0,d)
    row+=1
row=1
for d in program_diff_m_not_c:
    worksheet.write(row,1,d)
    row+=1
row=1
for d in program_inter_m_c:
    worksheet.write(row,2,d)
    row+=1
workbook.close()

difflist = list(dictdiffer.diff(m_tree.protocols_dict,c_tree.protocols_dict))
f = open('diff.txt','w+')
for diff in difflist:
    f.write("\t\t%s\t%sfrom %s to %s\n" % (diff[0],str(diff[1]).ljust(55),str(diff[2][1]).ljust(30),str(diff[2][0]).ljust(30)))
    
f.close()

print("Done!")

def dataframe_difference(df1: DataFrame, df2: DataFrame) -> DataFrame:
    """
    Find rows which are different between two DataFrames.
    :param df1: first dataframe.
    :param df2: second dataframe.
    :return:    if there is different between both dataframes.
    """
    comparison_df = df1.merge(df2, indicator=True, how='outer')
    diff_df = comparison_df[comparison_df['_merge'] != 'both']
    return diff_df
