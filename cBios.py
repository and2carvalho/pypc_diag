import os
import sys
import datetime
import psutil
import uuid
import win32print
import json
import pandas as pd
import numpy as np
# busca programas pelo registro do windows
import errno, os, winreg

def default(o):
    '''
Força conversao de numpy.int para int possibilitando 
que o numero seja JSON serializable
                                    '''
    if isinstance(o, np.int64): return int(o)  
    raise TypeError

class mydict(dict):
    '''
Classe para gerar json com dupla aspas("") utilizando
a função anterior como serializador
                                    '''
    def __str__(self):
        return json.dumps(self,default=default) 

class Clt_bios(): 
    '''
                               GUIA DE USO
: ocor = Clt_bios()

forma de chamar o atributo relacionados a processos e programas
- retorna programas instalados : ocor.instalados()
    - que causam lentidão: ocor.excluir()
    - que sao webbrowsers: ocor.clt_naveg()
    - que sao de determinada empresa: ocor.clt_progEmp()
- retorna processos: ocor.ds_processos()
    - por memoria: ocor.proc_sumaMemo(ocor.ds_processos)
    - por cpu: ocor.proc_sumaCpu(ocor.ds_processos)
- retorna dicionario: ocor.dic_modelo().values()
- gera arquivo texto: ocor.relatorio_txt(ocor.modelo)
obs. depende dos resultados do teste de ping e conexão
                                                    '''
    def __init__(self):

        # define status da memoria
        def status_memo(self):
            if self.memo_disp <= self.memo_total*0.10:
                status = '[status_critico]\nMenos de 10% de memória disponivel'
            elif self.memo_disp <= self.memo_total*0.20:
                status = '[status_baixa]\nMenos de 20% de memória disponivel'
            else:
                status = '[status_ok]\nMais de 20% de memória disponivel'
            return status

        self.id_maq = str(uuid.UUID(int=uuid.getnode())) # serial da placa mae
        self.nome_processador = self.get_cpu_type()
        self.qtd_processador = int(psutil.cpu_count())
        self.memo_total = float(psutil.virtual_memory()[0] / 1024 /1024)
        self.memo_disp = float(psutil.virtual_memory()[1] / 1024 /1024)
        self.status_memo = status_memo(self)
        self.nome_maq = str(os.environ['USERDOMAIN'])
        self.data_ocor = datetime.datetime.now(tz=None).strftime('%Y-%m-%d %H:%M:%S')
        self.ds_pdisk = self.busca_hd()
        self.ds_processos = self.busca_processos()
        self.instalados = self.prog_instalados()
        self.excluir = self.prog_lentidao(self.instalados)
        self.clt_naveg = self.prog_naveg(self.instalados)
        self.clt_progEmp = self.prog_emp(self.instalados)
        self.printers = self.impressoras()
        self.teste_ping = None
        self.teste_net = None
        self.info_usuario = None
        self.modelo = self.dic_modelo()
           
    # busca o nome do processador
    def get_cpu_type(self):
        from win32com.client import GetObject
        root_winmgmts = GetObject(r"winmgmts:root\cimv2")
        cpus = root_winmgmts.ExecQuery("Select * from Win32_Processor")
        return cpus[0].Name

    # busca por diferentes hd na máquina
    def busca_hd(self):
        nome_disk = []
        
        for i in range(len(psutil.disk_partitions())):
        # confere se é unidade disco (hd) eliminando opcoes como 'cdrom'
           if psutil.disk_partitions()[i][3] == 'rw,fixed':
                particao = str(psutil.disk_partitions()[i][1])
                tam = psutil.disk_usage(particao)[0] / 1024
                livre = psutil.disk_usage(particao)[2] / 1024
                nome_disk.append([particao,tam,livre])
        return nome_disk

    def busca_processos(self):
        ds_processos =[]
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['name','pid','username'])
        # converte valor de uso de memoria para Kb
                pinfo['proc_memo'] = proc.memory_info().vms / 1024
        # busca a percentagem de consumo de cada processo. Pode-se dividir pelo cpu_cout para que
        # processos atuando em mais de 1 core não acusem > 100% de consumo da máquina 
                pinfo['proc_cpu'] = proc.cpu_percent(interval=1) / psutil.cpu_count()
                ds_processos.append(pinfo)
            except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # transforma processos em Dataframe
        ds_processos = pd.DataFrame(ds_processos).rename(columns={'name':'proc_nome',
        'pid':'proc_pid','username':'proc_usuario'})

        return ds_processos

    def proc_sumaMemo(self,ds_processos):
        # agrupando diferentes processos e ordenando pelo uso de memória
        suma_processos = ds_processos.groupby(
        ds_processos['proc_nome'])['proc_memo','proc_cpu'].agg('sum').sort_values('proc_memo',
        ascending=False).reset_index()
        return suma_processos

    def proc_sumaCpu(self,ds_processos):
        # agrupando diferentes processos e ordenando pelo uso de cpu
        suma_processos2 = ds_processos.groupby(
        ds_processos['proc_nome'])['proc_memo','proc_cpu'].agg('sum').sort_values('proc_cpu',
        ascending=False).reset_index()
        return suma_processos2

    # relação de programas instalados
    def prog_instalados(self):
        ''' busca programas instalados juntos ao registro
        do windows. '''
        # armazena programas instalados.
        instalados = []

        proc_arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
        try:
            proc_arch64 = os.environ['PROCESSOR_ARCHITEW6432'].lower()
        except:
            pass

        if proc_arch == 'x86' or proc_arch == 'amd64':
            arch_keys = {winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY}
        elif proc_arch == 'x86' and not proc_arch64:
            arch_keys = {0}
        else:
            raise Exception("Unhandled arch: %s" % proc_arch)

        for arch_key in arch_keys:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_READ | arch_key)
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                skey_name = winreg.EnumKey(key, i)
                skey = winreg.OpenKey(key, skey_name)
                try:
                    instalados.append([winreg.QueryValueEx(skey, 'DisplayName')[0],
                                      winreg.QueryValueEx(skey, 'DisplayVersion')[0]])
                except OSError as e:
                    if e.errno == errno.ENOENT:
                        # DisplayName doesn't exist in this skey
                        pass
                finally:
                    skey.Close()
        return instalados

    # Busca programas que causam lentidão
    def prog_lentidao(self,instalados):
        # lista de programas que podem causar lentidão
        progs_exc = ['Steam','Origin','GOG Galaxy','Total Security','Avira','AVG',
                     'Avast','Kaspersky','Bitdefender','F-Secure','McAfee','ESET','G-Lock',
                     'Symantec','SpyHunter','Ad-Aware','Panda Antivirus','Norton AntiVirus',
                     'ESET NOD32','Microsoft Security Essentials','PW Clean','Comodo','NANO',
                     'Dr.Web','Baidu','ClamWin','Protector Plus','PC Tools','Mx One','Emco',
                     'ADinf32','F-Prot','PSafe','G DATA','Abacre','CS Anti-Virus','CMC Antivirus',
                     'Sophos','Forefront Client','IObit','RemoveIT','Multi Virus','Zillya',
                     'Rising','Naevius','Safety Scanner','RegRun','Trend Micro','eScan','Agnitum',
                     'Autorun Virus','VIPRE','Standalone System Sweeper','Moon Secure','NoVirus',
                     'Bittorrent','Utorrent','Team Viewer','Team Speaker','Adobe']

        excluir = []
        for i in range(len(instalados)):
            for n in range(len(progs_exc)):
                if str(progs_exc[n]) in str(instalados[i]):
                    excluir.append(instalados[i])
        return excluir

    # Busca navegadores
    def prog_naveg(self,instalados):
        # lista navegadores
        navegadores = ['Google Chrome','Mozilla Firefox',' Microsoft Edge',
                       'Opera','Apple Safari','Pale Moon']
        clt_naveg = []

        for i in range(len(instalados)):
            for n in range(len(navegadores)):
                if str(navegadores[n]) in str(instalados[i]):
                    clt_naveg.append(instalados[i])
        return clt_naveg

    # Busca programas de algum uso determinado
    def prog_emp(self,instalados):
        
        uso_id = ['Java','PostgreSQL','Adobe','Microsoft','Firebird']

        clt_progEmp = []

        for i in range(len(instalados)):
            for n in range(len(uso_id)):
                if str(uso_id[n]) in str(instalados[i]):
                    clt_progEmp.append(instalados[i])

        clt_progEmp = pd.DataFrame(clt_progEmp)
        if len(clt_progEmp)>0:
            clt_progEmp['status'] = 'Parado'
            clt_progEmp = clt_progEmp.rename(columns={0:'programa',1:'versao',2:'status'})
            # verifica se programas estão com serviço ativo
            for i in range(len(clt_progEmp)):
                self.validaExecucao(clt_progEmp.loc[i,'programa'])
            if True:
                clt_progEmp.loc[i,'status'] = 'Em Execução'
        # remove os aplicativos que checam update da lista
            try:
                clt_progEmp = clt_progEmp[~clt_progEmp['programa'].str.contains('Updater')]
            except: pass

        return clt_progEmp

    def impressoras(self):

        descart_print = ['Attributes','AveragePPM', 'DefaultPriority', 'Priority', 
        'StartTime','UntilTime', 'pComment', 'pDatatype', 'pDriverName', 'pLocation', 
        'pParameters','pPrintProcessor','pSecurityDescriptor','pSepFile','pDevMode']

        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTIONS+
                                           win32print.PRINTER_ENUM_LOCAL, None, 2)

        printers = pd.DataFrame(printers).drop(columns=descart_print)
        return printers

        #verifica se programas estão com serviço ativo
   
    # Verifica se determinado processo está em execução
    def validaExecucao(self, processName):
        '''
        Check if there is any running process that contains the given name processName.
        '''
        #Iterate over the all the running process
        for proc in self.ds_processos['proc_nome']:
            try:
                # Check if process name contains the given name string.
                if processName.lower() in proc:
                    return True
            except:
                pass
        return False

    # Compõe estrutura do objeto JSON
    def dic_modelo(self):
        proc_dic = []
        for i in range(len(self.ds_processos)):
            proc_dic.append({'proc_nome':self.ds_processos.loc[i]['proc_nome'],
            'proc_pid':self.ds_processos.loc[i]['proc_pid'],
            'proc_memo':float(self.ds_processos.loc[i]['proc_memo']),
            'proc_cpu':float(self.ds_processos.loc[i]['proc_cpu']),
            'proc_usuario':self.ds_processos.loc[i]['proc_usuario']
            })

        insta_dic = []
        for i in range(len(self.instalados)):
            insta_dic.append({'prog_nome':self.instalados[i][0],
            'prog_vers':self.instalados[i][1]})

        imp_dic = []
        for i in range(len(self.printers)):
            imp_dic.append({'imp_nome':self.printers.loc[i]['pPrinterName'],
            'imp_porta':self.printers.loc[i]['pPortName'],
            'imp_jobs':self.printers.loc[i]['cJobs'],
            'imp_status':self.printers.loc[i]['Status']
            })

        prog_dic = []
        for i in range(len(self.excluir)):
            prog_dic.append({'prog_nome':self.excluir[i][0],
            'prog_vers':self.excluir[i][1]
            })

        naveg_dic =[]
        try:
            for i in range(len(self.clt_naveg)):
                naveg_dic.append({'naveg_nome':self.clt_naveg[i][0],
			    'naveg_vers':self.clt_naveg[i][1]
			    })
        except:
            pass

        progId_dic =[]
        try:
            for i in range(len(self.clt_progEmp)):
                progId_dic.append({'progId_nome': self.clt_progEmp.programa.iloc[i],
                'progId_status' : self.clt_progEmp.status.iloc[i],
				'progId_vers': self.clt_progEmp.versao.iloc[i]
                })
        except: 
            pass

        hd_dic = []
        for i in range(len(self.ds_pdisk)):
            hd_dic.append({'hd_nome' : self.ds_pdisk[i][0],
                        'hd_tamanho' : self.ds_pdisk[i][1],
                        'hd_livre' : self.ds_pdisk[i][2]
                        })

        modelo = {"nome_maq" : self.nome_maq,
                "id_maq" : self.id_maq,
                "memo_total" : self.memo_total,
                "memo_disp" : self.memo_disp,
                "nome_processador":self.nome_processador,
                "qtd_processador" : self.qtd_processador,
                "disco_rigido" : hd_dic,
                "clt_naveg" : naveg_dic,
                "clt_progEmp" : progId_dic,
                "prog_lentidao" : prog_dic,
                "proc_maq": proc_dic,
                "insta_maq":insta_dic,
                "imp_inst": imp_dic,
                "teste_ping":[],
                "teste_net":[], 
                "data_ocor": self.data_ocor,
                "info_usuario": []
                } 
        return modelo

    def relatorio_txt(self,modelo,saida='cmd'):
        saida_default = sys.stdout
        if saida == 'cmd':
           sys.stdout = saida_default
        elif saida == 'txt': 
            sys.stdout = open('id_diag_'+self.data_ocor[:10].replace('/',
        '-')+'.txt','w',encoding='latin-1')

        print('#'*80)
        print('%50s'%('DIAGNOSTICO DA MÁQUINA'))
        print('#'*80,'\n\n')
        # processadores
        print('%52s' % ('ANÁLISE DE PROCESSADORES'))
        print(f'\n>>> Processamento: [{modelo["qtd_processador"]}] processadores'
        	f'\n*{modelo["nome_processador"]}\n\n{"-"*80}\n')  
        # analise de HD
        print('%51s' % ('ANÁLISE DE DISCO RÍGIDO'))
        for i in range(len(self.ds_pdisk)):
        	if (self.ds_pdisk[i][2] / self.ds_pdisk[i][1]) <= 0.10:
        		print(f'\n>>> Unidade de Disco: {self.ds_pdisk[i][0]}\nCapacidade: {round(self.ds_pdisk[i][1]/1024/1024,3)} Gb\n\n* ATENCAO: [status_critico] \nMenos de 10% de espaço livre em disco {self.ds_pdisk[i][0]}\n')
        	else: print(f'\n>>> Unidade de Disco: {self.ds_pdisk[i][0]}\nCapacidade: {round(self.ds_pdisk[i][1]/1024/1024,3)} Gb\n\n* [status_OK]\nMais de 10% de espaço livre em disco {self.ds_pdisk[i][0]}\n')
        print('-'*80)
        # memoria
        print('\n%51s' % ('ANÁLISE DE MEMÓRIA RAM'))
        print(f'\nMemória Total {modelo["memo_total"]/1024:>12.3f} Gb'
        	f'\nMemória Disponível {modelo["memo_disp"]/1024:>7.3f} Gb'
        	f'\n\n* {self.status_memo}\n{"-"*80}\n')
            
        print('%54s' % ('ANÁLISE DE PROGRAMAS E PROCESSOS'))
        # programas lentidao      
        if len(self.excluir) > 0:
        	print(f'\n>>> Encontrados [{len(self.excluir)}] programas que podem estar causando lentidão\n')
        	print('\tNOME\t\t\t\t\t\t VERSAO\n')
        	for proc in modelo['prog_lentidao']:
        		print(f'* {proc["prog_nome"][:20]:>20}'
        			f'{proc["prog_vers"]:>40}')
        #print('-'*80) 
        # navegadores e versao
        if len(self.clt_naveg) > 0:
        	print(f'\n>>> Encontrados [{len(self.clt_naveg)}] navegadores de internet\n')
        	print('\tNOME\t\t\t\t\t\t VERSAO\n')
        	for proc in modelo['clt_naveg']:
        		print(f'*  {proc["naveg_nome"][:20]:<20}'
        			f'{proc["naveg_vers"]:>42}')
        #    print('-'*80) 

        # programas usados por determinada empresa

        if len(self.clt_progEmp) > 0:
        	print(f'\n>>> Encontrados [{len(self.clt_progEmp)}] programas relacionados à *det. empresa*\n')
        	print('\tNOME\t\t\t  STATUS\t\t\t VERSAO\n')
        	for proc in modelo['clt_progEmp']:
        		print(f'*  {proc["progId_nome"][:20]:<20}'
        			f'{proc["progId_status"]:>18}'
        			f'{proc["progId_vers"]:>20}')
        #    print('-'*80)

        # processos windows
        print(f'\n>>> Processos ordenados por consumo de memória\n')
        print('\tNOME\t\t   USO MEMORIA\t\t\t     USO CPU\n')
        for i in range(5):
            print(f'{self.proc_sumaMemo(self.ds_processos).loc[i]["proc_nome"][:17]:>17}'
        	    f'{self.proc_sumaMemo(self.ds_processos).loc[i]["proc_memo"]/1024:>18.2f} Mb'
   	    	    f'{self.proc_sumaMemo(self.ds_processos).loc[i]["proc_cpu"]:>21.2f} %')        

        print(f'\n>>> Processos ordenados por consumo de CPU\n')
        print('\tNOME\t\t   USO MEMORIA\t\t\t     USO CPU\n')         
        for i in range(5):
            print(f'{self.proc_sumaCpu(self.ds_processos).loc[i]["proc_nome"][:17]:>17}'
        	    f'{self.proc_sumaCpu(self.ds_processos).loc[i]["proc_memo"]/1024:>18.2f} Mb'
   	    	    f'{self.proc_sumaCpu(self.ds_processos).loc[i]["proc_cpu"]:>21.2f} %')  
        print('-'*80)
        print('\n%44s' % ('TESTE DE INTERNET'))
        print(f'\n* Download {(modelo["teste_net"][0]["download"]/1024/1024):>26.2f} Mb'
            f'\n* Upload {(modelo["teste_net"][0]["upload"]/1024/1024):>28.2f} Mb'
            f'\n* Ping {modelo["teste_net"][0]["ping"]:>30.2f} ms\n')	
        print(f'\nConexão servidor Sofstore\n'
            f'\nMédia do ping {modelo["teste_ping"][0]["sofstore_medPing"]:>23} ms\n'
            f'Passou comunicação {modelo["teste_ping"][0]["sofstore_passed"]:>15}\n'
            f'Falhas de Comunicaçao {modelo["teste_ping"][0]["sofstore_failed"]:>12}'
            f'\n\n\nConexão servidor Google'
            f'\n\nMédia do ping {modelo["teste_ping"][0]["google_medPing"]:>23} ms\n'
            f'Passou comunicação {modelo["teste_ping"][0]["google_passed"]:>15}\n'
            f'Falhas de Comunicaçao {modelo["teste_ping"][0]["google_failed"]:>12}\n')
        print('-'*80) 

        print('\nImpressoras instaladas:\n')
        print('\tIMPRESSORA\t\t\tPORTA\t\tSTATUS\t\tJOBS\n')
        for imp in modelo['imp_inst']:    
        	print(f'*  {imp["imp_nome"][:17]:>17}'
        		f'{imp["imp_porta"][:10]:>19}'
        		f'{imp["imp_status"]:>13}'
        		f'{imp["imp_jobs"]:>15}')
        print('\n','-'*80)

        # nome da maquina e data do relatorio
        print('\nIdentificação da Máquina\n',self.id_maq)
        print('\nData do Diagnóstico\n',self.data_ocor)
        print('-'*80)
        print(f'\n Usuário: {modelo["info_usuario"][0]["user"]:>5}'
              f'\n    Loja: {modelo["info_usuario"][0]["loja"]:>3}')
        print('\n','-'*80)
        sys.stdout = saida_default
