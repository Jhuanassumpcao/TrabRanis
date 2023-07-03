import socket
import pickle
import crcmod.predefined

# Função para calcular o CRC de um quadro
def calcular_crc(quadro):
    crc16 = crcmod.predefined.mkCrcFun('crc-16')
    dados_serializados = pickle.dumps(quadro['dados'])
    return crc16(dados_serializados)

# Cria um objeto socket
servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

endereco_servidor = ('127.0.0.1', 2080)
servidor_socket.bind(endereco_servidor)
servidor_socket.listen(1)

print("Servidor pronto para receber conexões.")

# Função para enviar uma confirmação (ACK) ao cliente
def enviar_ack():
    ack = {'ack': True}
    cliente_socket.send(pickle.dumps(ack))

# Função para enviar uma negação (NAK) ao cliente
def enviar_nak():
    nak = {'ack': False}
    cliente_socket.send(pickle.dumps(nak))

# Função para receber um quadro do cliente
def receber_quadro():
    quadro_serializado = cliente_socket.recv(1024)
    return pickle.loads(quadro_serializado)

# Função para processar o quadro recebido
def processar_quadro(quadro):
    if calcular_crc(quadro) == quadro['crc']:
        print("Quadro válido recebido:", quadro)
        enviar_ack()
    else:
        print("Quadro inválido recebido. CRC não coincide.")
        enviar_nak()

# Aceita conexões de clientes
cliente_socket, endereco_cliente = servidor_socket.accept()
print("Conexão estabelecida com:", endereco_cliente)

# Variáveis para controle da janela de recebimento
janela_recebimento_base = 0
janela_recebimento_tamanho = 3
janela_recebimento = []

# Recebe os quadros e adiciona na janela de recebimento
while True:
    try:
        quadro = receber_quadro()
        if quadro['tamanho'] == janela_recebimento_base:
            janela_recebimento.append(quadro)
            janela_recebimento_base += 1
            processar_quadro(quadro)
        else:
            enviar_nak()
    except EOFError:
        break

# Fecha a conexão
cliente_socket.close()
servidor_socket.close()
