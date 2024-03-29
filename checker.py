import sys

if len(sys.argv) < 2:
    print("Digite " + sys.argv[0] + " <arquivo_log>")
    sys.exit()

try:
    l = open(sys.argv[1], "r")
except IOError:
    print("Não foi possível abrir o arquivo " + sys.argv[0])
if l.mode is not "r":
    print("Não foi possível ler o arquivo " + sys.argv[0])
    sys.exit()

var = -1 # variavel compartilhada entre as threads
escritoras_ativas = 0 # qtd de escritoras ativas, tem de ser 1 ou 0 para quando leitoras ativas > 0
leitoras_ativas = 0 # qtd de leitoras ativas, pode assumir qualquer valor, contanto que seja 0 quando escritoras_ativas > 0

log = l.readlines() # log do programa
params = log[0].split() # primeira linha do log contem os args que o programa recebeu (nthreads, qtd_execucao)
nthreads_leitoras = int(params[0])
nthreads_escritoras = int(params[1])
n_exec_l = int(params[2])
n_exec_e = int(params[3])
qtd_exec = 2 * ((nthreads_leitoras * n_exec_l) + (nthreads_escritoras * n_exec_e)) # ¯\_(ツ)_/¯

qtd_exec_leitoras = {} # dictionary p guardar quantas execucoes as threads leitoras realizaram
for i in range(nthreads_leitoras): # populando o dictionary com a qtd de execucoes
    qtd_exec_leitoras[i*2] = int(params[2]) # a key é o id das threads

qtd_exec_escritoras = {} # dictionary p guardar quantas execucoes as threads escritoras realizaram
for i in range(nthreads_escritoras): # populando o dictionary com a qtd de execucoes
    qtd_exec_escritoras[i + (i + 1)] = int(params[3]) # a key é o id das threads

log_thread = {} # map p guardar os logs das threads
for i in range(nthreads_leitoras):
    file_name = str(i*2) + ".txt"
    with open(file_name) as f:
        log_thread[i*2] = f.readlines() # a key é o id da thread e o value são as linhas do log

def entraEscrita(id, leit, escr):
    global var, escritoras_ativas, leitoras_ativas
    var = id # guarda o id da thread na variavel

    escritoras_ativas += 1 # incrementa o numero de threads escritoras ativas, tem de ser 0 ou 1

    if escr != escritoras_ativas: # verifica se o numero de threads no log é o mesmo da execução sequencial
        print("Valor de escritoras ativas diferente do registrado no log. A execução do programa é incorreta.")
        sys.exit()
    
    if leit != leitoras_ativas: # verifica se o numero de threads no log é o mesmo da execução sequencial
        print("Valor de leitoras ativas diferente do registrado no log. A execução do programa é incorreta.")
        sys.exit()

    if escritoras_ativas > 1: # se mais de uma thread esta escrevendo ao mesmo tempo, deu ruim
        print("Mais de uma thread escritora ativa, a execução está incorreta. threads: " + str(escritoras_ativas))
        sys.exit()
    
    if qtd_exec_escritoras[id] == 0: # verifica se essa thread executou mais vezes do que deveria
        print("Thread escritora executando mais vezes do que deveria.")
        sys.exit()
    
def saiEscrita(id, leit, escr):
    global escritoras_ativas, leitoras_ativas

    qtd_exec_escritoras[id] -= 1 # diminui o numero de execucoes que ainda restam para a thread

    escritoras_ativas -= 1

    if escr != escritoras_ativas: # verifica se o numero de threads no log é o mesmo da execução sequencial
        print("Valor de escritoras ativas diferente do registrado no log. A execução do programa é incorreta.")
        sys.exit()
    
    if leit != leitoras_ativas: # verifica se o numero de threads no log é o mesmo da execução sequencial
        print("Valor de leitoras ativas diferente do registrado no log. A execução do programa é incorreta.")
        sys.exit()

def entraLeitura(id, leit, escr):
    global var, escritoras_ativas, leitoras_ativas

    leitoras_ativas += 1

    if qtd_exec_leitoras[id] == 0: # verifica se essa thread executou mais vezes do que deveria
       print("Thread leitora executando mais vezes do que deveria.")
       sys.exit()
    
    execucao = n_exec_l - qtd_exec_leitoras[id]
    valor_lido = int(log_thread[id][execucao].rstrip("\n"))
    
    if valor_lido != var: # valor da variavel é diferente do que a thread leitora leu 
        print("Thread " + str(id) + " leu um valor incorreto.")
        sys.exit()
    
    if escr != escritoras_ativas: # verifica se o numero de threads no log é o mesmo da execução sequencial
        print("Valor de escritoras ativas diferente do registrado no log. A execução do programa é incorreta.")
        sys.exit()
    
    if leit != leitoras_ativas: # verifica se o numero de threads no log é o mesmo da execução sequencial
        print("Valor de leitoras ativas diferente do registrado no log. A execução do programa é incorreta.")
        sys.exit()
    

def saiLeitura(id, leit, escr):
    global escritoras_ativas, leitoras_ativas
    
    qtd_exec_leitoras[id] -= 1 # decrementa o numero de execucoes que ainda restam para a thread
    leitoras_ativas -= 1 # decrementa o numero de leitoras ativas

    if escr != escritoras_ativas: # verifica se o numero de threads no log é o mesmo da execução sequencial
        print("Valor de escritoras ativas diferente do registrado no log. A execução do programa é incorreta.")
        sys.exit()
    
    if leit != leitoras_ativas: # verifica se o numero de threads no log é o mesmo da execução sequencial
        print("Valor de leitoras ativas diferente do registrado no log. A execução do programa é incorreta.")
        sys.exit()


for i in range(qtd_exec):
    linha = log[i+1].split("\n") # pega uma linha do log
    linha = linha[0].split(";") # splita os valores da linha em 0:<id> 1:<funcao> 2:<valor_da_variavel> 3:<leitoras_executando> 4:<escritoras_executando>

    if int(linha[0]) % 2 == 0: # se id é par, thread leitora
        if linha[1] == "entraLeitura()":
            entraLeitura(int(linha[0]), int(linha[3]), int(linha[4])) # x thread executa a operação de leitura
        elif linha[1] == "saiLeitura()":
            saiLeitura(int(linha[0]), int(linha[3]), int(linha[4]))
    else: # id é impar, então thread escritora
        if linha[1] == "entraEscrita()":
            entraEscrita(int(linha[0]), int(linha[3]), int(linha[4])) # x thread executa a operação de escrita
        elif linha[1] == "saiEscrita()": # se a operação de escrita é saiEscrita(), decrementa o número de escritoras ativas
            saiEscrita(int(linha[0]), int(linha[3]), int(linha[4]))
        else:
            print("sei la mano qq isso  " + linha[1])
            sys.exit()

for i in range(nthreads_escritoras):
    if qtd_exec_escritoras[i + (i + 1)] is not 0: # verifica se escreveu o numero esperado de vezes
        print("A thread " + str(i + (i + 1)) + " não executou todas as vezes que deveria.")
        sys.exit()

for i in range(nthreads_leitoras):
    if qtd_exec_leitoras[i * 2] is not 0: # verifica se leu o numero esperado de vezes
        print("A thread " + str(i * 2) + " não executou todas as vezes que deveria.")
        sys.exit()

print("O programa foi executado corretamente :)")
print("Não houveram leitoras e escritoras acessando a variavel compartilhada ao mesmo tempo.")
print("Todas as " + str(nthreads_leitoras) + " threads leitoras executaram o numero de vezes esperado. " + str(qtd_exec_leitoras))
print("Todas as " + str(nthreads_escritoras) + " threads escritoras executaram o numero de vezes esperado. " + str(qtd_exec_escritoras))