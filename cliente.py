import socket
import pickle
import random

# Função para calcular o CRC de um quadro
def calcular_crc(quadro):
    crc16 = 0xFFFF
    poly = 0x8005

    dados_serializados = pickle.dumps(quadro['dados'])
    dados = bytearray(dados_serializados)

    for byte in dados:
        crc16 ^= (byte << 8)
        for _ in range(8):
            if crc16 & 0x8000:
                crc16 = (crc16 << 1) ^ poly
            else:
                crc16 <<= 1

    return crc16 & 0xFFFF

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

# Lê as mensagens de um arquivo de texto
with open('mensagens.txt', 'r') as arquivo:
    mensagens = arquivo.read().splitlines()

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
        if random.random() < 0.3:  # 30% de chance de perder o ACK
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
