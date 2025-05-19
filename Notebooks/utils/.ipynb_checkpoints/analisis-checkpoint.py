import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

'''
Consideraciones:
- Se considera que el target es una variable binaria
- Se considera una variable discreta numerica como una categorica (categorica ordinal)
  
Tenemos 3 funciones:

- EDA_graf_categoricas: Nos da 2 graficas, la primera es una grafica de conteo sobre las categorias de la variable, la segunda es una grafica de los procentajes de default (TARGET) sobre cada categoria de la variable, ademas el  valor top_n indica la maxima cantidad de categorias a mostrar en cada clase, las categorias sobrantes se agruparan en una nueva con el nombre 'otros'

- EDA_graf_numericas : Nos da 2 graficas, la primera es la distribucion de la variable numerica, la segunda son 2 distribuciones para cada segmento 'cumplen' y 'no incumplen'.

- graficar_EDA_target : Apartir de una lista de variables, se escoge cualquiera de las 2 funciones anteriores para graficarlas, dependiendo de su tipo, si es categorica se usa la variable max_cat que se le pasara como parametro a la funcion EDA_graf_categoricas como vimos anteriormente.

'''



# Grafica para variables categorica y target binario
def EDA_graf_categoricas_target(
    df_,
    target: str,
    variable: str,
    top_n: int = None,      # si no se pasa, muestra todas las clases
    null_label: str = 'Nulo'
):
    """
    Grafica:
      - countplot de la variable categórica (top_n + 'otros')
      - barplot del % de 1s por cada categoría (misma lógica de top_n + 'otros')
    """
    # 1) Prepara la columna
    df = df_.copy()
    df[variable] = df[variable].fillna(null_label).astype(str)
    
    # 2) Calcula conteos y orden de "top_n"
    counts = df[variable].value_counts()
    if top_n and counts.size > top_n:
        principales = counts.iloc[:top_n].index.tolist()
        # mapeo a "otros" para el resto
        df['__cat__'] = df[variable].where(df[variable].isin(principales), other='otros')
    else:
        principales = counts.index.tolist()
        df['__cat__'] = df[variable]
    
    # 3) Orden alfabético (oponible: quieres mantener orden de frecuencia?)
    orden = df['__cat__'].unique()
    
    # 4) % de 1s por categoría
    proporciones = (
        df
        .groupby('__cat__')[target]
        .mean()
        .reindex(orden)
        .values
    )
    
    # 5) Dibuja
    fig, axes = plt.subplots(1, 2, figsize=(12,5))
    sns.set_style('whitegrid')
    
    # 5a) Countplot
    sns.countplot(
        data=df,
        x='__cat__',
        order=orden,
        ax=axes[0]
    )
    axes[0].set_title('Frecuencia por categoría')
    axes[0].set_xlabel(variable)
    axes[0].tick_params(axis='x', rotation=90)
    
    # 5b) Barplot de proporciones
    sns.barplot(
        x=orden,
        y=proporciones,
        ax=axes[1]
    )
    axes[1].set_title('% de 1s por categoría')
    axes[1].set_xlabel(variable)
    axes[1].tick_params(axis='x', rotation=90)
    linea_ref = axes[1].axhline(
        y=df[target].mean(),
        color='red',
        linestyle='--',
        label=f'% global = {df[target].mean():.3f}'
    )
    
    handles, labels = axes[1].get_legend_handles_labels()
    # Llamas a legend indicando ese handle
    axes[1].legend(
        handles=[linea_ref],
        loc='upper right'
    )
    
    plt.tight_layout()
    plt.show()
    
# Grafica para variables numericas y target binario
def EDA_graf_numericas_target(df_,target,variable):
    """
    Grafica:
      - Distribucion de la variable numerica sin contar el 0.1% restante (outliers)
      - Distribucion de la variable para cada segmento del TARGET sin contar el 0.1% restante (outliers).
    """
    
    df = df_.dropna(subset=variable)
    df.reset_index(inplace=True)
    p_99 =df[variable].quantile(0.999)
    df = df.query(f'{variable}<{p_99}')
    
    df_0 = df.query(f'{target}==0')[variable]
    df_1 = df.query(f'{target}==1')[variable]
    
    f,ax = plt.subplots(1,2)
    f.set_size_inches(9,4)
    sns.set_style('whitegrid')

    sns.distplot(df[variable],hist=False,color='black',kde=True,ax=ax[0])
    sns.distplot(df_0,hist=False,color='green',kde=True,ax=ax[1],label='cumplen')
    sns.distplot(df_1,hist=False,color='red',kde=True,ax=ax[1],label='incumplen')
    ax[1].legend()
    
    f.suptitle(f'Distribucion 99.5%',fontsize=18)
    plt.show()

# Graficas para un target binario
def graficar_EDA_target(df,target,variables,max_cat=8):
    for variable in variables:
        if df[variable].dtype=='O' or df[variable].nunique()<10:
            EDA_graf_categoricas_target(df_=df,target=target,variable=variable,top_n=max_cat)
        else:
            EDA_graf_numericas_target(df,target,variable)
            
# Descripcion de variables categoricas
def describe_categoricas(df_,variables,hide=False):

    df = df_.copy()
    df.fillna('nulo',inplace=True)
    cantidades = []
    porcentajes = []
    index1 = []
    index2 = []
    
    for var in variables:
        i_1 =  [var]*df[var].nunique()
        i_2 = list(df[var].value_counts().index)

        # Conteo de las clases de la variable
        valores = df[var].value_counts()
        valores_conteo = list(valores.values)

        # Porcentajes de las clases de la variable
        valores_per = valores/sum(valores)
        valores_porcentaje = list(valores_per.values)

        # Si hide!=False y el numero de variables es mayor que el indicado -> entra
        if df[var].nunique()>hide and hide:
            # Cambiamos los indices
            i_1 = i_1[:hide+1]
            i_2 = i_2[:hide] + ['otros']
            
            # Sumamos los conteos
            otros_conteo = sum(valores_conteo[hide+1:]) 
            otros_porcentaje = sum(valores_porcentaje[hide+1:])

            # Guardamos en valores_conteo y modificamos el ultimo con la suma de los que quedaron
            valores_conteo = valores_conteo[:hide] + [otros_conteo]
            valores_porcentaje = valores_porcentaje[:hide] + [otros_porcentaje]

        # Concatenamos a las listas 
        index1 += i_1
        index2 += i_2
        cantidades += valores_conteo
        porcentajes += valores_porcentaje

    # Le damos formato
    cantidades = np.array(cantidades).astype('int')
    porcentajes = [x+'%' for  x in np.round(np.array(porcentajes)*100,3).astype('str')]

    # definimos la tabla para crear el dataframe
    tabla = {'porcentaje': porcentajes,
             'cantidad': cantidades,
             'clases': index2}
    tabla = pd.DataFrame(tabla,index=index1)

    # Editamos para tener 2 indices
    tabla = tabla.set_index('clases',append=True)
    
    return tabla    