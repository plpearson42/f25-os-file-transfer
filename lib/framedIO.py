#!/usr/bin/env python3 

import os

class BufferedReader(): 
    def __init__(self, fd, bufSize=1024):
        self.fd = fd
        self.bufSize = bufSize
        self.buffer = b""
        self.index = 0


    def _fillBuffer(self):
        data = os.read(self.fd, self.bufSize)
        if not data:
            return False
        self.buffer = data
        self.index = 0
        return True


    def read(self, nBytes):
        output = bytearray()
        while nBytes > 0:
            if self.index >= len(self.buffer):
                if not self._fillBuffer():
                    break
            start = self.index
            end = self.index + min(nBytes, len(self.buffer) - self.index)
            output.extend(self.buffer[start:end])
            self.index = end
            nBytes -= end - start
        return bytes(output)


    def close(self):
        os.close(self.fd)


            
             

class BufferedWriter():
    def __init__(self, fd, bufSize=4096):
        self.fd = fd
        self.bufSize = bufSize
        self.buffer = bytearray(bufSize) 
        self.index = 0

    def _writeByte(self, byte):
        self.buffer[self.index] = byte
        self.index += 1
        if self.index >= self.bufSize:
            self._flush()

    def _flush(self):
        start = 0
        while start < self.index:
            start += os.write(self.fd, self.buffer[start:self.index])
        self.index = 0

    

    def write(self, data):
        for byte in data:
            self._writeByte(byte)
        self._flush() 

    def close(self):
        self._flush()
        os.close(self.fd)


"""
takes files and frames them in a bytestring
"""
class FramedReader():
    def __init__(self, bufSize=1024):
        self.bufSize = bufSize
        self.escChar = b"~" 
        self.MAXREAD = 2**30  # max file size 1GB

    def read(self, fileList):
        output = bytearray()

        for title in fileList:
            output.extend(title.encode() + self.escChar + b"e")

            fd = os.open(title, os.O_RDONLY)

            br = BufferedReader(fd, self.bufSize)
            data = br.read(self.MAXREAD)
            br.close()

            for byte in data:
                if byte == ord(self.escChar):
                    output.extend(self.escChar + self.escChar)
                else:
                    output.append(byte)

            output.extend(self.escChar + b"e")

        return bytes(output)  # return bytestring from output bytearray


"""
takes framed bytestring and writes to files
"""
class FramedWriter():
    def __init__(self, bufSize=4096):
        self.bufSize = bufSize
        self.escChar = b"~"
        
    def write(self, data):
        context = 0  # 0:title, 1:data
        escaped = False
        buffer = bytearray()
        currentTitle = b""

        for byte in data:
            if escaped:
                if byte == ord(self.escChar):
                    buffer.append(byte)
                elif byte == ord(b"e"):
                    if not context:
                        currentTitle = bytes(buffer)
                        buffer.clear()
                    else:
                        fd = os.open(currentTitle, os.O_WRONLY | os.O_CREAT)
                        bw = BufferedWriter(fd, self.bufSize)
                        bw.write(bytes(buffer))
                        bw.close()
                        buffer.clear()

                    context = not context
                escaped = False
                continue

            if byte == ord(self.escChar):
                escaped = True
                continue

            buffer.append(byte)
            
