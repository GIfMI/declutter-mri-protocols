#!/usr/bin/env python
import functools
import dictdiffer
import pandas as pd
from collections import OrderedDict

class ProtocolTree:
    def __init__(self,tree,scanner):
        self.tree = tree
        self.scanner = scanner 
      
    def toTOC(self):
        #if self.TOC_dict is None:
        self.TOC_dict = dict()
        
        for region in self.tree.iter("region"):
            for exam in region.iter("NormalExam_dot_engine"):
                for program in exam.iter("program"):
                    steps = program.getchildren()
                    for step in range(len(steps)):
                        sequence = dict()
                        sequence['Region'] = region.attrib['name']
                        sequence['Exam'] = exam.attrib['name']
                        sequence['Program'] = program.attrib['name']
                        sequence['Step'] = steps[step].attrib['name']
                        sequence['Id'] = steps[step].attrib['Id']
                        self.TOC_dict[sequence['Id']] = sequence                                     
        print(self.TOC_dict)
        return self.TOC_dict

    def toprogram(tree):
        return()
    def toregion(tree):
        return()
    def toexam(tree):
        return()

    def toparamlist(self):
        self.param_list=[]
        for card in self.tree.iter("Card"):
            card_name=card.attrib['name']
            for param in card.iter("ProtParameter"):
                param_name="%s-%s" %(card_name,param[0].text)
                self.param_list.append(param_name)
        self.param_set = sorted(self.param_list)
        return self.param_list, self.param_set
    
    def toprotocols(self):
        self.protocols=[]
        self.protocols_dict={}
        for node in self.tree.iter("Protocol"):
            protocol={}
            protocol['id']=node.attrib['Id']
            protocol['headertitle']=node[0].text
            protocol['HeaderProtPath']=node[1][0][0].text
            #print(protocol['HeaderProtPath'])
            protocol_split=protocol['HeaderProtPath'].split("\\")
            protocol['Program']=protocol_split[-2]
            protocol['Exam']=protocol_split[-3]
            protocol['Region']=protocol_split[-4]
            sequence=node[1][0][0].text
            # print()
            # print(sequence)
            path_list=sequence.split("\\")
            # print(path_list)

            protocol['Sequencename']=path_list[-1].lower() #convert to lower case
            protocol['HeaderProperty']=node[1][0][1].text
            TAend = protocol['HeaderProperty'].find('PM')-1
            protocol['AcqTime'] = protocol['HeaderProperty'][4:TAend]
            if protocol['AcqTime'].find('s')<1:
                seconds = functools.reduce(lambda x, y: x*60+y, [int(i) for i in (protocol['AcqTime'].replace(':',',')).split(',')])
                protocol['AcqTimeSeconds']=seconds
            else:
                protocol['AcqTimeSeconds'] = protocol['AcqTime'][0:-2]
            
            voxStart = protocol['HeaderProperty'].find('Voxel')
            voxEnd = protocol['HeaderProperty'].find('mm')-1
            protocol['voxSize'] = protocol['HeaderProperty'][voxStart:voxEnd]
            protocol['voxSize'][12:len(protocol['voxSize'])]
            seqStart = protocol['HeaderProperty'].rfind(':')+2
            seqEnd = len(protocol['HeaderProperty'])-1
            protocol['seqType']=protocol['HeaderProperty'][seqStart:seqEnd]
            params=OrderedDict.fromkeys(self.param_set,"")
            
            for card in node.iter("Card"):
                card_id=card.attrib['ID']
                card_name=card.attrib['name']
                # print ("%s %s %s" % (protocol_id,card_id,card_name))
                for param in card.iter("ProtParameter"):
                    param_name="%s-%s" %(card_name,param[0].text)
                    param_value=param[1].text
                    params[param_name]=param_value
            protocol['parameters']=params
            self.protocols.append(protocol)
            self.protocols_dict[protocol['id']]=protocol
        return self.protocols_dict, self.protocols
    
    def todf(self,lowercase=1):
        self.df = []
        self.df = pd.DataFrame.from_dict(self.TOC_dict).T
        if lowercase == 1:
            self.df = self.df.apply(lambda x: x.str.lower() if x.dtype == "object" else x)
        
        