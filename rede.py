from operator import le
import re
import platform
import os

def validar_direccion_ip(ip):
    regex = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(3[0-2]|[1-2]?[0-9])$"
    if re.match(regex, ip):
        return True
    else:
        return False



class Subredes():
    def __init__(self, ip):
        self.sufijo =int(ip.split("/")[1])

        self.mascaraB = self._getMacara(self.sufijo)

        self.redB= self._getRed(ip.split("/")[0])


        
    def __str__(self):
        return f"Red: {self.red}/{self.sufijo}, host: {self.hosts}  Máscara: {self.mascara}"

        
    def _getMacara(self,sufijo): 
        mascara="00000000000000000000000000000000"
        for i in range(int(sufijo)):
            mascara= mascara. replace("0","1",1)

        mascaraB=["","","",""]
        for i in range(4):
            mascaraB[i]= mascara[:8]
            mascara=mascara.replace(mascaraB[i],"",1)


        return mascaraB
    
    def _getRed(self,red):
        redD=[0,0,0,0]
        i=0

        for octeto in red.split("."):
            redD[i]=  int(octeto)
            i+=1

        redB=["","","",""]
        i=0

        for bi in redD:
            redB[i]=f"{bi:08b}" #bin(bi).replace("0b","")
            i+=1

        return redB


    @property
    def red(self):
        return ".".join(map(str,self.binariodecimal(self.redB)))

    @property
    def mascara(self):
        return ".".join(map(str,self.binariodecimal(self.mascaraB)))
   
    @property
    def hosts(self):
        return 2**(32-self.sufijo)-2


    def binariodecimal(self,red:list[str]):
        redD=[0,0,0,0]
        for i in range(4):
            redD[i]= int(red[i],2)
        
        return redD

    def subredes_sufijo(self,sufijo:int)->list:
        dif = sufijo-self.sufijo
        print(f"calcular subrede ")

        nNesubredes = 2**dif
        redes=[]
        for i in range(0,nNesubredes):
            iB = self._decimal_a_binario_con_n_bits(i,dif)
            auxsubred= self._reemplazar_rango("".join(self.redB),self.sufijo,sufijo,iB)
            auxsubred=self._dividir_cadena_en_segmentos(auxsubred)
            auxsubred=self.binariodecimal(auxsubred)
            
            subred =".".join(map(str,auxsubred))
            subred=Subredes(f'{subred}/{sufijo}')
            redes.append(subred)

        return redes
    
    def subredes_subredes(self,subre:int):
        bistP = f"{(subre-1):b}"
        sufijo =self.sufijo+len(bistP)

        if sufijo>30:
            raise "formato no valido"

        return self.subredes_sufijo(sufijo)

    def subredes_host(self,hosts:int):
        bits =f"{hosts:b}"
        sufijo = 32-len(bits)
        
        return self.subredes_sufijo(sufijo)

    def generar_configurasion(self):
        last_hos = self.get_hosts().pop()
        print(f"Red: {self.red}")
        print("Configurar interfaz")
        print(f"""
        interface GigabitEthernet <interfaz>
        ip addres {last_hos} {self.mascara}
        no shutdown 
        """)

        print("\nConfigurar dhcp")
        print(f"""
        ip dhcp pool <nombre>
        network {self.red} {self.mascara}
        default-router {last_hos}
        dns-server <ip_servidor_dns>
        ip dhcp excluded-address {last_hos}
        """)
        
    
    def get_hosts(self):
        bits_tomados = len(f"{self.hosts:b}")
        red = "".join(self.redB)

        host =[]
        for h in range(1,self.hosts+1):
            hb=self._decimal_a_binario_con_n_bits(h,bits_tomados)
            new_hos=self._reemplazar_rango(red,self.sufijo,bits_tomados+self.sufijo,hb)
            new_hos= self._dividir_cadena_en_segmentos(new_hos)
            host.append(".".join(map(str,self.binariodecimal(new_hos))))

        return host

    def _decimal_a_binario_con_n_bits(self,numero_decimal, n):
        # Paso 1: Convierte el número decimal a binario
        binario = bin(numero_decimal)[2:]  # La [2:] elimina el prefijo '0b' de la representación binaria
        
        # Paso 2: Agrega ceros a la izquierda si es necesario
        longitud_actual = len(binario)
        if longitud_actual < n:
            ceros_faltantes = n - longitud_actual
            binario = '0' * ceros_faltantes + binario
        
        return binario
    
    def _reemplazar_rango(self,cadena, inicio, fin, reemplazo):
        # Dividir la cadena en tres partes
        parte1 = cadena[:inicio]
        parte2 = reemplazo
        parte3 = cadena[fin:]
        
        # Concatenar las partes
        resultado = parte1 + parte2 + parte3
        
        return resultado

    def _dividir_cadena_en_segmentos(self,cadena:str)->list[str]:
        segmentos = []
        for i in range(0, len(cadena), 8):
            segmento = cadena[i:i+8]
            segmentos.append(segmento)
        return segmentos





def menuinicial():
    clear()
    print(f"Ingrese una direccion de red \n ejemplo 192.168.74.0/24\n")
    direccion_ip =input("Ingrese la Red >>  ")
    
    red =Subredes(direccion_ip)
    accion=0
    
    while True:
        clear()
        print("que desae relizar obtener subredes:  \npor sufijo de Red : 0\npor N Redes: 1\npor N host: 2\nueva red: 3\nmostrar configuracion: 4")
        accion=input(">>  ")
        if accion=='0':
            clear()
            sufijo=input("Cual es el sufijo de red >>  ")
            
            redes=red.subredes_sufijo(int(sufijo))
            cont=0
            for re in redes:
                print(f"{cont} {re}")
                cont+=1

            input()
        elif accion =='1':
            clear()
            subredes=input("cantidad de redes a generar >>  ")
            
            redes=red.subredes_subredes(int(subredes))
            cont=0
            for re in redes:
                print(f"{cont} {re}")
                cont+=1

            input()
        elif accion =='2':
            clear()
            host=input("cantidad de host por red >>  ")
            
            redes=red.subredes_host(int(host))
            cont=0
            for re in redes:
                print(f"{cont} {re}")
                cont+=1

            input()
        elif accion =='3':
            clear()
            print(f"Ingrese una direccion de red \n ejemplo 192.168.74.0/24\n")
            direccion_ip =input("Ingrese la Red >>  ")
            
            red =Subredes(direccion_ip)
        elif accion=='4':
            red.generar_configurasion() 
            input()

        else:
            break


def clear():

    # Obtener el nombre del sistema operativo
    sistema_operativo = platform.system()

    # Comprobar si es Windows
    if sistema_operativo == "Windows":
        os.system("cls")
    else:
        os.system("clear")


if __name__ == "__main__":
    menuinicial()
