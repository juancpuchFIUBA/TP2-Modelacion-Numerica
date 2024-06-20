import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Parámetros
CW = 1.85
LARGO_VERTEDERO = 1.0
GRAVEDAD = 9.81
LARGO_RESERVORIO = 100.0
ANCHO_RESERVORIO = 75.0
AREA_RESERVORIO = LARGO_RESERVORIO * ANCHO_RESERVORIO
PASO_TIEMPO = 1 * 3600  # Paso de tiempo en segundos (1 hora)
Hd_RESERVORIO = 15.0
DISCRETIZACION = 1/240
# Leer datos de caudal ingresante (Qin) del archivo
data = np.loadtxt('Qin.txt', skiprows=1)
HORA = data[:, 0]
Qin = data[:, 1]

# Inicializar variables
VOLUMEN_INICIAL = 0.0  # Volumen inicial
H_INICIAL = 0.0  # Nivel de agua inicial
Qout_INICIAL = 0.0  # Caudal saliente inicial


# Simulación usando método de Euler de primer orden
def resolver_euler(tiempo, lista_volumenes, lista_niveles, lista_Qouts, lista_Qin, lista_factores_amplificacion, discretizacion):
    H = H_INICIAL
    V = VOLUMEN_INICIAL
    delta_t = PASO_TIEMPO * discretizacion

    for i in range(len(lista_Qin) - 1):

        Qin_Ahora = lista_Qin[i]
        # Calcular Qout basado en el nivel de agua H
        if H <= Hd_RESERVORIO:
            Qout = 0.0
        else:
            h = H - Hd_RESERVORIO
            Qout = (2 / 3) * CW * LARGO_VERTEDERO * np.sqrt(2 * GRAVEDAD) * h ** (3 / 2)


        # Actualizar volumen y nivel de agua
        V = V + delta_t * (Qin_Ahora - Qout)
        H = V / AREA_RESERVORIO

        # Verificar si el nivel de agua excede el máximo permitido


        # Una vez lleno, el nivel de agua no puede bajar de 15 m
        if H < Hd_RESERVORIO and lista_niveles[-1] >= Hd_RESERVORIO:
            H = Hd_RESERVORIO
            V = H * AREA_RESERVORIO

        # Se calcula el factor de amplificacion para analizar estabilidad
        g = calcular_factor_amplificacion(V, delta_t)

        lista_factores_amplificacion.append(g)
        lista_volumenes.append(V)
        lista_niveles.append(H)
        lista_Qouts.append(Qout)
    return 0

def calcular_factor_amplificacion(volumen_agua, delta_t):
    if (volumen_agua > Hd_RESERVORIO * AREA_RESERVORIO):
        factor_amplificacion = 1 - delta_t * (1/3) * CW * np.sqrt(2 * GRAVEDAD) * LARGO_VERTEDERO * (((volumen_agua/AREA_RESERVORIO) - Hd_RESERVORIO) ** (1/2)) * (1/AREA_RESERVORIO)
    else:
        factor_amplificacion = 1
    return abs(factor_amplificacion)

def crear_lista_Qin(discretizacion):
    lista_Qin = []
    if discretizacion > 1:
        for i in range(0, len(Qin), discretizacion):
            lista_Qin.append(Qin[i])

    elif (discretizacion < 1):
        for i in range(len(Qin) - 1):
            paso_qin = (Qin[i+1] - Qin[i]) * discretizacion
            for j in range(int(discretizacion**-1)):
                lista_Qin.append(Qin[i] + paso_qin * j)
        lista_Qin.append(Qin[i+1])
    else:
        lista_Qin = Qin
    return lista_Qin

def crear_lista_horas(discretizacion):
    lista_horas = []
    if discretizacion > 1:
        for i in range(0, len(HORA), discretizacion):
            lista_horas.append(HORA[i])
    elif (discretizacion < 1):
        for i in range(len(HORA) - 1):
            for j in range(int(discretizacion**-1)):
                hora = HORA[i] + discretizacion * j
                lista_horas.append(hora)
    else:
        lista_horas = HORA

    return lista_horas



def escribir_vector_a_archivo(vector, nombre_archivo):
    try:
        with open(nombre_archivo, 'w') as archivo:
            for numero in vector:
                archivo.write(f"{int(numero)}\n")
        print(f"Vector escrito en el archivo {nombre_archivo}.")
    except Exception as e:
        print(f"Error al escribir en el archivo: {e}")

def main ():

    lista_volumenes = [VOLUMEN_INICIAL]
    lista_niveles = [H_INICIAL]
    lista_Qouts = [Qout_INICIAL]
    lista_Qins = crear_lista_Qin(DISCRETIZACION)
    lista_horas = crear_lista_horas(DISCRETIZACION)
    lista_factores_amplificacion = [0]
    resolver_euler(lista_horas, lista_volumenes ,lista_niveles, lista_Qouts, lista_Qins, lista_factores_amplificacion, DISCRETIZACION)

    escribir_vector_a_archivo(lista_volumenes, "solucion_analitica.txt")
    return 0

main()