# botentry
A binance day trading bot

Primer entrenamiento con Algoritmo Genético (ag) exitoso.

Se observan las medias móviles de 7, 25 y 99 periodos (verde, naranja y azul) , los primeros 8 valores del cálculo del retroceso de fibonacci (lineas rectas), las compras realizadas(triángulo rojo) y las ventas (triángulo verde), los puntos azules son los stop loss para cada tiempo, cada stop loss se calcula restando un % a la compra y aumenta en cada tiempo nuevo (tanto el porcentaje como el aumento son variables que se asignan antes de correr el ag, en este caso es 0.02 o 2% para el stop_loss y el aumento es del 1% cada t). Cuando el stoploss intersecta con el precio hay una venta.

La función para calcular el fitness del ag es la suma de la multiplicación de cada una de las variables por una constante codificada "gen" en el "dna" de cada individuo del ag, el dna tiene varios genes y se codifica en binario siendo el símil de las bases nitrogenadas el 0 y el 1. El dna por ejemplo puede ser 0111011101 donde cada n dígitos hay un gen (genotipo) que codifica a un número real (fenotipo) en un intervalo dado. Las variables son las segundas derivadas del filtro gaussiano aplicado al precio de apertura con distintas sigmas, para obtener los puntos críticos en distintas temporalidades. 

Sean las segundas derivadas del filtro gaussiano aplicado al precio: dg_1, dg_2 ... dg_n
Y las constantes que codifica el algoritmo genético: cg_1, cg_2 ...cg_n

La función principal es: f = f(dg_1, ..., dg_n) = dg_1*cg_1 + ... + dg_n *cg_n

Posterior a eso el ag compra cuando la pendiente es cercana a cero viniendo de un comportamiento ascendente en f (que es cuando tentativamente hay un mínimo local en el precio), esto se calcula con la regresión lineal en un intervalo de tiempo anterior al actual (se va recorriendo el arreglo de fechas para f), se compra y se fijan los stop loss. El score o variable a optimizar es la ganancia al final del recorrido de todas las fechas, entre más monedas gane más probabilidad tendrá de reproducirse cada individuo del ag, heredando así su dna a un hijo que tendra la mezcla del dna del padre y la madre y será sometido a mutaciones.

Para este entrenamiento se empezó con 5000 usd y se tuvo una ganancia de 754 usd en 4 días en periodos de 15 minutos para cada vela. En porcentaje es un profit de cerca del 15%.

Esto es solo con el ag, falta agregar la información que dan los demás indicadores en distintas temporalidades; el volumen, los fibos, las ema, las ma, las tendencias lineales, las bandas de bollinger, etc. para realizar la menor cantidad de compras en zonas comprometedoras y hacer scalping solo cuando la tendencia principal es favorable.
