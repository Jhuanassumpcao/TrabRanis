import socket
import pickle

def calcular_crc(dados):
    crc16 = 0xFFFF
    poly = 0x8005

    for byte in dados:
        crc16 ^= (byte << 8)
        for _ in range(8):
            if crc16 & 0x8000:
                crc16 = (crc16 << 1) ^ poly
            else:
                crc16 <<= 1

    return crc16 & 0xFFFF

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12345)

try:
    server_socket.bind(server_address)
    server_socket.listen(1)
    print('Servidor pronto para receber conexões.')

    client_socket, addr = server_socket.accept()
    print('Conexão estabelecida com o cliente:', addr)

    expected_frame_no = 0

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            try:
                received_frame = pickle.loads(data)
                print('Quadro válido recebido:', received_frame)

                if received_frame['numero'] == expected_frame_no and calcular_crc(received_frame['dados'].encode()) == received_frame['crc']:
                    print('Enviando ACK:', expected_frame_no)
                    client_socket.send(pickle.dumps(expected_frame_no))
                    expected_frame_no += 1
                else:
                    print('Quadro inválido. Ignorando e enviando ACK:', expected_frame_no - 1)
                    client_socket.send(pickle.dumps(expected_frame_no - 1))
                    continue  # Continua aguardando o próximo quadro

            except pickle.UnpicklingError:
                print('Erro ao decodificar o quadro recebido.')
        except socket.timeout:
            print('Timeout: Nenhum dado recebido.')
        except socket.error as e:
            print('Erro na comunicação com o cliente.')
            print('Detalhes do erro:', str(e))
            break

    client_socket.close()
    server_socket.close()
    print('Conexão encerrada com o cliente.')

except socket.error as e:
    print('Erro ao iniciar o servidor.')
    print('Detalhes do erro:', str(e))
