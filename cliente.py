import socket
import pickle
import crcmod.predefined
import random

# Função para calcular o CRC de um quadro
def calcular_crc(quadro):
    crc16 = crcmod.predefined.mkCrcFun('crc-16')
    dados_serializados = pickle.dumps(quadro['dados'])
    return crc16(dados_serializados)

# Cria um objeto socket
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

endereco_servidor = ('127.0.0.1', 2080)
cliente_socket.connect(endereco_servidor)

def enviar_quadro(quadro):
    quadro['crc'] = calcular_crc(quadro)
    cliente_socket.send(pickle.dumps(quadro))

# Função para reenviar os quadros dentro da janela
def reenviar_quadros():
    for quadro_numero in range(janela_base, janela_superior):
        mensagem = mensagens[quadro_numero]
        quadro = {
            'numero': quadro_numero,
            'tamanho': len(mensagem),
            'origem': cliente_socket.getsockname(),
            'destino': endereco_servidor,
            'dados': mensagem
        }
        enviar_quadro(quadro)
        print("Reenviado quadro", quadro_numero)

# Dados a serem enviados ao servidor
mensagens = ["Olá, servidor!", "Esta é uma mensagem de teste.", "Aqui está outra mensagem."]

# Número máximo de quadros a serem enviados sem aguardar ACKs
max_quadros = 1

# Variáveis de controle Go-Back-N ARQ
janela_base = 0
janela_superior = max_quadros
ack_confirmados = set()

# Envia os quadros para o servidor
quadro_numero = 0
while quadro_numero < len(mensagens):
    if quadro_numero < janela_superior:
        mensagem = mensagens[quadro_numero]

        # Cria o quadro com as informações
        quadro = {
            'numero': quadro_numero,
            'tamanho': len(mensagem),
            'origem': cliente_socket.getsockname(),
            'destino': endereco_servidor,
            'dados': mensagem
        }

        enviar_quadro(quadro)
        print("Enviado quadro", quadro_numero)
        quadro_numero += 1
    else:
        # Simula perda de ACK no cliente
        if random.random() < 0.8:  # 20% de chance de perder o ACK
            reenviar_quadros()
            continue  # Ignora o ACK e não aguarda resposta

        # Aguarda ACKs
        ack = pickle.loads(cliente_socket.recv(1024))
        if ack['ack']:
            print("Recebido ACK para quadro", ack['numero'])
            if ack['numero'] not in ack_confirmados:
                ack_confirmados.add(ack['numero'])
                if ack['numero'] == janela_base:
                    janela_base += 1
                    janela_superior += 1

# Aguarda ACKs finais
while janela_base < len(mensagens):
    
    ack = pickle.loads(cliente_socket.recv(1024))
    if ack['ack']:
        print("Recebido ACK para quadro", ack['numero'])
        if ack['numero'] not in ack_confirmados:
            ack_confirmados.add(ack['numero'])
            if ack['numero'] == janela_base:
                janela_base += 1
                janela_superior += 1

# Fecha a conexão
cliente_socket.close()
