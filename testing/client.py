from multiprocessing import Pool
import socket
import time
import struct
import sys
#from db import getTotalBalance

BUFFER = 100000

def send_file(filename):
    print(filename)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.gethostname())
    server_address = ('0.0.0.0', 12345)
    sock.connect(server_address)
    print("connected")
    with open(filename, 'rb') as f:
        xml_data = f.read()
    print("read")
    xml_len = len(xml_data)

    current_time = time.time()
    sock.send(struct.pack('i', xml_len))
    print("send_len")
    sock.send('\n'.encode())
    sock.sendall(xml_data)
    response_data = sock.recv(BUFFER)
    time_passed = time.time() - current_time

    response_str = response_data.decode()
    print('Time taken to send/receive one XML transactions:', time_passed)
    #print('Received response:', response_str)
    sock.close()


if __name__ == '__main__':
    current_time = time.time()
    pool = Pool(4)
    filename = 'testCreate.xml'
    send_file(filename)
    #balance1 = getTotalBalance()
    for i in range(10):
        filename = 'testTrans'+str(i)+'.xml'
        pool.apply_async(send_file, args=(filename,))
    pool.close()
    pool.join()
    #balance2 = getTotalBalance()
    #if abs(balance1 - balance2) < 1e-4:
    #    print('Successfully match, balance before is ', balance1, ' balance after is ',balance2)
    #else:
    #    print('Fail match, balance before is ',balance1,' balance after is ',balance2)
    time_passed = time.time() - current_time
    print('Time taken to send/receive all XML transactions:', time_passed)
