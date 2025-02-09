from syndesi.adapters import IP, Remote
from syndesi.tools.log import set_log_stream

def main():

    #set_log_stream(True, 'DEBUG')
    my_adapter = Remote(IP('pcsebastien'), IP('tcpbin.com', port=4242))

    output = my_adapter.query('Hello World\n')

    print(output)


if __name__ == '__main__':
    main()