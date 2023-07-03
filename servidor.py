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
def enviar_ack(numero_quadro):
    if quadro_numero_esperado <= numero_quadro < quadro_numero_esperado + max_quadros:
        ack = {'ack': True, 'numero': numero_quadro}
        cliente_socket.send(pickle.dumps(ack))

# Função para enviar uma negação (NAK) ao cliente
def enviar_nak(numero_quadro):
    if quadro_numero_esperado <= numero_quadro < quadro_numero_esperado + max_quadros:
        nak = {'ack': False, 'numero': numero_quadro}
        cliente_socket.send(pickle.dumps(nak))

# Função para receber um quadro do cliente
def receber_quadro():
    quadro_serializado = cliente_socket.recv(1024)
    return pickle.loads(quadro_serializado)

# Função para processar o quadro recebido
def processar_quadro(quadro):
    if calcular_crc(quadro) == quadro['crc']:
        print("Quadro válido recebido:", quadro)
        enviar_ack(quadro['numero'])
    else:
        print("Quadro inválido recebido. CRC não coincide.")
        enviar_nak(quadro['numero'])

# Lista de mensagens a serem recebidas
mensagens = ["Olá, cliente!", "Esta é uma mensagem de teste.", "Aqui está outra mensagem."]

# Aceita conexões de clientes
cliente_socket, endereco_cliente = servidor_socket.accept()
print("Conexão estabelecida com:", endereco_cliente)

# Variáveis de controle Go-Back-N ARQ
quadro_numero_esperado = 0
max_quadros = 3

# Recebe e processa os quadros enviados pelo cliente
while True:
    quadro = receber_quadro()
    if quadro_numero_esperado <= quadro['numero'] < quadro_numero_esperado + max_quadros:
        if quadro['numero'] == quadro_numero_esperado:
            processar_quadro(quadro)
            quadro_numero_esperado += 1
        else:
            enviar_ack(quadro_numero_esperado - 1)
    else:
        enviar_ack(quadro_numero_esperado - 1)

    # Verifica se todos os quadros foram recebidos
    if quadro_numero_esperado == len(mensagens):
        break

# Envia ACK final
enviar_ack(quadro_numero_esperado)

# Fecha a conexão
cliente_socket.close()
servidor_socket.close()
