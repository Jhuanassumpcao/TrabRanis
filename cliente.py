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
mensagem = "Olá, servidor!"

# Tamanho da janela de envio
janela_envio_tamanho = 3

# Variáveis para controle da janela de envio
janela_envio_base = 0
janela_envio_limite = janela_envio_tamanho - 1
janela_envio = []

# Cria os quadros e adiciona na janela de envio
for i in range(len(mensagem)):
    quadro = {
        'tamanho': len(mensagem),
        'origem': cliente_socket.getsockname(),
        'destino': endereco_servidor,
        'dados': mensagem[i]
    }
    janela_envio.append(quadro)

# Envia os quadros na janela de envio
while janela_envio_base <= len(mensagem):
    for i in range(janela_envio_base, min(janela_envio_base + janela_envio_tamanho, len(mensagem))):
        enviar_quadro(janela_envio[i])
    janela_envio_base += janela_envio_tamanho

# Aguarda a resposta do servidor
response = cliente_socket.recv(1024)
print("Dados recebidos do servidor:", response)

# Fecha a conexão
cliente_socket.close()
 