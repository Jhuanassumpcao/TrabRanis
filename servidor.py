import socket
import pickle

# Função para calcular o CRC de um quadro
def calcular_crc(quadro):
    crc16 = 0xFFFF  # Valor inicial do CRC com todos os bits em 1
    poly = 0x8005  # Polinômio gerador usado no algoritmo CRC-16 CCITT

    dados_serializados = pickle.dumps(quadro['dados'])  # Serializa os dados do quadro
    dados = bytearray(dados_serializados)  # Converte os dados serializados em um array de bytes

    for byte in dados:
        crc16 ^= (byte << 8)  # XOR do byte com os 8 bits mais significativos do CRC
        for _ in range(8):
            if crc16 & 0x8000:  # Verifica se o bit mais significativo do CRC é 1
                crc16 = (crc16 << 1) ^ poly  # Desloca o CRC para a esquerda e aplica o polinômio gerador
            else:
                crc16 <<= 1  # Desloca o CRC para a esquerda

    return crc16 & 0xFFFF  # Retorna o valor do CRC de 16 bits

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

# Lê as mensagens de um arquivo de texto
with open('mensagens.txt', 'r') as arquivo:
    mensagens = arquivo.read().splitlines()

# Aceita conexões de clientes
cliente_socket, endereco_cliente = servidor_socket.accept()
print("Conexão estabelecida com:", endereco_cliente)

# Variáveis de controle Go-Back-N ARQ
quadro_numero_esperado = 0
max_quadros = 1

# Recebe e processa os quadros enviados pelo cliente
while True:
    quadro = receber_quadro()
    if quadro_numero_esperado <= quadro['numero'] < quadro_numero_esperado + max_quadros:
        if quadro['numero'] == quadro_numero_esperado:
            processar_quadro(quadro)
            quadro_numero_esperado += 1
        else:
            enviar_ack(quadro_numero_esperado - 1)
            enviar_nak(quadro['numero'])  # Envia um NAK para solicitar o reenvio do quadro
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
