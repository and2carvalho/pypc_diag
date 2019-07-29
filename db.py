import mysql.connector

conexao = False
host = ''
user=''
passwd=''
database=''

try:
    conexao = mysql.connector.connect(host=host,user=user,
    passwd=passwd,database=database, port=3306)
except: 
	pass	
    
if conexao:

    print('Conexão com banco de dados realizada com sucesso')
    cursor = conexao.cursor()


 #sql cria tabelas no banco de dados caso elas não existam
#    tab_ocorBios = '''
#    create table if not exists tab_ocorBios (
#        ocor_id varchar(500) not null,
#        id_maq varchar(255),
#        nome_processador varchar(255),
#        qtd_processador int,
#       memo_total double,
#        memo_disp double,
#        nome_maq varchar(255),
#        data_ocor datetime,
#        primary key(ocor_id)
#    ); 
#    '''
#    tab_ocorHd = ''' 
#    create table if not exists tab_ocorHd (
#        reg_id int not null auto_increment,
#        ocor_id varchar(255) not null,
#        hd_nome varchar(255),
#        hd_tamanho double,
#        hd_livre double,
#        primary key(reg_id),
#        foreign key(ocor_id)
#        references tab_ocorBios(ocor_id)
#        on update cascade
#        on delete cascade
#    ); 
#    '''
#    tab_ocorProc = ''' 
#    create table if not exists tab_ocorProc (
#        reg_id int not null auto_increment,
#        ocor_id varchar(255) not null,
#        proc_nome varchar(255),
#        proc_pid int,
#        proc_memo double,
#        proc_cpu double,
#        proc_usuario varchar(255),
#        primary key(reg_id),
#        foreign key(ocor_id)
#        references tab_ocorBios(ocor_id)
#        on update cascade
#        on delete cascade
#    ); 
#    '''
#    tab_ocorInsta = ''' 
#    create table if not exists tab_ocorInsta (
#        reg_id int not null auto_increment,
#        ocor_id varchar(255) not null,
#        prog_nome varchar(255),
#        prog_vers varchar(255),
#        primary key(reg_id),
#        foreign key(ocor_id)
#        references tab_ocorBios(ocor_id)
#        on update cascade
#        on delete cascade
#    ); 
#    '''
#
#    tab_ocorImp = ''' 
#    create table if not exists tab_ocorImp (
#        reg_id int not null auto_increment,
#        ocor_id varchar(255) not null,
#        imp_nome varchar(255),
#        imp_porta varchar(255),
#        imp_jobs int,
#        imp_status int,
#        primary key(reg_id),
#        foreign key(ocor_id)
#        references tab_ocorBios(ocor_id)
#        on update cascade
#        on delete cascade
#    ); 
#    '''
#
#    tab_ocorPing = ''' 
#    create table if not exists tab_ocorPing (
#        reg_id int not null auto_increment,
#        ocor_id varchar(255) not null,
#        sofstore_medPing double,
#        sofstore_passed int,
#        sofstore_failed int,
#        google_medPing double,
#        google_passed int,
#        google_failed int,
#        primary key(reg_id),
#        foreign key(ocor_id)
#        references tab_ocorBios(ocor_id)
#        on update cascade
#        on delete cascade
#    ); 
#    '''
#
#    tab_ocorNet = ''' 
#    create table if not exists tab_ocorNet (
#        reg_id int not null auto_increment,
#        ocor_id varchar(255) not null,
#        download double,
#        upload double,
#        ping double,
#        prov_net varchar(255),
#        primary key(reg_id),
#        foreign key(ocor_id)
#        references tab_ocorBios(ocor_id)
#        on update cascade
#        on delete cascade
#    ); 
#    '''
#
#    tab_ocorUser = ''' 
#    create table if not exists tab_ocorUser (
#        reg_id int not null auto_increment,
#        ocor_id varchar(255) not null,
#        user varchar(255),
#        loja varchar(255),
#        primary key(reg_id),
#        foreign key(ocor_id)
#        references tab_ocorBios(ocor_id)
#        on update cascade
#        on delete cascade
#    ); 
#    '''
#
#    cursor.execute(tab_ocorBios)
#    cursor.execute(tab_ocorHd)
#    cursor.execute(tab_ocorProc)
#    cursor.execute(tab_ocorInsta)
#    cursor.execute(tab_ocorImp)
#    cursor.execute(tab_ocorPing)
#    cursor.execute(tab_ocorNet)
#    cursor.execute(tab_ocorUser)

