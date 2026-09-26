# Qué hace falta —y qué no alcanza— para sostener novedad estructural en un sustrato que reescribe su propia física

*Borrador de trabajo, 2026-09-26. Línea El Útero de zeta-life. Todos los
números citan `docs/EL_UTERO.md` (ledger) y `results/utero_*_run.txt`.*

## Resumen

Presentamos El Útero, un autómata celular mínimo en el que **la regla de cada
celda es parte de su estado mutable**: un programa de 16 instrucciones que
actúa sobre la materia local, sobre sí mismo (auto-reescritura) y sobre el
vacío vecino (colonización con variación derivada de la materia, sin generador
de números aleatorios). No hay meta, fitness ni juez: el único filtro es la
persistencia, implementada como una sonda que elimina las físicas ciegas a la
materia. Sobre este sustrato corrimos una serie de diecinueve experimentos,
cada uno con vara definida antes de mirar y control adversarial, y registramos
tanto los resultados positivos como las refutaciones. Los hallazgos
principales: (1) la novedad estructural sostenida —genomas nunca vistos que
siguen acuñándose tras diez mil ticks— es **posible pero rara** en la línea
1-D, alrededor del 5% de las semillas (n=120), y es defendible con el filtro
de persistencia de linaje de MODES y contra una corrida sombra neutral que
acuña exactamente cero; (2) el filtro de persistencia **no es contabilidad
neutra**: sin la sonda, un genoma ciego a la materia barre el mundo en menos
de 250 ticks; (3) la auto-reparación tras destruir la zona activa depende de
la **fertilidad del tejido asentado**, no de su geometría, memoria ni
capacidad, y esa fertilidad falla por un mecanismo preciso —la variación
germinal determinista cae siempre en la misma cría, letal—; (4) tres
mecanismos distintos (memoria recurrente, invasión de tejido asentado,
recombinación al nacer) rompen jaulas nombradas sin mover el techo de
tipicidad, y el último destapa la jaula siguiente, el barrido del clon
viable; (5) *(v8, pendiente)* el paso a dos dimensiones. Discutimos qué
diferencia a este sustrato de BFF, Stringmol, Flow-Lenia y Evoloop, y qué
de lo aquí medido no aparece en esa literatura.

## 1. Pregunta y principios

La pregunta no es si un sistema puede evolucionar hacia una meta, sino si
puede **seguir produciendo estructura nueva** cuando nadie le pide nada. La
literatura de evolución abierta la formula como los "hallmarks" de Tokyo
(Packard et al. 2019); nosotros la acotamos a lo medible: ¿se sigue acuñando
código nunca visto, con descendencia viva, a largo plazo?

Tres principios, no negociables por diseño:

1. **Reglas-como-estado.** No hay ley intocable afuera: la física de cada celda
   vive adentro, y puede cambiar.
2. **Lazo cerrado física↔física.** La regla de una celda produce el próximo
   valor de la materia *y* la próxima versión de sí misma, a partir de su
   vecindario. Local, sin nivel externo.
3. **Persistencia como único filtro.** Ni recompensa ni objetivo. Una celda
   se vacía si su próxima regla es degenerada: no termina, sale de rango o es
   ciega a la materia bajo una sonda. Vivo es lo que logra seguir siendo.

## 2. El sustrato

**Celda.** Materia `v` en el círculo `[0,1)` (toroidal desde v3), programa
`r` de K=16 instrucciones `[op, a, b, c]` con diez operaciones: NOP, ADD, SUB,
MUL, THR, CONST, READ (lee un opcode del vecino), MUTO (reescribe un opcode
propio con `int(|R|·10)`), COPY (copia una instrucción de un vecino) y SPAWN
(coloniza el vacío vecino). Registros `[vl, v, vr, R]`; la salida de materia es
`R mod 1`; `R` crudo es el potencial interno (memoria, v5). El programa es
total por construcción: nunca lanza y termina en K pasos.

**Actualización.** Asincrónica, una celda por vez en orden aleatorio sembrado,
efectos inmediatos. El orden es azar sin dirección: perturba, no elige. No hay
ruido sobre el código.

**Espacio.** Una línea con bordes que crece donde una física escribe más allá
del borde (v1); el vacío interior es colonizable.

**Reproducción.** SPAWN escribe en el vacío vecino una copia de la propia
regla con **una** instrucción reescrita desde la materia del momento (v2,
"germinal"): posición fijada por el campo `c`, opcode `int(|R[b]|·10)`. La
variación sale del estado del mundo, no de un RNG.

**La sonda** (la única mano que se nota). Antes de aplicar la regla se la
ejecuta con la materia de todo el vecindario en 0 y en `h=0,618…`, con la
misma memoria; si las tres salidas coinciden hasta 1e-12, la física es ciega a
la materia y la celda se vacía.

**Encarnaciones como flags** sobre la misma clase, cada una byte-idéntica a la
anterior cuando está apagada (verificado por test):

| Flag | Versión | Qué agrega |
|---|---|---|
| `germinal` | v2 | variación en el parto desde la materia |
| `toroidal` | v3 | materia en un círculo: mapas expansivos expresables |
| `muerte_equilibrio` | v4 | la materia quieta muere (refutado) |
| `memoria` | v5 | el potencial interno persiste tick a tick (2º orden) |
| `invasion="asentada"` | v6 | SPAWN reemplaza una celda viva quieta hace `eq_window` ticks |
| `recombina` | v7 | la cría toma una instrucción del otro progenitor |
| `UteroPlano` | v8 | el mismo sustrato en 2-D, von Neumann |

## 3. La vara y los controles

**Novedad.** Con orden aleatorio, "no ciclar" no prueba nada. Contamos
**genomas nunca vistos acuñados por tramo de 500 ticks**; código nuevo sólo
puede nacer de eventos de escritura (MUTO, COPY, parto), nunca del azar del
orden.

**Filtro de persistencia de linaje** (Dolson et al. 2019). Un genoma acuñado
en `t` cuenta sólo si `t_filtro` ticks después sigue viva su línea: la propia
celda o sus crías por SPAWN. COPY es transferencia horizontal y no cuenta como
descendencia. Se reporta con `t_filtro` ∈ {100, 500, 2000}.

**Corrida sombra** (Bedau, Snyder y Packard 1998). Misma semilla y sustrato,
mismo número de muertes por tick que la corrida real, pero al azar en vez de
por la sonda. Lo que la sombra acuña es deriva.

**Sostenida** = media ≥ 5 genomas persistentes por tramo en el régimen maduro
`[8000, 12000)` y ≥ 2× su sombra. **Típica** = ≥ 8 de 40 semillas.

**Ecología.** Entropía de Shannon (bits) de los genomas persistentes presentes
por tramo. Monocultura = < 1 bit.

**Ablación de la bomba.** En `t=8000` se vacía toda celda cuyo código cambió en
los últimos 200 ticks. Se mide la **cola** (novedad en `+1000..+3000`), no el
pulso de recolonización, y se la divide por la cola de la misma corrida sin
ablar: `R ≥ 0,5` = el motor se reparó.

**Ruido vs función.** Propagación, persistencia y regeneración de los
genomas tardíos contra una línea base de espuma medida en el propio sistema.

Todas las varas y reglas de veredicto se escribieron en el docstring de cada
experimento antes de correrlo. Cuando una regla resultó mal diseñada (la cuota
de genoma dominante de v6), se la declaró y no se reinterpretó el resultado.

## 4. Resultados

### 4.1 La cadena de jaulas

Cada encarnación nombró la jaula en la que cayó la anterior:

| Versión | Jaula que rompe | Jaula en la que cae |
|---|---|---|
| Nivel 1 | — | cristal lento: 3/20 sostienen cambio a 5000 ticks |
| Nivel 2 | forma fija de la ley | ciclos límite: 20/20 en bucles de 1–20 estados |
| v1 | espacio fijo, sincronía | monocultivo: 13/20 crecen a la pared, novedad 0 tras el tramo 1 |
| v2 | copia exacta | materia congelada: partos que acuñan siempre la misma cría |
| v3 | materia contractiva | bomba frágil: novedad sostenida en 1/20, no se regenera |
| v4 | — (refutada) | desierto: matar la materia quieta extingue 15/20 |
| v5 | bomba frágil | rareza: auto-reparación en 1 semilla |
| v6 | llanura inerte | 3/40 estable; mundos vivos pero quietos |
| v7 | punto fijo letal | barrido del clon viable |

### 4.2 Novedad sostenida: rara, real, defendible

- Tipicidad con la vara completa: v5 **2/40**, v6 **3/40**, v7 1/40 (sola) y
  3/40 (con invasión). Con 80 semillas nuevas: v5 3/80, v6 4/80. A 1024
  celdas: 2/40 y 4/40. Combinado n=120: **v5 4,2% [1,8–9,4], v6 5,8%
  [2,9–11,6]**.
- El filtro de linaje casi no cambia el régimen maduro (13: 100% persiste; 35:
  79%; insensible a `t_filtro`). En la sopa inicial sí se pierde 40–60%.
- **La sombra acuña cero** desde t≈500 en las 40 semillas. Verificado a mano:
  en 250 ticks un único genoma ocupa las 242 celdas vivas y la materia se
  detiene. Sin la sonda gana el copiador trivial de Fontana y Buss (1994).
- Ruido vs función (seed 13, t≥6000, 6.198 genomas): 17% visita ≥2 celdas,
  25% vive >10× la línea base, top ~5.800 ticks; estructuras itinerantes tipo
  glider. La regeneración post-ablación falló en v3 y apareció en v5.

### 4.3 Anatomía de la excepción

La seed 13 resiste todas las encarnaciones. Comparada con la 35 (motor mayor,
sin auto-reparación) bajo seis hipótesis pre-registradas: geometría de la
bomba, reservorio lento, capacidad de los sobrevivientes, potencial de borde,
especificidad de la ablación y recolonización. **No distinguen**: misma
fracción activa (0,33), mismos segmentos (10 vs 11), 100% de sobrevivientes
con MUTO/COPY/SPAWN, cadencia bimodal (ventanas 50–400 dan la misma
ablación). **Distinguen**: la 35 sobrevive a una ablación aleatoria del mismo
tamaño y muere a la de la bomba; sus llanuras colonizan el hueco 6× más y las
vivas no suben. Destino de las crías tras la ablación: 13 → 144 nacimientos,
80 genomas, 76% supera 100 ticks; 35 → 699 nacimientos, **6 genomas, vida
mediana 1 tick**.

### 4.4 El mecanismo de la esterilidad

Un sondeo previo refutó la explicación genética: 85–91% de los mutantes de un
opcode de cualquier genoma pasan la sonda. El seguimiento de 3.743 crías de
llanura en 6 semillas dio: 71% ciegas al nacer en su contexto real, **0%
sobrevive 500 ticks, 0% de genomas distintos**; en la 35, 674 crías, 100%
ciegas, un solo genoma. La mutación germinal es una función determinista del
estado quieto de la madre y cae siempre en el mismo mutante, letal. Como
ninguna cría la desplaza, la madre persiste: **la esterilidad se
auto-preserva**. La fertilidad de la 13 no era un tejido fértil en reposo
sino un tejido diverso (44 genomas de llanura contra 16) que, abierto el
espacio, cae en mutantes distintos, algunos viables.

### 4.5 El motor es germinal, no ecológico

La transferencia horizontal (COPY desde un genoma distinto) es 0,0000 en las
llanuras de ambas semillas; la novedad viene de MUTO sola en 96,6% (13) y 86%
(35); las semillas con más transferencia tienen novedad cero (bucles de
copia). Las llanuras ejecutan MUTO y COPY en el 7% de sus celda-ticks sin
cambiar nunca de código: **reescritura idempotente**, un punto fijo de la
auto-reescritura.

### 4.6 Tres mecanismos, un techo

- **Memoria (v5)**: auto-reparación en régimen maduro en la 13 (cola/pre 2,05
  vs 0,10); no en la 35; tipicidad sin cambio.
- **Invasión de tejido asentado (v6)**: 3/40 con cualquier `eq_window` entre
  10 y 1000; sin umbral, 0/40 y churn puro (245 invasiones por tick). El umbral
  es una condición cualitativa —lo que sigue deviniendo no puede ser
  reescrito—, la forma positiva del principio 3. Mantiene vivos los mundos (246
  celdas contra 12) pero quietos; desconcentra (cuota 0,77–0,81 de la de v5).
- **Recombinación al nacer (v7)**: las crías pasan de 100% a **0% ciegas**;
  el mundo se llena; y la 35 colapsa en monocultura (ecología 0,07 bits, 2.386
  crías de un solo genoma). Liberada la fertilidad, un clon viable con ruta de
  copia confiable barre el tejido, invisible para la sonda. La cría letal era
  lo que preservaba la diversidad.

### 4.7 Dos dimensiones (v8)

*Pendiente: `results/utero_plano_run.txt`.* Placa 32×32, bloque 8×8, tres
brazos, misma vara. La dirección del parto se modula con la materia porque con
dirección fija el crecimiento avanza en rayos y la placa no se coloniza.

## 5. Discusión

**Qué hace falta.** Materia que pueda moverse (v3: sin el toro, todo es
contractivo). Espacio para reproducirse (sin vacío no hay partos; la 13 no
pare en régimen estacionario). Un filtro que mate la ceguera a la materia
(sin él, monocultura en 250 ticks). Diversidad de madres, porque la
variación germinal es determinista y sólo madres distintas dan crías
distintas.

**Qué no alcanza.** Más presión de muerte (v4). Memoria (v5). Que la
variación llegue al tejido asentado (v6). Que las crías sean viables (v7).
Cada una rompe una jaula y descubre la siguiente; ninguna mueve el techo del
5%.

**Contra la literatura** (`docs/ESTADO_DEL_ARTE_UTERO.md`). BFF (Agüera y
Arcas et al. 2024) mostró replicadores sin fitness y sin RNG; su
autocorrección de 2026 mostró que un paseo aleatorio los encuentra igual. Aquí
la pregunta no es si aparece un replicador sino si el tejido sigue acuñando
estructura; y la sombra separa lo que acuña la selección de lo que acuña la
deriva. Flow-Lenia lleva parámetros con la materia con mutaciones del
experimentador y una meseta de diversidad; aquí la *forma* de la ley es
mutable y la variación no tiene RNG, y la meseta tiene un mecanismo nombrado.
Evoloop vivió el mismo cruce en 1999 y respondió con colisiones y sexo; aquí
la recombinación funciona mecánicamente y destapa el barrido. Stringmol es el
único sustrato verificado donde la novedad no se seca, y su motor es el
parasitismo: la interacción regla↔regla que aquí es marginal.

**Lo que no aparece en esa literatura**: la muerte por degeneración de la
regla como único filtro y su efecto anti-monocultura medido contra sombra;
la auto-reparación sin objetivo anclada a la diversidad de crías; el
mecanismo del secado (punto fijo letal del mapa germinal) medido cría por
cría; la reescritura idempotente como estado del tejido asentado.

**Límites.** n=1 o 2 en varias anatomías; 40–120 semillas; la sonda y su
umbral son constitutivos de lo que "vive" (Davis 2024); un genoma de largo
fijo con diez operaciones tiene una combinatoria finita y la teoría (Banzhaf
et al. 2016) predice agotamiento sin niveles nuevos; ninguna medida de
complejidad ni de novedad fenotípica (sólo genotípica).

## 6. Trabajo futuro

Mantener la diversidad contra el barrido sin juez: estructura espacial (v8),
límite de uso del vacío (MCC), parasitismo emergente. Vara de novedad
fenotípica y de aprendibilidad (Hughes et al. 2024). Barrido de la severidad
de la sonda (Soros et al. 2016). Genoma de largo variable (condición 4 de
Soros y Stanley).

## Referencias

Ver `docs/ESTADO_DEL_ARTE_UTERO.md` (cada entrada con URL y estado de
verificación).
