# Many credits to Christopher Piekarski, who wrote the code which I heavily
#  patterned this setup after. See his work at:
# https://cpiekarski.com/2011/05/09/super-easy-python-json-client-server/
import socket
import struct



class UDPServer(object):
    def __init__(self, send_to_address='10.17.36.2', send_to_port=5800):
        # we use UDP to send information from the BBB to the roborio, because speed
        #  is far more important than deterministic data transfer.
        # SOCK_DGRAM indicates UDP (instead of TCP)
        # Note address and port must match what the robot Java code is configured
        #  to listen on.
        # Per the FMS whitepaper, we have ports 5800 through 5810 available, so we'll pick 5800 as default
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conn = self.socket
        self._timeout = None
        self._address = send_to_address
        self._port = send_to_port

    def sendString(self, msg):
        if isinstance(msg, str):
            msg = str.encode(msg)

        if self.socket:
            frmt = "=%ds" % len(msg)
            packedMsg = struct.pack(frmt, msg)
            self._send(packedMsg)

    def _send(self, msg):
        sent = 0
        while sent < len(msg):
            sent += self.conn.sendto(msg[sent:],(self._address, self._port))

    def close(self):
        print("closing main socket")
        self._closeSocket()
        if self.socket is not self.conn:
            print("closing connection socket")
            self._closeConnection()

    def _closeSocket(self):
        self.socket.close()

    def _closeConnection(self):
        self.conn.close()

    def _get_timeout(self):
        return self._timeout

    def _set_timeout(self, timeout):
        self._timeout = timeout
        self.socket.settimeout(timeout)

    def _get_address(self):
        return self._address

    def _get_port(self):
        return self._port

# Main code, which is used as a test environment
if __name__ == "__main__":
    import TargetObservation
    print("Starting basic server JSON test...")

    testServer = UDPServer(send_to_address="127.0.0.1",send_to_port = 5800)
    testData = TargetObservation.TargetObservation()
    #testData.addTarget(1,2,3,4,5)
    testData.addTarget(6,7,8,9,10)
    testData.addTarget(11,12,13,14,15)
    testData.addTarget(0,0,0,0,0)
    testData.setMetadata(5,0.8,0.2,0.3,28.5)

    # I watch the results of this on wireshark
    testServer.sendString(testData.toJsonString())
    #testServer.sendString("{malformed blarg blarg}")


    print("Basic server JSON test completed")
