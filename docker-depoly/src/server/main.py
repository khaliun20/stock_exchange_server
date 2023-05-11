from run_server import worker, buildServer, initDatabase

def main():
    s = buildServer()
    initDatabase()
    #uncomment below to use multiprocessing and delete worker(s, con) - test it
    worker(s) #implementation in run_server.py
    s.close()
    return

if __name__ == "__main__":
    main()