# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 21:21:18 2025

@author: Kevin
"""

import random
import tkinter as tk

# Algoritmo Evolutivo
def random_chromosome(nq):
    """Genera una permutación 0..nq-1 (una reina por columna y fila)."""
    return random.sample(range(nq), nq)


def pair_attacks(chrom):
    """Cuenta pares de reinas que se atacan en diagonal."""
    attacks = 0
    n = len(chrom)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(chrom[i] - chrom[j]) == abs(i - j):
                attacks += 1
    return attacks


def fitness(chrom):
    """Fitness: mayor = mejor. Máximo = número total de pares no atacantes."""
    n = len(chrom)
    max_pairs = n * (n - 1) // 2
    return max_pairs - pair_attacks(chrom)


def tournament_selection(pop, k):
    """Selecciona el mejor entre k individuos al azar."""
    contenders = random.sample(pop, k)
    return max(contenders, key=fitness)


def order_crossover(a, b):
    """Order Crossover (OX) para permutaciones."""
    n = len(a)
    if n < 2:
        return a[:]
    i, j = sorted(random.sample(range(n), 2))
    child = [-1] * n
    # copiar segmento de a
    child[i:j + 1] = a[i:j + 1]
    pos = (j + 1) % n
    # rellenar con el orden de b
    sequence = b[(j + 1) % n:] + b[:(j + 1) % n]
    for val in sequence:
        if val not in child:
            child[pos] = val
            pos = (pos + 1) % n
    return child


def swap_mutation(chrom, mutation_prob):
    """Swap mutation: intercambia dos posiciones con probabilidad mutation_prob."""
    child = chrom[:]
    if random.random() < mutation_prob:
        i, j = random.sample(range(len(child)), 2)
        child[i], child[j] = child[j], child[i]
    return child


def genetic_run(nq, pop_size, mut, k, elit, maxgen, stag, update_callback=None):
    """
    Ejecuta el GA y escribe el log en consola en el formato pedido.
    Devuelve: (best_chrom, generations, solved_bool, best_fitness)
    """
    max_pairs = nq * (nq - 1) // 2
    pop = [random_chromosome(nq) for _ in range(pop_size)]

    best = max(pop, key=fitness)
    best_score = fitness(best)
    stagnation = 0

    print(f"[GA] inicio: best_score={best_score}/{max_pairs}")

    for gen in range(1, maxgen + 1):
        pop_sorted = sorted(pop, key=fitness, reverse=True)
        new_pop = [c[:] for c in pop_sorted[:elit]]

        while len(new_pop) < pop_size:
            p1 = tournament_selection(pop, k)
            p2 = tournament_selection(pop, k)
            child = order_crossover(p1, p2)
            child = swap_mutation(child, mut)
            new_pop.append(child)

        pop = new_pop
        current_best = max(pop, key=fitness)
        current_score = fitness(current_best)

        if current_score > best_score:
            best = current_best[:]
            best_score = current_score
            stagnation = 0
            print(f"[GA] gen {gen}: mejora best_score={best_score}/{max_pairs}")
        else:
            stagnation += 1

        if callable(update_callback):
            update_callback(gen, best, best_score)

        if best_score == max_pairs:
            print("\nResultado final:")
            print(f"  n = {nq}")
            print(f"  Generaciones ejecutadas = {gen}")
            print("  Solución óptima encontrada = True")
            print(f"  Cromosoma (col -> fila) = {best}")
            return best, gen, True, best_score

        if stagnation >= stag:
            print(f"[GA] estancamiento en gen {gen}, mejor={best_score}/{max_pairs}")
            print("\nResultado final:")
            print(f"  n = {nq}")
            print(f"  Generaciones ejecutadas = {gen}")
            print("  Solución óptima encontrada = False")
            print(f"  Cromosoma (col -> fila) = {best}")
            return best, gen, False, best_score

    # si se agotan las generaciones
    print("\nResultado final:")
    print(f"  n = {nq}")
    print(f"  Generaciones ejecutadas = {maxgen}")
    print(f"  Solución óptima encontrada = {(best_score == max_pairs)}")
    print(f"  Cromosoma (col -> fila) = {best}")
    return best, maxgen, (best_score == max_pairs), best_score



class NQueensGUI:
    def __init__(self, root):
        self.root = root
        root.title("N-Reinas - Algoritmo Evolutivo")

        # Parámetros
        params = tk.Frame(root)
        params.pack(padx=6, pady=6)

        labels = [
            "N", "Población", "Mutación", "Torneo k",
            "Elitismo", "Max Gen", "Estancamiento"
        ]
        defaults = ["8", "60", "0.06", "3", "1", "2000", "400"]
        self.entries = {}
        for i, (lab, val) in enumerate(zip(labels, defaults)):
            tk.Label(params, text=lab).grid(
                row=i // 2, column=(i % 2) * 2, sticky="e", padx=3, pady=2
            )
            e = tk.Entry(params, width=8)
            e.insert(0, val)
            e.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=3, pady=2)
            self.entries[lab] = e

        # Botón único: Ejecutar GA
        btns = tk.Frame(root)
        btns.pack(pady=6)
        tk.Button(btns, text="Ejecutar Algoritmo Genético", command=self.run_ga).grid(
            row=0, column=0, padx=5
        )

        # Estado
        self.label_status = tk.Label(root, text="Listo", anchor="w")
        self.label_status.pack(pady=4)

        # Tablero
        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack(padx=8, pady=8)

    def draw_board(self, chrom):
        nq = len(chrom)
        size = min(500, 40 * nq)
        cell = size // nq
        self.canvas.config(width=size, height=size)
        self.canvas.delete("all")

        for r in range(nq):
            for c in range(nq):
                color = "#f0d9b5" if (r + c) % 2 == 0 else "#b58863"
                self.canvas.create_rectangle(
                    c * cell, r * cell, (c + 1) * cell, (r + 1) * cell,
                    fill=color, outline="black"
                )

        for col, row in enumerate(chrom):
            x = col * cell + cell // 2
            y = row * cell + cell // 2
            self.canvas.create_text(x, y, text="♛", font=("Arial", max(8, cell // 2)), fill="black")

    def run_ga(self):
        # leer parámetros
        nq = int(self.entries["N"].get())
        pop_size = int(self.entries["Población"].get())
        mut = float(self.entries["Mutación"].get())
        k = int(self.entries["Torneo k"].get())
        elit = int(self.entries["Elitismo"].get())
        maxgen = int(self.entries["Max Gen"].get())
        stag = int(self.entries["Estancamiento"].get())

        # callback visual (cada 10 generaciones actualiza tablero)
        def update_cb(gen, best, best_f):
            if gen % 10 == 0:
                self.draw_board(best)
                self.label_status.config(text=f"Gen {gen} - Fitness {best_f}")
                self.root.update_idletasks()

        # ejecutar GA 
        best, gens, solved, best_f = genetic_run(
            nq, pop_size, mut, k, elit, maxgen, stag, update_callback=update_cb
        )

        # resultado final 
        self.draw_board(best)
        if solved:
            self.label_status.config(text=f"Solución encontrada en {gens} gen! (fitness={best_f})")
        else:
            self.label_status.config(text=f"No óptimo tras {gens} gen. (fitness={best_f})")


if __name__ == "__main__":
    root = tk.Tk()
    app = NQueensGUI(root)
    root.mainloop()
