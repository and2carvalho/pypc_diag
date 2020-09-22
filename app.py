#!/usr/bin/env python3

import tkinter as tk
import cBios
import db
import testeNet
from testePing import Tping
import os
import sys
from configparser import ConfigParser
import datetime

# início da aplicação gráfica 
class Tela_main:
    def __init__(self, master):
        self.master = master
        self.logo = tk.PhotoImage(file=resource_path('static/imgMenu.png'))
        self.frame = tk.Frame(self.master, bg = 'white')
        self.logoLabel = tk.Label (self.master, image = self.logo, bg = "white") 
        self.userLabel = tk.Label (self.frame, text = "\nPor favor, digite seu nome: ", bg = "white")      
        self.userTextEntry = tk.Entry(self.frame, width = 14, bg = "white")      
        self.lojaLabel = tk.Label (self.frame, text = "\nInsira o nome da sua Loja: ", bg = "white")       
        self.lojaTextEntry = tk.Entry(self.frame, width = 14, bg = "white")       
        self.espaço = tk.Label(self.frame, text = '',bg='white')       
        self.diagBt = tk.Button(self.frame, text = "Enviar", width = 10, command=self.click_diag)
        self.espaço2 = tk.Label(self.frame, text = '',bg='white')
        self.sairBt = tk.Button(self.frame, text = "Sair", width = 10, command=self.sair)
        self.relatorio = tk.Text(self.frame, bg='white', wrap = tk.WORD)
        self.espaço3 = tk.Label(self.frame, text = '',bg='white')
        self.logoLabel.pack()
        self.userLabel.pack()
        self.userTextEntry.pack()
        self.userTextEntry.focus()
        self.lojaLabel.pack()
        self.lojaTextEntry.pack()
        self.espaço.pack()
        self.diagBt.pack()
        self.espaço2.pack()
        self.relatorio.pack()
        self.espaço3.pack()
        self.sairBt.pack()
        self.frame.pack(fill='x')
 
    def compoe_ocor(self):
        ocor = cBios.Clt_bios()

        ocor.modelo['info_usuario'].append({'user':self.userTextEntry.get(),'loja':self.lojaTextEntry.get()})
        # realiza testes de ping com servidores
        sofPing = Tping()
        sofPing.__ini__(host='www.duckduckgo.com')
        sofPing.resutado()
        gooPing = Tping()
        gooPing.__ini__(host='www.google.com.br')
        gooPing.resutado()
        ocor.modelo['teste_ping'].append({'sofstore_medPing': sofPing.mediaPing(),
        'sofstore_passed':sofPing.passed,'sofstore_failed':sofPing.failed,
        'google_medPing': gooPing.mediaPing(),'google_passed':gooPing.passed,
        'google_failed':gooPing.failed})
        # realiza teste de velocidade de internet
        try:
            testeNet.testeNet()
            ocor.modelo['teste_net'].append(testeNet.resultado_testeNet)
        except: 
            ocor.modelo['teste_net'].append({'download' : 0,
            'upload' : 0, 'ping' : 0})
            pass
               
        # adiciona informaçõe globais ao banco de dados
        sql_ocorBios = f'''insert into tab_ocorBios (
            id_maq,
            nome_processador,
            qtd_processador,
            memo_total,
            memo_disp,
            nome_maq,
            data_ocor,
            ocor_id
            ) 
            values (
                "{ocor.modelo["id_maq"]}",
                "{ocor.modelo["nome_processador"]}",
                {ocor.modelo["qtd_processador"]},
                {ocor.modelo["memo_total"]},
                {ocor.modelo["memo_disp"]},
                "{ocor.modelo["nome_maq"]}",
                "{ocor.modelo["data_ocor"]}",
                "{ocor.modelo["id_maq"].split('-')[-1]}{ocor.modelo["data_ocor"].replace(' ','-')}"
                )        
        '''
        try:
            db.cursor.execute(sql_ocorBios)
            db.conexao.commit()
        except:
            pass

        # adiciona HDs ao banco de dados
        for reparticao in ocor.modelo['disco_rigido']:
            try:
                valores = ', '.join("'" + str(x).replace('/', '_') + "'" for x in reparticao.values())
                sql_ocorHd = f''' insert into tab_ocorHd(
                    ocor_id,
                    hd_nome,
                    hd_tamanho,
                    hd_livre
                    )
                    values(
                    "{ocor.modelo["id_maq"].split('-')[-1]}{ocor.modelo["data_ocor"].replace(' ','-')}",
                    "{valores.split(",")[0]}",
                    {valores.split(",")[1]},
                    {valores.split(",")[2]}
                    )
                '''
                db.cursor.execute(sql_ocorHd)
                db.conexao.commit()
            except:
                pass
        # adiciona processos ao banco de dados
        for processo in ocor.modelo['proc_maq']:
            # separa valores de cada processo para inserir no comando sql
            try:
                valores = ', '.join("'" + str(x).replace('/', '_') + "'" for x in processo.values()) 
                sql_ocorProc = f'''insert into tab_ocorProc(
                    ocor_id,
                    proc_nome,
                    proc_pid,
                    proc_memo,
                    proc_cpu,
                    proc_usuario
                    )
                    values (
                        "{ocor.modelo["id_maq"].split('-')[-1]}{ocor.modelo["data_ocor"].replace(' ','-')}",
                        {valores}
                        )      
                    '''  
                db.cursor.execute(sql_ocorProc)
                db.conexao.commit()
            except: pass
         # adiciona progamas instalados ao banco de dados
        for instalados in ocor.modelo['insta_maq']:
            # separa valores de cada programa instalado para inserir no comando sql
            try:
                valores = ', '.join("'" + str(x).replace('/', '_') + "'" for x in instalados.values()) 
                sql_ocorInsta = f'''insert into tab_ocorInsta(
                    ocor_id,
                    prog_nome,
                    prog_vers
                    )
                    values (
                        "{ocor.modelo["id_maq"].split('-')[-1]}{ocor.modelo["data_ocor"].replace(' ','-')}",
                        {valores}
                        )      
                    '''  
                db.cursor.execute(sql_ocorInsta)
                db.conexao.commit()
            except: pass

         # adiciona impressoras ao banco de dados
        for imp in ocor.modelo['imp_inst']:
            # separa valores de cada impressora para inserir no comando sql
            try:
                valores = ', '.join("'" + str(x).replace('/', '_') + "'" for x in imp.values()) 
                sql_ocorImp = f'''insert into tab_ocorImp(
                    ocor_id,
                    imp_nome,
                    imp_porta,
                    imp_jobs,
                    imp_status
                    )
                    values (
                        "{ocor.modelo["id_maq"].split('-')[-1]}{ocor.modelo["data_ocor"].replace(' ','-')}",
                        {valores}
                        )      
                    '''  
                db.cursor.execute(sql_ocorImp)
                db.conexao.commit()
            except: pass
        
        # adiciona teste ping ao banco de dados
        for instalados in ocor.modelo['teste_ping']:
            # separa valores de ping para inserir no comando sql
            try:
                valores = ', '.join("'" + str(x).replace('/', '_') + "'" for x in instalados.values()) 
                sql_ocorPing = f'''insert into tab_ocorPing(
                    ocor_id,
                    sofstore_medPing,
                    sofstore_passed,
                    sofstore_failed,
                    google_medPing,
                    google_passed,
                    google_failed
                    )
                    values (
                        "{ocor.modelo["id_maq"].split('-')[-1]}{ocor.modelo["data_ocor"].replace(' ','-')}",
                        {valores}
                        )      
                    '''  
                db.cursor.execute(sql_ocorPing)
                db.conexao.commit()
            except: pass

        # adiciona teste net ao banco de dados
        sql_ocorNet = f'''insert into tab_ocorNet(
            ocor_id,
            download,
            upload,
            ping,
            prov_net
            )
            values (
                "{ocor.modelo["id_maq"].split('-')[-1]}{ocor.modelo["data_ocor"].replace(' ','-')}",
                {ocor.modelo['teste_net'][0]['download']},
                {ocor.modelo['teste_net'][0]['upload']},
                {ocor.modelo['teste_net'][0]['ping']},
                "{ocor.modelo['teste_net'][0]['client']['isp']}"
                )      
            '''  
        try:
            db.cursor.execute(sql_ocorNet)
            db.conexao.commit()
        except:
            pass

        # adiciona usuario ao banco de dados
        sql_ocorUser = f'''insert into tab_ocorUser(
            ocor_id,
            user,
            loja
            )
            values (
                "{ocor.modelo["id_maq"].split('-')[-1]}{ocor.modelo["data_ocor"].replace(' ','-')}",
                "{ocor.modelo["info_usuario"][0]["user"]}",
                "{ocor.modelo["info_usuario"][0]["loja"]}"
                )      
            '''  
        try:
            db.cursor.execute(sql_ocorUser)
            db.conexao.commit()
        except:
            pass

        # gera relatório em formato de arquivo txt
        ocor.relatorio_txt(ocor.modelo,saida='txt')
        
        # gera arquivo json com informações coletadas
        arq_final = str(cBios.mydict(ocor.modelo))
        with open('id_diag.json', 'w',errors='ignore') as f:
            f.write(arq_final)
            
    def click_diag(self):
        
        self.master.withdraw()
        self.compoe_ocor()
        # utiliza arquivo txt para mostrar relatório na interface
        try:
            with open('id_diag_'+datetime.datetime.now(tz=None).strftime('%Y-%m-%d %H:%M:%S')[:10] +'.txt','r')as f:
                self.relatorio.insert(tk.INSERT,f.read())
        except:
            pass
        self.master.geometry('700x570')
        self.userLabel.destroy()
        self.userTextEntry.destroy()
        self.lojaLabel.destroy()
        self.lojaTextEntry.destroy()
        self.diagBt.destroy()
        self.master.update()
        self.master.deiconify()

    def click_monitora(self):
        self.compoe_ocor()
        self.master.quit()
        self.master.destroy()
    
    def sair(self):
        self.master.quit()
        self.master.destroy()
        
# necessário para adicionar file ao exe standAlon
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    global auto_user
    root = tk.Tk()
    app = Tela_main(root)
    app.master.title("  BEM VINDO AO DIAGNOSTICO DE SUPORTE PYPC_DIAG ")
    app.master.geometry("500x260")
    app.master.configure(background = "white")
    app.master.protocol("WM_DELETE_WINDOW", app.sair)
    # caso possua config file o programa inicia automaticamente
    try:
        config = ConfigParser()
        config.read('monitora.ini')
        auto_user = config['login']['nome']
        auto_loja = config['login']['loja']
        app.userTextEntry.insert(0,auto_user)
        app.lojaTextEntry.insert(0,auto_loja)
        app.click_monitora()
    except:
        pass
        
    root.mainloop()
             

if __name__ == '__main__':
   main() 
