# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 08:20:14 2022

@author: uiad.analisis
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

nombres = np.array((
    ['A',True],
    ['B',False],
    ['C',True],
    ['D',True],
    ['E',False],
    ['F',False],
    ['G',True]
    ))
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.choice.html

def the_chosen_one(nombres, tipo = "k", valor = 1.05, imp_datos = True):
    """
    

    Parameters
    ----------
    nombres : np.array
        An array containing participant names and whether there must be a "consideration".
        Consideration must be entry as True of Flase statements.
    
    tipo: str with two posible values {"k", "ptj_v"}
        -k can be interpreted as how many times the probability of beeing chosen increments compared with 
            a fare lotery.
        -ptj_v is the advantage (in %) that someone with "some consideration" has over someone without "consideration"
        
        k : int or float, optional
            k is the constant that adds "consideration" to the selected participants
                If  k>=0 and k<1       --> Negative "consideration" is given to selected participants.
                If k=1                 --> No "consideration" is given to selected participants.
                If k>1 and k<=N/(N-Ns) --> Positive "consideration" is given.
            
            Where k has the following constraint:
                k>=0 and k<=N/(N-Ns)
        
        ptj_v : float, optional
            ptj_v  is the advantage that selected participants have over non selected participants.
            ptj_v = (p_v/p_s)-1
            
            In this case:
                pv = ps*(1+ptj_v)
            and ps comes from:
                ps*Ns + pv*Nv*(1+ptj_v) = 1
                ps = 1/(Ns+Nv*(1+ptj_v))
            
            Where ptj_v has the following contraint:
                -1 <= ptj_v <= (1/(ps*Nv)-1) = (1/((1/(Ns+Nv*(1+ptj_v)))*Ns)-1)
    
    valor: float
        The value related to the "tipo" parameter.
   imp_datos: bool, optional
       Set to True to print information about the process.
       
    Computation
        N = Nv + Ns   --> Where N is the number of participants, 
                          Nv is the number of participants with "some consideration"
                          and Ns are the number of participants without "some consideration".
       
        p = 1/N       --> Is the probaility that each participant is picked if no "consideration"
                          was taken into account.
                          
        pv = p*k      --> Is the probability that each participant with "consideration" is picked.
       
       Thus, it has to be the case that:
           
           pv*Nv + (1-pv*Nv) = 1  --> Where pv*Nv is the probability that someone with "consiederation" is picked
                                      and  (1-pv*Nv) is the probability that some one without "consideration" is picked.
       
        This results in the following expression:
            
        ps = (1-pv*Nv)/Ns --> Where ps is the probability that someone without "consideration" is picked.
        
        In order for the second axiom of probabilities to hold (sum(p)=1). It must be the case that:
        
        0 <= pv*Nv <= 1
        0 <= (1/N)*k*(N-Ns) <= 1
        0 <= k <= N/(N-Ns)
            
    Returns 
    -------
    the_chosen_one: "Name of the chosen one"

    """
    
    
    if nombres.shape[1]!=2:
        raise ValueError(f"Array shape must be (N,2), where N is the number of participants. {nombres.shape} was given")

    participantes = pd.DataFrame(nombres, columns = ['Nombre','Ventaja'])
    
    datos_unicos = np.sort(participantes['Ventaja'].unique())
    
    if  participantes['Ventaja'].nunique()>2 :
        raise Exception(f"Two unique values expected as considerarion. {participantes['Ventaja'].unique()} were given.")
    
    valores_posibles = np.array(("True", "False"))
    if participantes['Ventaja'].nunique()==2 and any([datos_unicos[i]!=np.sort(valores_posibles)[i] for i in range(len(valores_posibles))]):
        raise Exception(f'The values for "consideration" must be True or False. {datos_unicos} was given.')
    elif participantes['Ventaja'].nunique()==1 and participantes['Ventaja'].unique()[0] not in ["True", "False"]:
        raise Exception(f'The values for "consideration" must be True or False. {datos_unicos} was given.')
    
    
    if len(datos_unicos)==1:
        print("The process was excuted with only one category")
        the_chosen_one = np.random.choice(
            a = participantes['Nombre'].values
            )
        return the_chosen_one
    n = participantes['Nombre'].nunique()
    n_s = len(participantes[participantes['Ventaja']=='False'])
    n_v = len(participantes[participantes['Ventaja']=='True'])
    
    if n != len(participantes):
        raise Exception(f"There are {n} unique participants. However, {len(participantes)} were given.")
    
    if tipo not in ['k','ptj_v']:
        raise Exception(f'tipo takes no value "{tipo}". Allowed values are ["k","ptj_v"]')
    
        
    if tipo == 'k':
        if (valor<0) or ( valor>(n/(n-n_s)) ):
            raise Exception(f"k is expected to have values between 0 and {n/(n-n_s)} (N/(N-Ns)). {valor} was given")
    if tipo == 'ptj_v':
        if (valor<-1) or (valor>(1/((1/(n_s+n_v*(1+valor)))*n_s)-1)):
            raise Exception(f"ptj_v is expected to have values between -1 and {(1/((1/(n_s+n_v*(1+valor)))*n_s)-1)} ((1/((1/(Ns+Nv*(1+ptj_v)))*Ns)-1)). {valor} was given")

    if tipo == 'k':
        p_v = valor/n            
        p_s = (1-n_v*p_v)/n_s
    else:
        p_s = 1/(n_s+n_v*(1+valor))
        p_v = p_s*(1+valor)
    
    participantes['W'] = np.nan
    participantes.loc[participantes['Ventaja']=='True','W'] = p_v
    participantes.loc[participantes['Ventaja']=='False','W'] = p_s
    
    the_chosen_one = np.random.choice(
        a = participantes['Nombre'].values, 
        p =  participantes['W'].values
        )
    
    
    if  tipo == 'k' and valor == n/(n-n_s):
        print('Only the participants with "some consideration" where considered in this process.')
    elif tipo == 'k':
        print(f"The process was executed with k={valor} which is equivalent to {(p_v/p_s-1)*100}% as advange to selected participants")
    elif tipo=='ptj_v' and valor == n_s/(n-n_s):
        print('Only the participants with "some consideration" where considered in this process.')
    elif tipo=='ptj_v':
        print(f"The process was executed with ptj_v={valor}")
            
        
    return the_chosen_one 



def lunch_list(nombres, tipo = "k", valor = 1.05, imp_datos = True):
    
    los_nombres = nombres.copy()
    la_lista = []
    for ene in range(nombres.shape[0]):
        
        df_nombres = pd.DataFrame(los_nombres, columns = ['Nombre','Ventaja'])
        el_elegido = the_chosen_one(df_nombres.values, tipo = tipo, valor = valor, imp_datos=imp_datos)
        la_lista.append(el_elegido)
        df_nombres = df_nombres[df_nombres['Nombre']!=el_elegido]
        los_nombres = df_nombres.values
    return la_lista
        
valor = 0.5
tipo = 'ptj_v'
imp_datos = True

save_r = []
for c in range(1,1_000):
    result = the_chosen_one(nombres, tipo = tipo , valor = valor)
    save_r.append(result)

df_r = pd.DataFrame(save_r)

df_r.value_counts().plot(kind='bar')

lunch_list(nombres, tipo = tipo , valor = valor)

