import re
import os

global delist
def delist(x):
    y = x[0]
    return y

class Gaussian_computation:
    def __init__(self, file, parameters, label, number):
        self.file = file
        self.parameters = parameters
        self.label = label
        self.index = number
        self.energies = dict()
    
    def add_energy(self, energy_type, energy_value):
        self.energies.update({energy_type : energy_value})
        
class Gaussian_file:
    def __init__(self, script, file_name):
        self.name = file_name
        self.script = script
        self.computations = []
        self.path = self.script.script_path + "/" + self.name
        print("Importing " + self.name + "...")
    
    def iterate_through(self):
        print("Iterating file " + self.name + "...")
        reg_line1 = re.compile("^\s\*+")
        reg_line2 = re.compile("^\s\-+")
        reg_line3 = re.compile("^\s\#")
        reg_parameters = re.compile("\s[\w()]+/[\w\d*+-]+")
        
        def look_for_energy(self, line):
            def streamer(x,y,z):
                if x[z].search(y) != None:
                    return delist(x[z].findall(y))
                    
            def energy_to_number(text):
                reg_numpart = re.compile("=\s*-?[\d.DE+-]+")
                reg_number = re.compile("-?[\d.E+-]+")

                numpart = delist(reg_numpart.findall(text))
                numpart = numpart.replace("D","E")
                num = delist(reg_number.findall(numpart))
                num = float(num.replace("=",""))

                return num

            regd = self.script.regdict
            a = list((n,energy_to_number(m)) for n,m in map(lambda z: (z,streamer(regd, line, z)), regd.keys()) if m)
            if a:
                return a[0]

        cnt = 0
        ki = False
        ki1 = 0
        ki2 = 0
        nl = 0
        logcnt = -1
        label_cnt = False
        acnt = False
        parameters = ""

        with open(self.path, "r") as file:   
            for line in file:
                if ki == True and cnt == ki1+3:
                    if reg_line1.search(line) != None:
                        acnt = True
                    else:
                        ki = False
                        acnt = False
                if ki == True and acnt == True:
                    if reg_line2.search(line) != None:
                        ki = False
                if ki == False and acnt == True:
                    if reg_line3.search(line) != None:
                        label_cnt = True
                        parameters = delist(reg_parameters.findall(line)).replace(" ","",1)
                        acnt = False

                if label_cnt==True:
                    if reg_line2.search(line) != None:
                        nl += 1
                        ki2 = cnt
                    if cnt==ki2+1 and nl==2:
                        computation_label = line.replace(" ","",1)
                        computation_label = computation_label.replace("\n","")
                        label_cnt = False
                        nl = 0
                        logcnt+=1
                        self.computations.append(Gaussian_computation(self,parameters,computation_label,logcnt))

                if reg_line1.search(line) != None and acnt == False:
                    ki1 = cnt
                    ki = True
                cnt+=1
                
                
                if look_for_energy(self,line):
                    label, val = look_for_energy(self,line)
                    self.computations[logcnt].add_energy(label,val)
                    label = ""
                    val = 0
    
    def add_computation(computation):
        self.computations.append(computation)
        
class Script:
    def __init__(self):
        self.script_path = os.path.dirname(os.path.abspath(__file__))
        reg_directory = re.compile("\w+$")
        directory = reg_directory.findall(self.script_path)
        self.get_files()
        
        self.script_directory = delist(directory)
        self.script_filename = os.path.basename(__file__)
        
        files = []
        
        self.script_name = "script"
        self.arguments = []
        self.gaussian_files = []
        self.parse_name()
        
        self.regdict = dict()
        self.regdict_from_list()
        
    
    def add_file(self,file):
        self.files.append(file)
        
    def get_files(self,extension="log"):
        from os import listdir
        reg_extension = re.compile("\."+extension+"$")
        self.files = [f for f in listdir(self.script_path) if reg_extension.search(f) != None]
        
    def parse_name(self):
        text = self.script_filename
        reg_split = re.compile("[_.]")
        args = reg_split.split(text)
        args.pop(-1)
        self.script_name = args.pop(0)
        self.arguments = args
    
    global collider
    def collider(key):
        library_energy = {
            "HF":["HF","H-F"],
            "EUMP2":["EUMP2","MP2"],
            "EUMP3":["EUMP3","MP3"],
            "UMP4(SDQ)":["UMP4(SDQ)","MP4","MP4SDQ"],
            " E(CORR)":["E(CORR)","ECORR","EKOR","KOR"],
            "CCSD(T)":["CCSD(T)","CCSDT"],
            "CCSD":["CCSD"],
            }
        
        library_output_formats = {
            "txt":["TXT"],
            "csv":["CSV"],
            "xlsx":["XLSX","XLX"]
            }

        try:
            for i in library_energy.keys():
                if key in library_energy[i]:
                    return ("E",i)
                
            for j in library_output_formats.keys():
                if key in library_output_formats[j]:
                    return ("O",j)
        except:
            pass
        
    def regdict_from_list(self):
        for d in self.arguments:
            typ, value = collider(d.upper())
            if typ == "E":
                if value=="HF":
                    self.regdict.update({value : re.compile("^\sSCF\sDone:\s+E\(\w+\)\s*=\s*[-\d.DE+-]+")})
                elif value:
                    self.regdict.update({value : re.compile("\s" + value.replace("(","\(").replace(")","\)") +
                                                            "\s*=\s*[-\d.DE+-]+")})
            elif typ == "O":
                self.output_format = value
            
            
    def import_gaussian_files(self):
        for i in self.files:
            self.gaussian_files.append(Gaussian_file(self,i))
            
    def iterate_gaussian_files(self):
        if self.gaussian_files:
            for gfile in self.gaussian_files:
                gfile.iterate_through()
        else:
            raise Exception("No Gaussian_files class objects included. Import them first.")
            
            
    def write_output_file(self):
        from datetime import datetime
        
        time = datetime.now()
        output_path = str(self.script_path + "/" + self.script_name + 
                          time.strftime("_%d-%m-%y_%H-%M") + "." + self.output_format)
        
        def write_txt(self):
            print("Writing .txt file ...")

            with open(output_path, 'w', newline='') as txtfile:
                def wrt(s):
                    txtfile.write(s + "\n")
                    
                wrt("Evaluated directory:\t" + self.script_path)
                wrt("File generation time:\t" + time.strftime("%H:%M:%S %d-%m-%Y"))
                wrt("")
                tab = "\t"
                
                for gauss_file in self.gaussian_files:
                    wrt(gauss_file.name)
                    
                    for gauss_comp in gauss_file.computations:
                        wrt(tab + str(gauss_comp.index) + tab + gauss_comp.parameters + tab*2 + gauss_comp.label)
                        
                        for label, value in gauss_comp.energies.items():
                            wrt(tab*3 + label + tab + str(value))
              
        def write_csv(self):
            #print("Writing .csv") 
            print("Not implemented yet :-(") 
                
        def write_xlsx(self):
            print("Writing .xlsx file ...")
            
            try:
                import xlsxwriter
            except ImportError:
                import subprocess
                import sys
                def install_pckg(package):
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                install_pckg(xlsxwriter)
            
            with xlsxwriter.Workbook(output_path) as excel_file:
                worksh = excel_file.add_worksheet()
                
                global row
                row = 0
                global col
                col = 0
                
                def wrt(tx, *args):
                    global row
                    global col
                    worksh.write(row, col, tx, *args)
                    
                bold = excel_file.add_format({'bold': True})
                numeric_4dec = excel_file.add_format({'num_format': '#.###0'})
                
                wrt("Evaluated directory:")
                col+=1
                wrt(self.script_path)
                row+=1
                col=0
                wrt("File generation time:")
                col+=1
                wrt(time.strftime("%H:%M:%S %d-%m-%Y"))
                col=0
                row+=2
                col+=4
                
                for label in list(self.regdict.keys()):
                    wrt(label, bold)
                    col+=1
                    
                col=0
                row+=1
                
                length_file = 17
                length_parameters = 12
                length_label = 12
                
                def greater(a,b):
                    if a<b:
                        return b
                    else:
                        return a
                
                for gauss_file in self.gaussian_files:
                    wrt(gauss_file.name, bold)
                    length_file = greater(length_file, len(gauss_file.name))
                    col+=1
                    
                    for gauss_comp in gauss_file.computations:
                        wrt(gauss_comp.index)
                        col+=1
                        wrt(gauss_comp.parameters)
                        length_parameters = greater(length_parameters, len(gauss_comp.parameters))
                        col+=1
                        wrt(gauss_comp.label)
                        length_label = greater(length_label, len(gauss_comp.label))
                        col+=1
                        
                        for key in self.regdict.keys():
                            value = gauss_comp.energies[key]
                            wrt(value, numeric_4dec)
                            col+=1
                            
                        col=1
                        row+=1
                    col=0
                    row+=1
                    
                worksh.set_column(0, 0, length_file)
                worksh.set_column(1, 1, 4)
                worksh.set_column(2, 2, length_parameters)
                worksh.set_column(3, 3, length_label)
                worksh.set_column(4, 4+len(self.regdict.keys()), 12)
                
        switch = {"txt":write_txt, "csv":write_csv, "xlsx":write_xlsx}
        switch[self.output_format](self)
        
        
        
#output = Script()
#output.import_gaussian_files()
#output.iterate_gaussian_files()
#output.write_output_file()
