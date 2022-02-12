from socket import *
serverName = '129.219.10.241'
serverPort = 6250
clientSocket = socket(AF_INET, SOCK_DGRAM)
while (True):
        message = input('Input lowercase sentence:')
        clientSocket.sendto(message.encode(),(serverName, serverPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        print(modifiedMessage.decode())
clientSocket.close()