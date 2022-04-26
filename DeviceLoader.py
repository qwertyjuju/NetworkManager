import time
import re
import serial
from logger import log


class SerialDisplay:
    def __init__(self, display):
        self.display = display
        self.display.setReadOnly(0)

    def add(self):
        pass

"""
SerialInterface
"""


class SerialInterface:
    def __init__(self, port_com: str):
        self._ser = serial.Serial(
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            write_timeout=1,
            xonxoff=1,
            timeout=1)
        self._ser.port = port_com
        self.loopnb = 0
        self._ser.open()
        log("info", "serial opened")
        self.initialised = 0
        print(self._ser.inWaiting())
        regex = re.compile("^(\w+[#>])$")
        while not self.initialised:
            last_line = self.write_command()
            if "[yes/no]:" in last_line:
                self.write_command("no")
                out = self.write_command()
                print("out", out)
            elif regex.search(last_line) is not None:
                    print("init complete")
                    self.initialised = 1
        """
        while not self.initialised:
            line=self.write_command()
            if line:
                print(line)
            if "[yes/no]:" in line:
                self.write_command("no")
            if line[-1:] in [">", "#"]:
                self.initialised = 1
        """
    def write_command(self, command: str = None, sleeptime: int = 1):
        out = ""
        command = "\r" if not command else command+"\r"
        self._ser.write(command.encode("utf-8"))
        time.sleep(sleeptime)
        while self._ser.inWaiting()>0:
            out+= str(self._ser.read(self._ser.inWaiting()).decode("utf-8").lower())
        print(self.loopnb, repr(out))
        self.loopnb+=1
        return out

    def write_commands(self, commands: list):
        for command in commands:
            self.write_command(command)

    def print_line(self):
        print(self._ser.readline())

    def loop(self):
        print(self.write_command("ena"))
        print(self.write_command("reload"))
        print(self.write_command())

    def get_mode(self):
        pass

    def close(self):
        """
        Permet de fermer la connexion entre l'hôte et la machine
        :return:
        """
        self._ser.close()

    def line(self):
        """
        Permet d'afficher la dernière ligne. Fonction d'affichage
        :return: La dernière ligne
        """
        return self._ser.readline()


if __name__ == "__main__":
    t = SerialInterface("COM7")
    t.loop()


"""
DUMP



        while not self.initialised:
            self._ser.write(b'\n')
            nbbytes = self._ser.inWaiting()
            print(nbbytes)
            if nbbytes > 0:
                line = str(self._ser.read(nbbytes).decode("utf-8").lower().replace('\r\n',""))
                print(type(line), line)
                if "[yes/no]:" in line:
                    self.write_command("no")
                if line[-1:] in [">", "#"]:
                    self.initialised = 1
            self._ser.reset_input_buffer()
            time.sleep(0.5)
            
            
        while not self.initialised:
            self._ser.break_condition = 1
            self._ser.write(b'\n')
            line = self._ser.readline().decode("utf-8").lower().replace('\r\n',"")
            self._ser.break_condition = 0
            log("info", "console output: ", line)
            if "[yes/no]:" in line:
                self.write_command("no")
            if line[-1:] in [">", "#"]:
                self.initialised = 1
            else:
                print(self._ser.readline().decode("utf-8").lower().replace('\r\n',""))
                print("no")
            time.sleep(1)
            
        self._ser.readline().decode("utf-8").lower().replace('\r\n',"")
"""
