import math, random
import info as cfg

NOMES = list(cfg.PODER_POKEMON)
PODER = [cfg.PODER_POKEMON[n] for n in NOMES]
NP = len(NOMES)

GINASIOS = sorted(cfg.DIFICULDADE_GINASIO)
DIF = [cfg.DIFICULDADE_GINASIO[g] for g in GINASIOS]
NG = len(GINASIOS)
E = cfg.ENERGIA_INICIAL
SOMA = [sum(PODER[i] for i in range(NP) if m >> i & 1) for m in range (1 << NP)]
BITS = [[i for i in range(NP) if m >> i & 1] for m in range (1 << NP)]

def usos(sol):
    uso = [0] * NP
    for m in sol:
        for i in BITS[m]:
            uso[i] += 1
    return uso

def valida(sol):
    uso = usos(sol)
    return max(uso) <= E and min(uso) < E

def custo(sol):
    return sum(DIF[g] / SOMA[m] for g, m in enumerate(sol))


def solucao_aleatoria(rng):
    restante = [E] * NP
    restante[rng.randrange(NP)] = E - 1
    sol = []
    for _ in range(NG):
        p = rng.choice([i for i in range(NP) if restante[i] > 0])
        restante[p] -= 1
        sol.append(1 << p)
    return sol


def aplicar(sol, mov):
    nova = sol[:]
    for g, novo_gene in mov:
        nova[g] = novo_gene
    return nova

def movimento_aleatorio(sol, rng):
    tipo = rng.randrange(5)
    if tipo == 0:
        g = rng.randrange(NG);
        m = sol[g] ^ (1 << rng.randrange(NP))
        return [(g, m)] if m else None
    if tipo == 1:  # swap
        a, b = rng.sample(range(NG), 2)
        return [(a, sol[b]), (b, sol[a])] if sol[a] != sol[b] else None
    if tipo == 2:  # mover
        a, b = rng.sample(range(NG), 2);
        p = rng.randrange(NP)
        if not (sol[a] >> p & 1) or (sol[b] >> p & 1) or sol[a] == 1 << p: return None
        return [(a, sol[a] ^ (1 << p)), (b, sol[b] | (1 << p))]
    if tipo == 3:  # trocar
        g = rng.randrange(NG);
        p, q = rng.sample(range(NP), 2);
        m = sol[g]
        if not (m >> p & 1) or (m >> q & 1): return None
        return [(g, (m ^ (1 << p)) | (1 << q))]
    a, b = rng.sample(range(NG), 2)
    p, q = rng.sample(range(NP), 2)
    ma, mb = sol[a], sol[b]
    if not (ma >> p & 1) or (ma >> q & 1) or not (mb >> q & 1) or (mb >> p & 1):
        return None
    return [(a, (ma ^ (1 << p)) | (1 << q)), (b, (mb ^ (1 << q)) | (1 << p))]

def todos_movimentos(sol):
    for g in range(NG):
        for p in range(NP):
            m = sol[g] ^ (1 << p)
            if m: yield [(g, m)]  # flip
    for a in range(NG):
        for b in range(a + 1, NG):
            if sol[a] != sol[b]: yield [(a, sol[b]), (b, sol[a])]  # swap
    for a in range(NG):
        for b in range(NG):
            if a == b: continue
            for p in range(NP):
                if (sol[a] >> p & 1) and not (sol[b] >> p & 1) and sol[a] != 1 << p:
                    yield [(a, sol[a] ^ (1 << p)), (b, sol[b] | (1 << p))]  # mover
    for g in range(NG):
        for p in range(NP):
            for q in range(NP):
                if p != q and (sol[g] >> p & 1) and not (sol[g] >> q & 1):
                    yield [(g, (sol[g] ^ (1 << p)) | (1 << q))]  # trocar
    for a in range(NG):
        for b in range(a + 1, NG):
            for p in range(NP):
                for q in range(NP):
                    if p != q and (sol[a] >> p & 1) and not (sol[a] >> q & 1) \
                            and (sol[b] >> q & 1) and not (sol[b] >> p & 1):
                        yield [(a, (sol[a] ^ (1 << p)) | (1 << q)),
                               (b, (sol[b] ^ (1 << q)) | (1 << p))]  # cruzar

def simulated_annealing(rng, T0 = 10.0, Tmin = 0.01, alfa = 0.90, iter_por_T=3000):
    sol = solucao_aleatoria(rng)
    valor = -custo(sol)
    T = T0
    while T > Tmin:
        for _ in range(iter_por_T):
            mov = movimento_aleatorio(sol, rng)
            if mov is None: continue
            proximo = aplicar(sol, mov)
            if not valida(proximo): continue
            valor_proximo = -custo(proximo)
            dE = valor_proximo - valor
            if dE > 0 or rng.random() < math.exp(dE/T):
                sol, valor = proximo, valor_proximo
        T *= alfa
    return sol, custo(sol)

def hill_climbing(rng):
    sol = solucao_aleatoria(rng)
    c = custo(sol)
    while True:
        melhor_viz, c_viz = None, c
        for mov in todos_movimentos(sol):
            viz = aplicar(sol, mov)
            if not valida(viz): continue
            cv = custo(viz)
            if cv < c_viz - 1e-12:
                melhor_viz, c_viz = viz, cv
        if melhor_viz is None:
            return sol, c
        sol, c = melhor_viz, c_viz

def random_restart_hill_climbing(rng, reinicios = 10):
    melhor, c_melhor = None, float("inf")
    for _ in range(reinicios):
        s, c = hill_climbing(rng)
        if c < c_melhor: melhor, c_melhor = s, c
    return melhor, c_melhor

def relatorio(sol):
    uso = usos(sol)
    print("Ginasio Dificuldade Pokemon_que_lutam Tempo")
    for g, m in enumerate(sol):
        print(f"  {GINASIOS[g]:<6} {DIF[g]:>8}    {'+'.join(NOMES[i] for i in BITS[m]):<24}{DIF[g] / SOMA[m]:8.3f}")
    print("\nEnergia final:", {NOMES[i]: E - uso[i] for i in range(NP)})
    print("Custo total das batalhas: %.4f" % custo(sol))

if __name__ == "__main__":
    import time
    rng = random.Random(42)
    t = time.time()
    sol, c = simulated_annealing(rng)
    print("SA: %.4f   (%.1fs)\n" % (c, time.time() - t))
    relatorio(sol)