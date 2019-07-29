# ## Teste de Conexão Servidor

# Script adaptado de: https://github.com/yantisj/tcpping/blob/master/tcpping.py

import sys
import socket
import time
import signal
import timeit


class Tping:

    '''
Testa de ping em um determinado servidor definido na inicialização
instancia.
                        Modo de usar
    gooPing = Tping()
    gooPing.__ini__(host='www.google.com.br')
    gooPing.mediaPing()
    gooPing.resutado()

    '''
    def __ini__(self, host, port=80, maxCount=25, count=0, passed=0, failed=0, soma_ping=0):
        self.host = host
        self.port = port
        self.maxCount = maxCount
        self.count = count
        self.passed = passed
        self.failed = failed
        self.soma_ping = soma_ping
        while self.count < self.maxCount:
        
            # Increment Counter
            self.count += 1
            success = False

            # New Socket
            s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)

            # 1sec Timeout
            s.settimeout(1)

            # Start a timer
            s_start = timeit.default_timer()

            # Try to Connect
            try:
                s.connect((self.host, int(self.port)))
                s.shutdown(socket.SHUT_RD)
                success = True

            # Connection Timed Out
            except socket.timeout:
                print("Connection timed out!")
                failed += 1
            except OSError as e:
                print("OS Error:", e)
                failed += 1

            # Stop Timer
            s_stop = timeit.default_timer()
            s_runtime = "%.2f" % (1000 * (s_stop - s_start))

            if success:
                print("Conexão com %s[%s]: tcp_seq=%s time=%s ms" % (self.host, self.port, (self.count-1),s_runtime))
                passed += 1
                # ajuste feito para calcular a média do ping (s_runtime)
                soma_ping += float(s_runtime)

            # Sleep for 1sec
            if self.count < self.maxCount:
                timeit.time.sleep(1)

        self.count += count
        self.passed += passed
        self.failed += failed
        self.soma_ping += soma_ping

    def mediaPing(self):
        if self.passed > 0: 
            return round(self.soma_ping/self.passed,2)
        else:
            return 0

    def resutado(self):
        print("\nResultados TCP Ping: Conexões (Total/Passou/Falhou):"
            "[{:}/{:}/{:}] (Falhou: {:}%)".format((self.count),self.passed,self.failed,round(self.failed/(self.count)*100)),'\n')
