import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Parámetros
CW = 1.85
LARGO_VERTEDERO = 1.0
GRAVEDAD = 9.81

LARGO_RESERVORIO = 100.0
#LARGO_RESERVORIO = 500.0

ANCHO_RESERVORIO = 75.0
#ANCHO_RESERVORIO = 12.0

AREA_RESERVORIO = LARGO_RESERVORIO * ANCHO_RESERVORIO
PASO_TIEMPO = 1 * 3600  # Paso de tiempo en segundos (1 hora)

Hd_RESERVORIO = 15.0
#Hd_RESERVORIO = 20.0
#Hd_RESERVORIO = 2.0

DISCRETIZACION = 0.25
# Leer datos de caudal ingresante (Qin) del archivo
data = np.loadtxt('Qin.txt', skiprows=1)
HORA = data[:, 0]
Qin = data[:, 1]
PATH_SOLUCION_ANALITICA = "solucion_analitica.txt"

# Inicializar variables
VOLUMEN_INICIAL = 0.0  # Volumen inicial
H_INICIAL = 0.0  # Nivel de agua inicial
Qout_INICIAL = 0.0  # Caudal saliente inicial


# Simulación usando método de Euler de primer orden
def resolver_euler(tiempo, lista_volumenes, lista_niveles, lista_Qouts, lista_Qin, lista_factores_amplificacion, discretizacion):
    H = H_INICIAL
    V = VOLUMEN_INICIAL
    delta_t = PASO_TIEMPO * discretizacion
    for i in range(1, len(lista_Qin)):

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
        lista_volumenes.append(int(V))
        lista_niveles.append(round(H,2))
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
        for i in range(len(Qin)):
            for j in range(int(discretizacion**-1)):
                lista_Qin.append(Qin[i])
    else:
        lista_Qin = Qin
    return lista_Qin

def crear_lista_horas(discretizacion):
    lista_horas = []
    if discretizacion > 1:
        for i in range(0, len(HORA), discretizacion):
            lista_horas.append(HORA[i])
    elif (discretizacion < 1):
        for i in range(len(HORA)):
            for j in range(int(discretizacion**-1)):
                lista_horas.append(HORA[i] + discretizacion * j)
    else:
        lista_horas = HORA
    return lista_horas

def leer_vector_desde_archivo(nombre_archivo, lista_volumenes_solucion_analitica):

    try:
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                numero = int(linea.strip())  # Lee cada línea y convierte a número
                lista_volumenes_solucion_analitica.append(numero)
        print(f"Se ha leído el vector desde el archivo '{nombre_archivo}'")
        return lista_volumenes_solucion_analitica
    except IOError as e:
        print(f"No se pudo leer desde el archivo '{nombre_archivo}': {e}")
        return None
    except ValueError as e:
        print(f"Error al convertir los datos en '{nombre_archivo}': {e}")
        return None


def crear_lista_horas_sexagesimal(lista_horas):
    lista_horas_sexagesimal = []
    for i in range(len(lista_horas)):
        horas = int(lista_horas[i])
        minutos = int((lista_horas[i] - horas) * 60)
        lista_horas_sexagesimal.append(f"{horas:02d}:{minutos:02d}")
    return lista_horas_sexagesimal

# Convertir resultados a DataFrame para mejor visualización
def convertir_a_dataframe(lista_horas, Qin, Qouts, lista_volumenes, lista_niveles, lista_factores_amplificacion, lista_errores_truncamiento):
    lista_horas_sexagesimal = crear_lista_horas_sexagesimal(lista_horas)
    result_df = pd.DataFrame({
        'Tiempo [hr]': lista_horas_sexagesimal,
        'Qin [m3/s]': Qin,
        'Qout [m3/s]': Qouts,
        'Nivel de agua [m]': lista_niveles,
        'Volumen de agua [m³]': lista_volumenes,
        'Facor de Amplificacion': lista_factores_amplificacion,
        'Error de Truncamiento': lista_errores_truncamiento
    })
    return result_df

def convertir_a_dataframe_volumenes(lista_horas,lista_volumenes, lista_volumenes_sol_analitica, lista_errores_truncamiento):
    lista_horas_sexagesimal = crear_lista_horas_sexagesimal(lista_horas)
    result_df = pd.DataFrame({
        'Tiempo [hr]': lista_horas_sexagesimal,
        'Vol sol error [m³]': lista_volumenes,
        'Vol sol analitica [m³]': lista_volumenes_sol_analitica,
        'Error de Truncamiento': lista_errores_truncamiento
    })
    return result_df
def mostrar_data_frame(result_df):
    print("\n \n")

    # Mostrar el DataFrame completo
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.colheader_justify', 'center')
    pd.set_option('display.precision', 2)

    print(result_df)
    print("\n \n")
    return 0

def graficar_nivel_agua(lista_volumenes, lista_niveles, lista_horas):
    # Graficar resultados
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(lista_horas, lista_niveles, label='Nivel de agua (H)')
    plt.axhline(y=Hd_RESERVORIO, color='r', linestyle='--', label='Nivel del reservorio (Hd)')
    plt.xlabel('Tiempo [hr]')
    plt.ylabel('Nivel de agua [m]')
    plt.xticks(np.linspace(min(lista_horas), max(lista_horas), 13), np.arange(0, 49, 4))
    plt.legend()
    plt.grid()

    plt.subplot(2, 1, 2)
    plt.plot(lista_horas, lista_volumenes, label='Volumen de agua (V)')
    plt.axhline(y=Hd_RESERVORIO * AREA_RESERVORIO, color='r', linestyle='--', label='Nivel del reservorio (Hd)')
    plt.xlabel('Tiempo [hr]')
    plt.ylabel('Volumen de agua [m³]')
    plt.xticks(np.linspace(min(lista_horas), max(lista_horas), 13), np.arange(0, 49, 4))
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()
    return 0

def arreglar_lista_volumenes_solucion_analitica(discretizacion, lista_volumenes_solucion_analitica):
    lista_arreglada_volumenes_solucion_analitica = []

    for i in range(0, len(lista_volumenes_solucion_analitica),int(discretizacion * 60)):
        lista_arreglada_volumenes_solucion_analitica.append(lista_volumenes_solucion_analitica[i])
    return lista_arreglada_volumenes_solucion_analitica

def calclcular_errores_truncamiento(lista_volumenes, lista_volumenes_solucion_analitica, lista_errores_truncamiento):
    for i in range(len(lista_volumenes)):
        if lista_volumenes_solucion_analitica[i] != 0:
            error = round(abs(lista_volumenes[i] - lista_volumenes_solucion_analitica[i]) / lista_volumenes_solucion_analitica[i], 2)
        else :
            error = 0
        lista_errores_truncamiento.append(error)
    return 0


def calcular_error_truncamiento_promedio(errores_truncamiento):
    promedio_error = sum(errores_truncamiento) / len(errores_truncamiento)

    print(f"El promedio de error de truncamineto es de {promedio_error * 100:.2f}%")
    return 0


def main ():

    volumenes = [VOLUMEN_INICIAL]
    niveles_agua = [H_INICIAL]
    Qouts = [Qout_INICIAL]
    Qins = crear_lista_Qin(DISCRETIZACION)
    horas = crear_lista_horas(DISCRETIZACION)
    factores_amplificacion = [0]
    volumenes_solucion_analitica = []
    errores_truncamiento = []

    leer_vector_desde_archivo(PATH_SOLUCION_ANALITICA, volumenes_solucion_analitica)
    volumenes_solucion_analitica = arreglar_lista_volumenes_solucion_analitica(DISCRETIZACION, volumenes_solucion_analitica)

    resolver_euler(horas, volumenes ,niveles_agua, Qouts, Qins, factores_amplificacion, DISCRETIZACION)

    calclcular_errores_truncamiento(volumenes, volumenes_solucion_analitica, errores_truncamiento)

    data_frame1 = convertir_a_dataframe(horas, Qins, Qouts, volumenes, niveles_agua, factores_amplificacion, errores_truncamiento)
    data_frame2 = convertir_a_dataframe_volumenes(horas, volumenes, volumenes_solucion_analitica ,errores_truncamiento)
    mostrar_data_frame(data_frame1)
    mostrar_data_frame(data_frame2)

    calcular_error_truncamiento_promedio(errores_truncamiento)

    graficar_nivel_agua(volumenes, niveles_agua, horas)


main()