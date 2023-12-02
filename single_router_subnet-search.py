import time
import os
import sys
import re
import numpy as np

### File search function
def find_files(filename, search_path):
   result = []
# Waking top-down from the root
   for root, dir, files in os.walk(search_path):
      if filename in files:
         result.append(os.path.join(root, filename))
   return result

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

### IPV4 pattern ####
IPV4pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}')
route_instance_pattern = re.compile(r'.*inet.\d{1}')
ignore_show_line1 = re.compile("show")
ignore_show_line2 = re.compile("SHOW")
arr_route_info = []

router_hostname =[
    'cr1.mgmt.klwn1',
    'cr1.mgmt.kmlp8',
    'cr1.mgmt.pgrg1',
    'cr1.mgmt.srry1',
    'cr1.mgmt.vctr3',
    'cr1.mgmt.vncv1',
    'cr2.mgmt.vncv1'
]

print (router_hostname[0])
y = input()
##initialization
indx = -1

with open(os.path.join(sys.path[0],"show_route/show-route-output-cr2.mgmt.vncv1.txt"),'r') as txtlines:
    lines = txtlines.readlines()
    header_csv = "Index;Route_Instance;Subnet;Destination_Interface\n"
    filename_csv ="csv_output/csv_route_cr2.vncv1.csv"
    
    with open(filename_csv,'w') as f_csv:
        f_csv.write(header_csv)

    for line in lines:
        line=line.strip()
        ##searching line with show in the text
        ignore_pattern1 = re.search(ignore_show_line1,line)
        ignore_pattern2 = re.search(ignore_show_line2,line)
        ##
        if ignore_pattern1 or ignore_pattern2:
            #print(line)
            #print("This will pass")
            #y = input()
            continue    #go to the next line to examine

        ## Examine the line and look for routing instance

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

        if line.find('via')!=-1: #look for string with "via" it indicates it has exit interface
            check_int = (line.split("via",1)[1])  #get the exit interface
            for x in range(len(cr2_vncv1_p2pinterface)): #loop to examine the liner and check if check_int content is p2p interface
                analyze_int = re.search(cr2_vncv1_p2pinterface[x]+".\w+",check_int.strip())                 
                    
                    ##### debugging ####
                    #print(line)
                    #print("checking int: "+cr2_vncv1_p2pinterface[x])
                    #print("Values of analyze_int "+str(analyze_int))
                    #y = input()
                    #print("The value of this is : " + str(analyze_int))
                    
                if str(analyze_int) != "None" : #if analyze_int has value it means it is a p2pinterface
                    p2pinterface = "True" #set p2pinterface to TRUE to identify 
                    break
            ##index starts -1, if the procedure reached here means the lines evaluated with rows required
            indx = indx + 1

            ### check the interface; if the value is true then the subnet originates in this router
            if p2pinterface != "True":
                #print("Subnet " +ipadd+ " is seen in " +check_int.strip())
                dest_interface = check_int.strip()
                #print("%d\t%s\t%s\t\t%s" %(indx,route_instance,ipadd,dest_interface))
            ### means the subnet originates to other location
            else:
                dest_interface = "Adjacent Router"
            
            print("%d\t%s\t\t%s\t\t%s" %(indx,route_instance,ipadd,dest_interface))
            search_output_csv = str(indx)+";"+route_instance+";"+ipadd+";"+dest_interface+"\n"
            with open(filename_csv,'a') as f_csv:
                f_csv.write(search_output_csv)
           #y=input()
       
            p2pinterface = "False" # clear value of p2pinterface after check
    print("File has been saved")

                    





                
            
                          
            
            
            
            
            
            
            
            
            
            
            
            
            
            #if IPV4pattern.findall(line) != []:
            #    ipadd = IPV4pattern.findall(line)
                
            #if line.find('via')!=-1: #look for string with VIA
            #    check_int = (line.split("via",1)[1])
            #    for x in range(len(cr2_vncv1_p2pinterface)):
            #        analyze_int = re.findall(cr2_vncv1_p2pinterface[x],check_int)
            #        print(analyze_int)



        #print(ipadd)
        #print (check_int)
            


