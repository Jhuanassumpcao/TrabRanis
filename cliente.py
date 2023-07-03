import socket
import pickle
import crcmod.predefined

# Função para calcular o CRC de um quadro
def calcular_crc(quadro):
    crc16 = crcmod.predefined.mkCrcFun('crc-16')
    dados_serializados = pickle.dumps(quadro['dados'])
    return crc16(dados_serializados)

# Cria um objeto socket
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

endereco_servidor = ('127.0.0.1', 2080)
cliente_socket.connect(endereco_servidor)

# Função para enviar um quadro para o servidor
def enviar_quadro(quadro):
    quadro['crc'] = calcular_crc(quadro)
    cliente_socket.send(pickle.dumps(quadro))

# Dados a serem enviados ao servidor
mensagens = ["Olá, servidor!", "Esta é uma mensagem de teste.", "Aqui está outra mensagem."]

# Número máximo de quadros a serem enviados sem aguardar ACKs
max_quadros = 3

# Variáveis de controle
quadro_numero = 0
base_quadro = 0

# Envia os quadros para o servidor
while quadro_numero < len(mensagens):
    if quadro_numero < base_quadro + max_quadros:
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
        # Aguarda ACKs
        try:
            cliente_socket.settimeout(1.0)
            ack = pickle.loads(cliente_socket.recv(1024))
            if ack['ack']:
                print("Recebido ACK para quadro", ack['numero'])
                base_quadro = ack['numero'] + 1
        except socket.timeout:
            print("Timeout. Reenviando quadros", base_quadro, "a", quadro_numero - 1)

# Aguarda ACKs finais
while base_quadro < quadro_numero:
    try:
        cliente_socket.settimeout(1.0)
        ack = pickle.loads(cliente_socket.recv(1024))
        if ack['ack']:
            print("Recebido ACK para quadro", ack['numero'])
            base_quadro = ack['numero'] + 1
    except socket.timeout:
        print("Timeout. Reenviando quadros", base_quadro, "a", quadro_numero - 1)

# Fecha a conexão
cliente_socket.close()
