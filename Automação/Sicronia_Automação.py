
import serial #comunicação do Python e do arduino/ESP32
import pyvisa #comunicação do Python com o detector de potência via drivers da VISA
import matplotlib.pyplot as plt #Para plotar os gráficos
import time #usaremos para esperar alguns segundos.
import csv

#Altere seus valores para a configuração correta de seu experimento.

PortaESP32='COM3'
VelocidadeTransmissao=115200
PM100D_ENDERECO=  #INFORME SEU ENDEREÇO VISA DO SEU INSTRUMENTO DE MEDIÇÃO AQUI!!!!!!!!!!!!!
NumeroDeMedidas=200
MilimetroPorPasso=1.0
PosicaoInicial=0
ComprimentoDeOnda=633

#criaremos agora duas rotinas, uma para o experimento e uma para a plotagem dos gráficos:

def experimento():
    distancia = [] #criamos duas listas para armazenar os valores das medições.
    potencia = []

    print("Iniciando experimento...")
    '''Aqui iremos conectar o programa ao arduino, sendo port(conexão USB Com o computador), baudrate deverá ser a MESMA que o nosso
    programa em arduino, timeout é o tempo de espera para a leitura máximo'''
   
    esp32=serial.Serial(port=PortaESP32, baudrate=VelocidadeTransmissao, timeout=15)
    time.sleep(2)#tempo para a conexão ficar estabilizada.
    print("OK - Conexão estabelecida com a ESP32")
    esp32.reset_input_buffer()
    rm=pyvisa.ResourceManager() #faz uma varredura no sistema Op. em busca de equipamentos compatíveis com o padrão VISA.

    MedidorDePotencia =rm.open_resource(PM100D_ENDERECO) #variável que representa o nosso equipamento.
    #agora iremos configurar nosso medidor de potência, utilizando a linguagem SCPI:
    MedidorDePotencia.write(f'SENS:POW:RANGE:AUTO 1') #configuramos o range do nosso medidor.
    MedidorDePotencia.write(f'SENS:POW:CORR:WAV {ComprimentoDeOnda}') #configuramos o comprimento de onda do detector.
    print(f'CONECTADO AO MEDIDOR DE POTÊNCIA.')
    
    #MEDIÇÃO
    print("Iniciando medições: ")
    for i in range (NumeroDeMedidas):
        distanciaPercorrida=PosicaoInicial+(i*MilimetroPorPasso)
        print(f'Medida de {i+1}/{NumeroDeMedidas}: ')
        esp32.write(b'P\n')  #Estamos enviando a ESP32, P em formato de byte)
        resposta_raw = esp32.readline()
        confirmado = resposta_raw.decode('utf-8', errors='ignore').strip() #irá decodificar para o python a mensagem do arduino IDE.
        if "OK" in confirmado:
            time.sleep(2)
            print("Fazendo a leitura...")
            Potencia_Str = MedidorDePotencia.query('MEAS:POW?') #Pergunta ao medidor de potência sua potência e escreve em strings
            Potencia_float = float(Potencia_Str) #transforma strings em um número de fato.
            print(f'Potência medida: {Potencia_float:.4e}W')
            distancia.append(distanciaPercorrida)#armazena nossos valores de distância para montagem do gráfico
            potencia.append(Potencia_float)#armazena nossos valores de potência para montagem do gráfico

            #INTERRUPÇÃO PELOS MINI-SWITCHS
        elif "Voltando" in confirmado or "INICIO" in confirmado:
            print(f'{confirmado} Chave acionada')
            break
        else:
            print(f"Erro Inesperado. Resposta recebida da ESP32: '{confirmado}' (Bytes crus: {resposta_raw})")
            break
    print("Coleta de dados finalizada!")
    print("Dados coletados.")
#Fechando as conexões.
    esp32.close()
    print('Esp 32 encerrada')
    MedidorDePotencia.close()
    print('medidor de potência encerrado')
    salvar_csv("dados_experimento.csv", distancia, potencia)
    return distancia, potencia #garantimos que nossos equipamentos estão fechados e coletamos os valores por eles medidos.
    #GUARDA OS ARQUIVOS:

def salvar_csv(Graficoprofundidadecampo, distancia, potencia):
    if not distancia or not potencia:
        print("Nenhum dado para salvar no CSV.")
        return
    with open(Graficoprofundidadecampo, mode="w", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["Distancia_mm", "Potencia_W"])  # cabeçalho
        for d, p in zip(distancia, potencia):
            escritor.writerow([d, p])
    print(f"Dados salvos em {Graficoprofundidadecampo}")

#Plotagem do gráfico

def grafico(x_data, y_data):
    if not x_data or not y_data: #se alguma das listas vinher vazia terá valor logico F, então not x_data, passaria a ter valor lógico V
        print("Nenhum dado. Portanto, não é possível plotar o gráfico.")
        return # Se os dados estiverem vazios, não irá continuar.

    plt.figure(figsize=(12, 7))
    plt.plot(x_data, y_data, 'bo-', markersize=3)
    plt.title('Potência  vs. Distância $d_1$')
    plt.xlabel('Distância, $d_1$ (mm)')
    plt.ylabel('Potência (W)')
    plt.legend()
    plt.grid(True)
    if x_data:
        plt.xlim(min(x_data), max(x_data))
    plt.show()
if __name__ == "__main__":
    distancias_coletadas, potencias_coletadas = experimento()

    if distancias_coletadas and potencias_coletadas: #Este if servirá para quando nosso programa não tiver valor algum, [] não travar.
        print("Gerando o gráfico...")
        grafico(distancias_coletadas, potencias_coletadas)
    else:

        print("\nNenhum dado foi coletado. O gráfico não será gerado.")
