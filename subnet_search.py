import time
import os
import sys
import re
import numpy as np

### File search function
def find_files(filename, search_path):
# Waking top-down from the root
   for root, dir, files in os.walk(search_path):
      if filename in files:
         result = os.path.join(root, filename)
   return result

def func_analyze_int(check_int,cr_p2pinterface):
    p2pinterface = "False"
    for x in range(len(cr_p2pinterface)): #loop to examine the liner and check if check_int content is p2p interface
        analyze_int = re.search(cr_p2pinterface[x]+".\w+",check_int)               
                        
        ##### debugging ####
        #print(line)
        #print("checking int: "+cr2_vncv1_p2pinterface[x])
        #print("Values of analyze_int "+str(analyze_int))
        #y = input()
        #print("The value of this is : " + str(analyze_int))
                        
        if str(analyze_int) != "None" : #if analyze_int has value it means it is a p2pinterface
            p2pinterface = "True" #set p2pinterface to TRUE to identify 
            break
    
    return p2pinterface

##### INTERIOR #####

#### CR1.KLWN1 P2P Interfaces
#et-3/2/0 ## to cr1.kmlp8 port et-1/1/1
#ae0 ## to cr1.srry1 port et-5/1/5
#xe-5/3/0 to cr1.srry1 port xe-0/2/0
cr1_klwn1_p2pinterface = ['et-3/2/0','ae0','xe-5/3/0']

#### CR1.KMLP8 P2P Interfaces
#et-1/1/1 to cr1.klwn1 et-3/2/0
#et-1/1/0 to cr1.vncv1 ae7, cr.srry1 ae10
#ae9 to cr1.vncv1 ae9
cr1_kmlp8_p2pinterface = ['et-1/1/1','et-1/1/0','ae9']

#### CR1.PGRG1 P2P Interfaces
#xe-5/0/0 to cr2.vncv1 xe-1/0/5
#xe-4/1/0 to cr1.srry1 

cr1_pgrg1_p2pinterface = ['xe-5/0/0','xe-4/1/0']



##### MAINLAND #####

#### CR1.SRRY1 P2P Interfaces
#ae10 to cr1.kmlp8 et-1/1/0, cr1.pgrg1 ae10, cr1.vctr3 ae10
#ae1 to cr2.vncv1 
#ae8 to cr1.vncv1
#et-5/1/5 to cr1.klwn1
#xe-5/0/0:1 to cr1.klwn1
cr1_srry1_p2pinterface = ['ae10','ae1','ae8','et-5/1/5','xe-5/0/0:1']

#### CR1.VNCV1 P2P interfaces
#ae2 to cr2.vncv1 ae2
#ae6 to cr1.vctr3 ae5
#ae7 to cr1.vctr3 ae3 , cr1.kmlp8 et-1/1/0
#ae8 to cr1.srry1 ae8
#ae9 to cr1.kmlp8 ae9
cr1_vncv1_p2pinterface = ['ae2','ae6','ae7','ae8','ae9']

#### CR2.VNCV1 P2P interfaces
#xe-5/1/0:0 to cr1.pgrg1 xe-5/0/0
#ae2 to cr1.vncv1 ae2
#ae1 to cr1.srry1 ae1
cr2_vncv1_p2pinterface = ['xe-5/1/0:0','ae2','ae1']


##### ISLAND #####
#ae3 to cr1.srry1 ae10, cr1.vncv1 ae7
#ae5 to cr1.vncv1
cr1_vctr1_p2pinterface = ['ae3','ae5']


#variable for creating master file
masterfile_var=0 #0 means the master file has not yet created
masterfile_ind=0

asn_lookup = ""
aspath = ""

### IPV4 pattern ####
IPV4pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}')
route_instance_pattern = re.compile(r'.*inet.\d{1}')
asnpattern = re.compile(r"\d{1,6}")
aspathpattern = re.compile(r"\d+.* \d+")
asnpattern_self=re.compile("I")
asnpattern_multipath = re.compile(r"\d+.* \d+ [I?]")
asnpattern_singlepath = re.compile(r"\d{1,6} [I?]")
ignore_show_line1 = re.compile("show")
ignore_show_line2 = re.compile("SHOW")
arr_route_info = []
local_intpattern = re.compile(r"Local")
local_interface = "No"

router_hostname =[
    'cr1.mgmt.klwn1',
    'cr1.mgmt.kmlp8',
    'cr1.mgmt.pgrg1',
    'cr1.mgmt.srry1',
    'cr1.mgmt.vctr3',
    'cr1.mgmt.vncv1',
    'cr2.mgmt.vncv1'
]



for xx in range (len(router_hostname)):
    #print(router_hostname[xx])
    filelocation_show_route = find_files("show-route-output-"+router_hostname[xx]+".txt",os.path.join(sys.path[0],"show_route/"))
   
    #print(filelocation_show_route)
    #y = input()
 
    ##initialization
    

    with open(str(filelocation_show_route),'r') as txtlines:
        lines = txtlines.readlines()
        header_csv = "Index;Route_Instance;Supernet;Subnet;ASN;Destination_Interface;Router\n"
        filename_csv ="csv_output/"+router_hostname[xx]+"-show_route.csv"
        indx = -1

        with open(filename_csv,'w') as f_csv:
            f_csv.write(header_csv)

        for line in lines:
            line=line.strip()
            ##searching line with show in the text
            ignore_pattern1 = re.search(ignore_show_line1,line)
            ignore_pattern2 = re.search(ignore_show_line2,line)
        ##
            if ignore_pattern1 or ignore_pattern2:
                supernet_lookup = re.search(IPV4pattern,line)
                if supernet_lookup:
                    supernet_ip = supernet_lookup.group()
                #print(line)
                #print("This will pass")
                #y = input()
                continue    #go to the next line to examine

            ## Examine the line and look for routing instance
            #print(line)
            #y=input()
            if line.find('Local via')!=-1:
                local_interface = "Yes"
                #print(line)
                #y=input()
            #print(line)
            elif line.find('via lo')!=-1:
                local_interface = "Yes"
            if line.find('AS path:')!=-1:

                if re.search(asnpattern_multipath,line):
                    aspath = re.search(aspathpattern,line)
                    aspath = aspath.group()

                    asn_lookup = re.search(asnpattern_singlepath,line)
                    asn_lookup = asn_lookup.group()
                    asn_lookup = re.search(asnpattern,asn_lookup)
                    asn_lookup = asn_lookup.group()
                    #print(line)
                    #print(aspath)
                    #print(asn_lookup)
                    #y = input()
                    #print(line)
                    #print("mulliple")
                    #print(asn_lookup)
                    #y = input()  
                elif re.search(asnpattern_singlepath,line):
                    asn_lookup = re.search(asnpattern,line)
                    #asn_lookup = (line.split("AS path:",1)[1])
                  
                    if asn_lookup:
                        asn_lookup = asn_lookup.group()
                        #print(asn_lookup)
                        #y = input()
                    else:
                        asn_lookup = "271"
                    
                    aspath=asn_lookup
                    #print(line)
                    #print(aspath)
                    #print(asn_lookup)
                    #y = input()
                    
                    #print(line)
                    #print("single")
                    #print(asn_lookup)
                    #y = input()           
                elif re.search(asnpattern_self,line):
                    asn_lookup = "271"
                    aspath=asn_lookup
                else:
                    asn_lookup = "271"
                    aspath=asn_lookup                 
                #else:
                #elif re.search(asnpattern_multipath,line):
                #    print(line)
                #    #asn_lookup = re.search(asnpattern_multipath,line)
                #    multiple_asn = asnpattern.findall(line)
                #    print(multiple_asn)
                #    y = input()
                #    if asn_lookup:
                #        asn_lookup = asn_lookup.group()
                #        print(line)
                #        print(asn_lookup)
                #        y = input()
                #    else:
                #        asn_lookup = "271"
                #    aspath=asn_lookup
                #print("here you go")
                #print(asn_lookup)
                #y=input()
            
                if asn_lookup =="":
                    asn_lookup = "271"
                    aspath=asn_lookup
            
                if int(asn_lookup) > 65000 and int(asn_lookup) <66000 :
                    asn_lookup = "271"
                    aspath=asn_lookup
                #print(int(asn_lookup))

            

            route_instance_lookup = re.search(route_instance_pattern,line)   
            if route_instance_lookup:
                route_instance = route_instance_lookup.group()
            #print(route_instance)
            #y=input()      

            ## Examine the line if consist of subnet with slash notation       
            subnet_lookup = re.search(IPV4pattern,line) #scan if the liner is consist of subnet
            if subnet_lookup: #check if subnet_lookup has value
                ipadd = subnet_lookup.group() #store the subnet 
                #print("Subnet lookup for: "+ipadd)

            #if indx == 182:
            #    print(line)
            #    y=input()
            if line.find('via')!=-1: #look for string with "via" it indicates it has exit interface
                check_int = (line.split("via",1)[1])  #get the exit interface
                check_int = check_int.strip()
                if router_hostname[xx]=='cr1.mgmt.klwn1':
                    p2pinterface = func_analyze_int(check_int,cr1_klwn1_p2pinterface)
                elif router_hostname[xx]=='cr1.mgmt.kmlp8':
                    p2pinterface = func_analyze_int(check_int,cr1_kmlp8_p2pinterface)
                elif router_hostname[xx]=='cr1.mgmt.pgrg1':
                    p2pinterface = func_analyze_int(check_int,cr1_pgrg1_p2pinterface)
                elif router_hostname[xx]=='cr1.mgmt.srry1':
                    p2pinterface = func_analyze_int(check_int,cr1_srry1_p2pinterface)
                elif router_hostname[xx]=='cr1.mgmt.vctr3':
                    p2pinterface = func_analyze_int(check_int,cr1_vctr1_p2pinterface)
                elif router_hostname[xx]=='cr1.mgmt.vncv1':
                    p2pinterface = func_analyze_int(check_int,cr1_vncv1_p2pinterface)
                elif router_hostname[xx]=='cr2.mgmt.vncv1':
                    p2pinterface = func_analyze_int(check_int,cr2_vncv1_p2pinterface)
            

                ##index starts -1, if the procedure reached here means the lines evaluated with rows required
                indx = indx + 1

                ### check the interface; if the value is true then the subnet originates in this router
                if p2pinterface != "True":
                    #print("Subnet " +ipadd+ " is seen in " +check_int.strip())
                    dest_interface = check_int
                ### means the subnet originates to other location
                    ##filename-master_csv="csv_output/master_file.csv"
                    masterfile_ind = masterfile_ind + 1
                    if asn_lookup=="":
                        asn_lookup = "271"
                        aspath ="271"
                    if masterfile_var == 0:
                        header_csv = "Index;Route_Instance;Supernet;Subnet;ASN;AS_Path;Destination_Interface;Local;Router\n"
                        with open("csv_output/master_file.csv",'w') as master_csv:
                            master_output_csv = str(masterfile_ind)+";"+route_instance+";"+supernet_ip+";"+ipadd+";"+asn_lookup+";"+aspath+";"+dest_interface+";"+local_interface+";"+router_hostname[xx]+"\n"         
                            master_csv.write(header_csv)
                            master_csv.write(master_output_csv)                            
                    else:
                        with open("csv_output/master_file.csv",'a') as master_csv:
                            master_output_csv = str(masterfile_ind)+";"+route_instance+";"+supernet_ip+";"+ipadd+";"+asn_lookup+";"+aspath+";"+dest_interface+";"+local_interface+";"+router_hostname[xx]+"\n"         
                            master_csv.write(master_output_csv)                            
                    masterfile_var = masterfile_var + 1
                    


                else:
                    dest_interface = "Adjacent Router"
                #print("%d\t%s\t%s\t\t%s\t%s" %(indx,route_instance,ipadd,dest_interface,router_hostname[xx]))
                #y=input()
                #if indx == 183:
                #print("%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %(indx,route_instance,supernet_ip,ipadd,asn_lookup,aspath,ipadd,dest_interface))
                #y=input()
                search_output_csv = str(indx)+";"+route_instance+";"+supernet_ip+";"+ipadd+";"+asn_lookup+";"+dest_interface+";"+local_interface+";"+router_hostname[xx]+"\n"
                with open(filename_csv,'a') as f_csv:
                    f_csv.write(search_output_csv)
                #y=input()
                local_interface = "No"
                asn_lookup="" #clear value   
                aspath=""     
                p2pinterface = "False" # clear value of p2pinterface after check
        print("CSV File has been saved. Source: "+router_hostname[xx])
