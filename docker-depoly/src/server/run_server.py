import xml.etree.cElementTree as ET
import socket, multiprocessing
import struct
import os
from db import create_tables, delete_tables
from transactions import handle_transaction
from create import handle_create

def handleRequest(data, root, c):
    if root == 'transactions':
        response_str = handle_transaction(data)
    elif root == 'create':
        response_str = handle_create(data)
    else: 
        pass #handle error
    # Send response to client
    c.send(response_str)
    print('send response xml back to client')
    
    # Close the socket connection when the client is done
    c.close()


def initDatabase():
    delete_tables()
    print("delete tables")
    create_tables()
    print("build tables")


def buildServer() -> socket.socket:
    s = socket.socket()
    hostname = socket.gethostname()
    print(hostname)
    port = 12345
    s.bind((hostname, port))
    s.listen(100)
    return s


def worker(s):
    print("Worker started")
    num_processes = 4
    #l = multiprocessing.Lock()
    pool = multiprocessing.Pool(processes=num_processes)
    Processes = []
    '''
    cpu_cors = 4

    for i in range(num_processes):
        p = pool._pool[i]
        affinity = range(0,cpu_cors)
        os.sched_setaffinity(p.pid, affinity)
    '''
    print(111)
    while True:
        c, addr = s.accept()
        print(f"Connected to {addr}")

        #while True:
        # Receive the length of the XML data
        len_bytes = c.recv(4)
        if not len_bytes:
            break
        xml_len = struct.unpack('i', len_bytes)[0]
        #print(xml_len)
        # Receive the new line character
        c.recv(1)
        # Receive the rest of the XML data
        xml_data = bytearray()
        while len(xml_data) < xml_len:
            buffer = c.recv(xml_len - len(xml_data))
            if not buffer:
                break
            xml_data.extend(buffer)
        #print(xml_data.decode())
        # Parse the XML data
        xml_str = xml_data.decode()
        data = ET.ElementTree(ET.fromstring(xml_str))
        root = data.getroot().tag

        # Assign task to available worker process
        pool.apply_async(handleRequest, args=(data, root, c))
        #p = multiprocessing.Process(target=handleRequest,args=(data,root,c,))
        #Processes.append(p)
        #p.start()
        
        
    #for p in Processes:
    #    p.join()
    # Close the multiprocessing pool when the worker loop exits
    pool.close()
    pool.join()

