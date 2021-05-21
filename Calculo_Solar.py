# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 08:59:03 2021

@author: peyopro94
"""

import requests
import pandas as pd

def NASA (lon,lat):
    try:
        print('Buscando data en Power NASA...')
        API="https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py?&request=execute&identifier=SinglePoint&parameters=SI_EF_TILTED_SURFACE&userCommunity=SB&tempAverage=CLIMATOLOGY&outputList=JSON&lat={}&lon={}".format(lon,lat)
        response = requests.get(API)
    
        #Transformando en dataframe
        
        data=response.json()['features'][0]['properties']['parameter']
        df=pd.DataFrame.from_dict(data)
        index=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre','Año']
        df['MES']=index
        
        #Calculo HSP Minima del sistema
        a=df.loc[:,['SI_EF_OPTIMAL','SI_EF_OPTIMAL_ANG']].rename(columns=
                                                         {'SI_EF_OPTIMAL':'HR. GLOBAL'
                                                         ,'SI_EF_OPTIMAL_ANG':'ANGULO OPTIMO' }).T
        a.columns=index
        a['Unidad']=['kW-hr/m^2/day','Grados']
        HP_min=df['SI_EF_OPTIMAL'].min()
        print('Datos encontrados en Power NASA!')
        return HP_min
        
    except:
        print ('Error, no conexión a POWER NASA')
        return "Error"

def pot_sistema (P,h):  
    """Calcula la potencia AC que hay que alimentar"""
    Egen= P*h
    return Egen

def vol_sis (Egen):
    if Egen<=200:
        v_sis=12
        return v_sis
    elif Egen>200 and Egen<=4000:
        v_sis=24
        return v_sis
    elif Egen>4000:
        v_sis=48
        return v_sis
    
def perdidas (n_r,n_inv,n_x,**kwargs):
    """Calcula las perdidas por equipos"""
    n_t=n_r*n_inv*n_x
    for kwargs in kwargs:
        n_t=n_t*kwargs
    return n_t

def n_panles(Wp,Hp_min,Egen,n_t):
    """Calculo de numeros paneles necesarios
    
    Wp= Watts pico del panel (fabrica)
    Hp_min: Hora pico Minima del lugar"""
    
    E_panel=Wp*Hp_min

    f_sp=1.2
    n_tp=f_sp*(Egen/(E_panel*(1-(1-n_t)-0.05)))
    return n_tp

def rad_men(o,HP_min0):
    """Calcula la radiación solar media mensual del sistema en un angulo de funcionamiento
    Donde:
    o=angulo de orientación de los paneles, en °
    HP_min0= Radiación diaria solar media mensual en el angulo 0°, en kW-hr/m^2/day
    """
    GA=HP_min0/(1-(4.46*10^-4*o)*(1.19*10^-4*o^2))
    return GA

"""
while True:
    lon=float(input('Ingrese longitud: '))
    lat= float(input('Ingrese Latitud: '))
    print("")
    
    #Información NASA
    
    HP_min=NASA(lon,lat)

    bat=str(input("¿El sistema requiere baterias? y/n :"))
    
    #Potencia del sistema
    
    P=float(input("\nPotencia alimentar el sistema (W): "))
    h=float(input("Horas de funcionamiento: "))
    
    Egen=pot_sis(P,h)
       
    #Estimación de perdidas
    print("\nLas eficiencias por defecto son:")
    
    if bat=='y':
        print("n_r=0.95       Eficiencia del regulador")
        print("n_inv=0.90     Eficiencia del inversor")
        print("n_b=0.90       Eficiencia de las baterías litio")
        print("n_x= 0.97      Eficiencia por otras pérdidas")
        print("f_c=0.05       Factor de contingencia")
        eff_input=str(input("\n¿Desea modificarlo? y/n: "))
        if eff_input =="y":
            n_r=float(input("Eficiencia del regulador: "))       
            n_inv=float(input("Eficiencia del inversor: "))  
            n_b=float(input("Eficiencia de las baterías litio: "))      
            n_x=float(input("Eficiencia por otras pérdidas: ")) 
            f_c=float(input("Factor de contingencia: ")) 
        elif eff_input=='n':
            n_r=0.95       
            n_inv=0.90     
            n_b=0.90       
            n_x= 0.97      
            f_c=0.05   
            print("Se mantienen valores por defecto")
        n_t=perdidas(n_r,n_inv,n_x,n_b)
    elif bat=='n': 
        print("n_r=0.95       Eficiencia del regulador")
        print("n_inv=0.90     Eficiencia del inversor")
        print("n_x= 0.97      Eficiencia por otras pérdidas")
        print("f_c=0.05       Factor de contingencia")
        eff_input=str(input("\n¿Desea modificarlo? y/n: "))
        if eff_input =="y":
            n_r=float(input("Eficiencia del regulador: "))       
            n_inv=float(input("Eficiencia del inversor: "))  
            n_x=float(input("Eficiencia por otras pérdidas: ")) 
            f_c=float(input("Factor de contingencia: ")) 
        elif eff_input=='n':
            n_r=0.95       
            n_inv=0.90     
            n_x= 0.97      
            f_c=0.05   
            print("Se mantienen valores por defecto")
        n_t=perdidas(n_r,n_inv,n_x)
    print ('\n-->Las perdidas son: {}%. Teniendo factor de contigencia {}%: {}%'.format(round(n_t*100,2),
                                                                               round((f_c)*100,2),
                                                                               round((n_t-f_c)*100,2)))
    #Voltaje del sistema
    
    if Egen<=200:
        v_sis=12
    elif Egen>200 and Egen<=4000:
        v_sis=24
    elif Egen>4000:
        v_sis=48

    print('-->El voltaje seleccionado para el sistema es: {} V'.format(v_sis))
     
    v_input=str(input("¿Desea Cambiarlo? (y/n): "))

    if v_input=='y':
        v_sis=int(input("Ingrese voltaje de diseño del sistema (Vdc): "))
    else:
        pass
           
    #Dimensionamiento

    #Paneles
    t3="\nDimensionamiento de Paneles"
    print(t3)
    print("----------------------")

    w_p= int(input("Potencia del panel a usar, Wp: "))

    n_tp=n_panles(w_p,HP_min,Egen,n_t,f_c)
    
    ##Baterias

    if bat =='y':
        t1="\nDimensionamiento de Baterias"
        print(t1)
        print("----------------------")
        
        eff_bat=float(input("Ingrese eficiencia de la bateria: "))
        v_bat=float(input("Ingrese voltaje de la bateria,V: "))
        cap=float(input("Ingrese capacidad de la bateria,Ah: "))
        Pdes=float(input("Ingrese profundidad de descarga de la bateria: "))
        
        Bah=(Egen/eff_bat)/v_sis
        print('-->El sistema consume {} Ah/d'.format(round(Bah,2)))
        
        print("\nBaterias en serie")
        bat_serie=np.ceil(v_sis/v_bat)
        print("-->Se necesitan {} baterias en serie".format(np.ceil(bat_serie)))
        
        print("\nBaterias en paralelo")
        Aut=float(input("Ingrese dias de autonomia del sistema: "))
        bat_paralelo=np.ceil(Bah*Aut/Pdes/cap)
        print("-->Se necesitan {} baterias en paralelo".format(np.ceil(bat_paralelo)))
        
        print("\nTotal de Baterias")
        print("-->Se necesitan {} baterias".format(np.ceil(bat_paralelo*bat_serie)))
    else:
        pass
    
    #Inversor
    t2="\nDimensionamiento inversor"
    print(t2)
    print("----------------------")
    
    P_sim=P*1.2
    PF=float(input("Ingresar PF del sistema: "))
    S_inv=P_sim/PF
    print("\n-->El tamaño del inversor debe ser: {} kVA".format(np.ceil(S_inv/1000)))
    
    
    ##Cerrar programa
    cont=str(input("\n¿Desea reiniciar el programa?(y/n): "))
    if cont=="y":
        continue
    elif cont=="n":
        print("-->Cerrando Programa")
        time.sleep(2)
        break
    """