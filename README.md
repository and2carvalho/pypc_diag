# PyPc_Diag
<p align="center">
    <img width="320" height="250" src="static/main.png"/>
    <img width="320" height="250" src="static/output.png"/>
</p>


## Descrição de Arquivos:

**app.py** - estrutura da aplicação gráfica que chama
os processos e métodos do programa. O arquivo fecha
automaticamente após 2 minutos de inatividade após
gerado o relatório.

**cBios.py** - Classe para instanciar o objeto da ocorrencia,
o script concentra funções e cálculos usados na aplicação. 

**testeNet.py** - Classe que realiza teste de velocidade da
internet. Engloba lista de servidores disponível para
realizar o teste e calcula melhor rota baseado no ping.

**testePing.py** - Classe que realiza teste de conexão com
servidor.

### Opção MONITORA (para ser usada junto com o agendador de tarefas do windows):

A criação de um arquivo .ini permite que o aplicativo
rode com login automático e sem intereção do usuario.
Para isso basta criar um arquivo monitora.ini (o nome 
tem que ser MONITORA) mantendo-o na pasta raiz.

modelo do conteudo do arquivo:
(copie as 3 linhas abaixo em um arquivo txt substituindo
os ```*``` com as informações de cada cliente)
```
[login]
nome = *
loja = *
```
# Compilação para stand alone exe:

pip install auto-py-to-exe.

Fazer upload do arquivo app.py no campo SCRIPT LOCATION,
marcar a opção ONE FILE e deixar CONSOLE BASED nas opções
de CONSOLE WINDOW.

Em ADDITIONAL FILES adicionar o arquivo logoID.png e deixar
um '.' no campo ao lado do caminho do arquivo (DESTINATION).
Nas opções de avançado basta localizar a o campo '-n' e inserir
o nome do arquivo (id_diag). 
