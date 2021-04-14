import numpy as np
import random
import multiprocessing

# Genetic algorithm

class Individual:
    
    def __init__(self, _length, _mutation_intensity, _dna=None):
        self.length = _length
        self.mutation_intensity = random.randint(1, _mutation_intensity)
        self.dna = _dna if _dna else self.generate_individual() 
        self.score = 0
        
    def generate_individual(self):
        """Generate n bits strings individual
        
        :param nbits: String length simulating the bits quantity
        :type nbits: int
        
        """ 
        count = 0
        individual = ""
        while(count<self.length):
            individual += str(random.randint(0, 1))
            count += 1
        return individual
    
    def binary_to_decimal(self, a, b):
        """ Converts binary values into a decimal values with one comma, between 
        [a,b] interval
        
        :param bin: String binary value
        :type bin: String:
        :param a: Start interval
        :type a: int
        :param b: End interval
        :type b: int
        """
        n = self.length
        dec = 0
        for i in self.dna:
            if i=='1':
                dec+=2**(n-1)
            n-=1
        return  a+((dec)/(2**self.length-1))*(b-a)
    
    
    def mutation(self):
        bin = list(self.dna)
        for _ in range(int(len(bin)/random.randint(1, self.mutation_intensity))):
            rand=random.randint(0, self.length - 1)
            if(bin[rand]=="0"):
                bin[rand]="1"
            if(bin[rand]=="1"):
                bin[rand]="0"
        return "".join(bin)



class Population:
    
    def __init__(self, _quantity, _dna_length, _mutation_intensity):
        self.quantity = _quantity
        self.dna_length = _dna_length
        self.mutation_intensity = _mutation_intensity
        self.population = self.generate_population()
        self.score = 0
    
    def generate_population(self):
        population = []
        count = 0
        while(count < self.quantity):
            individual = Individual(self.dna_length, self.mutation_intensity)
            population.append(individual)
            count += 1
        return population
            
    def breed(self, bin1, bin2):
        """
        Reproduction function, cross the gen for two individuals, uniform cross.
        :param bin1: One individual
        """
        self.__order_by_individual_score()
        half = int(self.quantity/2)
        best_half = self.population[:half]
        ten_percent = int(self.quantity/10)
        best_ten_percent = self.population[:ten_percent]
        
        new_population = []
        fifty_percent = ten_percent * 5
        for _ in range(fifty_percent):
            mother = best_ten_percent[random.randint(0, ten_percent)]
            father = best_half[random.randint(0, half)]
            new_population.append(
                self.__cross_genes(
                    father,
                    mother
                )
            )
            
        self.population = best_half + new_population
            
    def __order_by_individual_score(self):
        self.population.sort(key=lambda individual: individual.score)

    def __cross_genes(self, father, mother):
        son_dna = ""
        for i in range(self.dna_length):
            rand=random.randint(0,1)
            if (rand==0):
                son_dna += father[i]
            else:
                son_dna += mother[i]
        son = Individual(self.dna_length, self.mutation_intensity, son_dna)
        son.mutation()
        return son


class GeneticAlgorithm:
    pass




"""Algoritmo de selección de mínimos, recibe una función de evaluación y una
   lista con individuos(cadenas de binarios) a evaluar, selecciona al 50% más
   apto, los reproduce y la descendencia remplaza al 50% menos apto"""

"""
def eval(x):
   return [f(x[0],x[1],x[2]),x[3],x[4],x[5],x[6]]

resultado = []

evaluaciones = []
def evolucion(a,b,t,individuosx,individuosy,individuost,iteraciones):
    global evaluaciones, resultado
    print("---------------------------------------------------------")
    if len(individuosx)!=len(individuosy)!=len(individuost):
        return "Las poblaciones iniciales deben tener la misma longitud."
    #Selección

    aEvaluar = []
    evaluacionRepetida = []

    for i in range(len(individuosx)):
        contiene = False
        for j in resultado:
            if (j[1]==individuosx[i] and j[2]==individuosy[i] and
                j[3]==individuost[i]):
                evaluacionRepetida.append([j[0], j[1], j[2], j[3], iteraciones])
                contiene = True
                print(binToDec(j[1],a,b), binToDec(j[2],a,b),
                      int(binToDec(j[3],0,t)), j[0])
                break

        if not contiene:
            aEvaluar.append([binToDec(individuosx[i],a,b),
                             binToDec(individuosy[i],a,b),
                             int(binToDec(individuost[i],0,t)),
                             individuosx[i],
                             individuosy[i],
                             individuost[i],
                             iteraciones])

    p = multiprocessing.Pool(4)
    evaluacionNoRepetida = p.map(eval, aEvaluar)

    evaluacion = evaluacionRepetida + evaluacionNoRepetida

    evaluacion.sort()

    for i in evaluacion:
        resultado.append(i)

    mejores50=evaluacion[:int(0.5*len(evaluacion))]
    #Reproducción
    hijos=[]
    mejores50bin=[]


    for i in range(len(mejores50)):
        mejores50bin.append([mejores50[i][1],mejores50[i][2],mejores50[i][3]])
        hijos.append([cruza(mejores50[random.randint(0,int(len(mejores50)/4)-1)][1],
                            mejores50[random.randint(0,int(len(mejores50)/4)-1)][1]),
                      cruza(mejores50[random.randint(0,int(len(mejores50)/4)-1)][2],
                            mejores50[random.randint(0,int(len(mejores50)/4)-1)][2]),
                      cruza(mejores50[random.randint(0,int(len(mejores50)/4)-1)][3],
                            mejores50[random.randint(0,int(len(mejores50)/4)-1)][3])])

    #Mutación, solo los hijos mutan.
    for i in range(int(len(hijos)/random.randint(1,4))):
        randx=random.randint(0,len(hijos)-1)
        hijos[randx][0]=mutacion(hijos[randx][0])

        randy=random.randint(0,len(hijos)-1)
        hijos[randy][1]=mutacion(hijos[randy][1])

        randt=random.randint(0,len(hijos)-1)
        hijos[randt][2]=mutacion(hijos[randt][2])


    #Junta a los padres y a los hijos
    nuevaGeneracion=(mejores50bin[:len(mejores50bin)/2]+
                     mejores50bin[:len(mejores50bin)-len(mejores50bin)/2]+
                     hijos)
    genx=[]
    geny=[]
    gent=[]
    for i in range(len(nuevaGeneracion)):
        genx.append(nuevaGeneracion[i][0])
        geny.append(nuevaGeneracion[i][1])
        gent.append(nuevaGeneracion[i][2])

    if(iteraciones==0):
        resultado.sort()
        decimales=[]
        for i in resultado:
            decimales.append([binToDec(i[1],a,b),binToDec(i[2],a,b),
                              int(binToDec(i[3],0,t)),i[0],i[4]])
        return decimales
    else:
        return  evolucion(a,b,t,genx,geny,gent,iteraciones-1)
"""