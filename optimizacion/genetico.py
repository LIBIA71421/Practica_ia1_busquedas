import random
from typing import List, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor

class AlgoritmoGenetico:
    def __init__(self, tam_poblacion: int, tam_cromosoma: int, 
                 prob_cruce: float = 0.8, prob_mutacion: float = 0.1, 
                 sigma_mutacion: float = 0.5):
        self.tam_poblacion = tam_poblacion
        self.tam_cromosoma = tam_cromosoma
        self.prob_cruce = prob_cruce
        self.prob_mutacion = prob_mutacion
        self.sigma_mutacion = sigma_mutacion
        self.poblacion = self._inicializar_poblacion()

    def _inicializar_poblacion(self) -> List[Tuple[float, ...]]:
        poblacion = []
        for _ in range(self.tam_poblacion):
            # Inicialización aleatoria entre -1 y 1
            individuo = tuple(random.uniform(-1.0, 1.0) for _ in range(self.tam_cromosoma))
            poblacion.append(individuo)
        return poblacion

    def seleccion_torneo(self, fitnesses: List[float], k: int = 3) -> Tuple[float, ...]:
        torneo = random.sample(range(self.tam_poblacion), k)
        mejor_idx = max(torneo, key=lambda idx: fitnesses[idx])
        return self.poblacion[mejor_idx]

    def cruce_aritmetico(self, p1: Tuple[float, ...], p2: Tuple[float, ...]) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        if random.random() < self.prob_cruce:
            alpha = random.random()
            h1 = tuple(alpha * p1[i] + (1 - alpha) * p2[i] for i in range(self.tam_cromosoma))
            h2 = tuple((1 - alpha) * p1[i] + alpha * p2[i] for i in range(self.tam_cromosoma))
            return h1, h2
        return p1, p2

    def mutacion_gaussiana(self, individuo: Tuple[float, ...]) -> Tuple[float, ...]:
        mutado = list(individuo)
        for i in range(self.tam_cromosoma):
            if random.random() < self.prob_mutacion:
                mutado[i] += random.gauss(0, self.sigma_mutacion)
                # Mantener o no en límites? Generalmente los pesos no tienen límites estrictos,
                # pero normalizarlos ayuda. Limitaremos a [-10, 10] por seguridad.
                mutado[i] = max(-10.0, min(10.0, mutado[i]))
        return tuple(mutado)

    def ejecutar(self, evaluar_fitness: Callable[[Tuple[float, ...]], float], generaciones: int):
        mejores_por_gen = []
        historial = {'mejor_fitness': [], 'prom_fitness': []}
        
        for gen in range(generaciones):
            # Evaluar población en paralelo para agilizar
            with ThreadPoolExecutor() as executor:
                fitnesses = list(executor.map(evaluar_fitness, self.poblacion))
            
            mejor_fitness = max(fitnesses)
            mejor_individuo = self.poblacion[fitnesses.index(mejor_fitness)]
            prom_fitness = sum(fitnesses) / self.tam_poblacion
            
            print(f"Generación {gen+1}/{generaciones} | Mejor: {mejor_fitness:.3f} | Promedio: {prom_fitness:.3f}")
            mejores_por_gen.append((mejor_individuo, mejor_fitness))
            historial['mejor_fitness'].append(mejor_fitness)
            historial['prom_fitness'].append(prom_fitness)
            
            # Elitismo: guardamos al mejor
            nueva_poblacion = [mejor_individuo]
            
            while len(nueva_poblacion) < self.tam_poblacion:
                p1 = self.seleccion_torneo(fitnesses)
                p2 = self.seleccion_torneo(fitnesses)
                h1, h2 = self.cruce_aritmetico(p1, p2)
                h1 = self.mutacion_gaussiana(h1)
                h2 = self.mutacion_gaussiana(h2)
                nueva_poblacion.append(h1)
                if len(nueva_poblacion) < self.tam_poblacion:
                    nueva_poblacion.append(h2)
                    
            self.poblacion = nueva_poblacion
        
        mejor = max(mejores_por_gen, key=lambda x: x[1])
        return mejor[0], mejor[1], historial
