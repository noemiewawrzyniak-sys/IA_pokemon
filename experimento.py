import random, statistics as st, time
import busca_local as bl

N_EXEC = 30
SEEDS = range (100, 100 + N_EXEC)
ALGOS = [
    ("Hill Climbing", lambda rng: bl.hill_climbing(rng)),
    ("Random-Restart HC (10x)", lambda rng: bl.random_restart_hill_climbing(rng, 10)),
    ("SA (alfa = 0.9, ~200000it.)", lambda rng: bl.simulated_annealing(rng, T0=10.0, Tmin=0.01, alfa=0.90, iter_por_T=3000)),
]

def main():
    print(f"{N_EXEC} execucoes por algoritmo (sementes {SEEDS.start}..{SEEDS.stop - 1})\n")
    print(f"{'Algoritmo':<26}{'melhor':>10}{'media':>11}{'desvio':>9}{'pior':>10}{'#=melhor':>10}{'#inviav.':>10}{'t/exec':>8}")
    melhor_global, c_global = None, float("inf")
    for nome, fn in ALGOS:
        custos, t0 = [], time.time()
        for s in SEEDS:
            sol, c = fn(random.Random(s))
            custos.append(c)
            if c < c_global: melhor_global, c_global = sol, c
        t = (time.time() - t0) / N_EXEC
        ok = [c for c in custos if c != float("inf")]
        melhor = min(ok)
        n_melhor = sum(abs(c - melhor) < 1e-6 for c in ok)
        print(f"{nome:<26}{melhor:>10.4f}{st.mean(ok):>11.4f}{st.pstdev(ok):>9.4f}{max(ok):>10.4f}"
              f"{n_melhor:>7}/{len(ok):<3}{N_EXEC - len(ok):>7}/{N_EXEC}{t:>7.2f}s")
        print("\nMelhor solucao encontrada:\n")
        bl.relatorio(melhor_global)

if __name__ == "__main__":
    main()