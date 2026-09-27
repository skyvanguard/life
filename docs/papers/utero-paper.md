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
viable; (5) el paso a dos dimensiones y el programa del sol: tres soles en la línea sin vestigio de inteligencia (visible: nada; consecuente: falso positivo replicado; que calienta: sin contacto, el tejido maduro es un cristal), y una primera respuesta al clima en el plano, pendiente de la corrida completa. Discutimos qué
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
| v9–v15 (sol) | contacto con el entorno | ninguna vara supera a sus controles en 18 corridas |
| — (§4.9) | — | **clausura de operandos**: la variación reescribe 1 de 4 campos; los tríos (a,b,c) están congelados en la sopa |
| v16 | clausura de operandos | no evoluciona: la variación abierta es carga; la mortalidad en la hambruna la fija la energía, no el programa |

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

### 4.8 Del orden a la inteligencia: el programa del sol

La novedad es orden. Para preguntar por inteligencia adoptamos la línea Ashby
→ Conant y Ashby → Beer: un tejido es inteligente en la medida en que su
estado interno modela su entorno y usa ese modelo para seguir siendo. Cuatro
varas con sus controles (regulación, anticipación, aprendizaje por
recurrencia, organización), un entorno con estructura aprendible —estaciones
en orden fijo, duraciones típicas pero impredecibles, un día dentro de cada
estación— y una regla pre-registrada de qué contaría como vestigio
(`docs/PLAN_INTELIGENCIA.md`).

- **Sol visible** (el vacío lleva la materia del sol): nada. Anticipación
  2/40 con sol contra 2 en la sombra; aprendizaje 1 contra 5. El tejido apenas
  siente el clima (acople del borde 0,12).
- **Sol consecuente** (la sonda de ceguera se referencia al clima): la regla
  disparó "vestigio" de anticipación con 3/40, el umbral mínimo. La réplica
  con dos soles nuevos y con el orden de estaciones permutado lo mostró falso
  positivo: 3, 2 y 6 positivas respectivamente; 8/120 contra 6 esperados al
  azar. El umbral de 3/40 al 5% era débil; la vara se enmendó (p binomial,
  comparación con el brazo permutado, condición de contacto previa).
- **Sol que calienta** (la superficie recibe materia del sol, κ=0,5): la
  superficie sigue al sol (correlación 0,92) y nada muere ni cambia
  (muertes 0,000 en régimen maduro). El tejido maduro de la línea es un
  cristal con una bomba; el sol calienta la piel de un cristal.

La lección es de Ashby: un tejido sin variables esenciales que el entorno
amenace no tiene nada que regular. En la línea 1-D el sol no amenaza nada.
En el plano, donde el tejido no es un cristal —llena la placa, muere y acuña
sin parar— y la superficie de contacto es grande, el humo mostró por primera
vez respuesta al clima: bajo el orden permutado las muertes se triplican al
inicio de cada estación y la tasa de muerte total es tres veces la del orden
cíclico. La corrida completa (20 semillas, cinco brazos, con un segundo orden cíclico
como control de los tipos de transición) lo desmintió: la placa madura satura
(1.024 vivas) y se vuelve inerte; contacto 0,82, regulación por orden 9/20 y
10/20, lecturas al nivel de los controles.

Tres diseños más cerraron el programa: **muerte por disolución** en el entorno
("lo que se vuelve igual al vacío es vacío"): purga inicial y luego cero
muertes; **metabolismo** (mantenimiento por tick, cosecha del desequilibrio con
el sol, difusión, herencia de energía): el entorno se vuelve esencial —sin sol
el tejido muere— y aun así ninguna vara supera a sus controles; **percepción**
de la propia energía como quinto registro: recambio continuo sin estructura
estacional. Un diagnóstico de escala temporal mostró la razón estructural: la
memoria interna del tejido dura entre 6 y 150 ticks y las estaciones entre 300
y 900. Cuatro diseños más cerraron la búsqueda: **fotosíntesis** (luz sobre todo el
tejido) reveló una bifurcación entre extinción e inmortalidad; **luz finita**
(la luz de cada tick se reparte entre las vivas: una capacidad de carga que
sigue a la estación) dio por primera vez un régimen intermedio real, con la
población siguiendo a la estación y las muertes concentradas en la hambruna,
y dos lecturas de ahorro previo a la hambruna (9/40 y 5/40) que sus réplicas
y el brazo con orden permutado desmontaron como artefacto de acumulación
(15/40 en el brazo sin regularidad). Un último diseño dio al sustrato
**registros lentos** (relojes a la escala de la estación, la pieza que la
medición de escala temporal mostró ausente): tampoco. Catorce corridas
pre-registradas sobre trece diseños, cero vestigios, cuatro señales tentadoras
desmontadas por sus controles.
Un **control positivo** cerró la pregunta: un anticipador diseñado a mano
(detector de estación en un registro lento, SPAWN auto-reescrito según la
estación) es viable y estable en el sustrato, muere en la hambruna la mitad
que el tejido evolucionado, y las varas de anticipación temporal no lo ven
(la lectura de mortalidad regular-vs-permutado sí). Sembrado desde raro no
invade, con partos gratis ni costosos, con o sin regularidad: la ecología no
selecciona la anticipación. El programa se reporta como negativo con
explicación: este sustrato produce orden, novedad y demografía estacional; la
regulación en el sentido de Ashby es viable en él pero no es seleccionada.

Dos regímenes más pusieron a prueba esa explicación con la evolución
experimental como método (elegir el régimen es elegir la pregunta, no la
respuesta): **hambruna dura con parto costoso** (dos sembrados del sol; una
caída de partos 9/40 en el brazo de control no replicó: 2/40) y **tierra
quemada** (el lugar de una celda muerta queda incolonizable una estación:
selección K, para que sobrevivir a la hambruna sea la única forma de tener
territorio). Ninguno movió la mortalidad en la hambruna bajo el orden regular
respecto del permutado (razones 1,2–1,3: mata más, no menos). Dieciocho
corridas pre-registradas, cero vestigios. La recolonización rápida no era el
cuello de botella.

### 4.9 La cuarta jaula: la variación no escribe operandos

La explicación estaba en el VM, no en la ecología. Ningún operador de
variación escribe los campos `a, b, c` de una instrucción: MUTO reescribe el
opcode de la fila `a%K`, el germinal el opcode de la fila `c%K`, COPY traslada
filas que ya existen y SPAWN copia. El conjunto de tríos de operandos de un
mundo es exactamente el de su sopa inicial —248 de los 4096 posibles (6,06%)—
y no cambia nunca: "la física que se reescribe" reescribía uno de sus cuatro
campos. Medido sobre las 40 semillas del programa del sol, sólo 3 sopas
contienen siquiera los operandos de las piezas del anticipador diseñado
(cota superior; Monte Carlo poblacional 0,157), antes de reunirlas en una
celda y en orden mediante filas COPY cuyos propios operandos —fila de origen,
fila de destino— también están congelados. Los dieciocho negativos buscaron
emergencia en un espacio con tres de cada cuatro campos fijos desde el tick
0; el control positivo tuvo que escribirse a mano porque la variación no
podía componerlo. Es la cuarta jaula de la cadena y la única que está en la
variación misma. La respuesta (v16, `escritura_total`: MUTO y el germinal
escriben la instrucción entera desde los registros, sin RNG) abre el espacio
—84 veces más genomas nunca vistos por mundo, 52 tríos nuevos contra 0,
viable en la misma ecología— y se corre con el mismo pre-registro.

### 4.10 Con el espacio abierto: no evoluciona

La corrida con escritura total no cambió nada (sin contacto: el recambio
continuo tapa la hambruna; R2_A 1,30). Con 4× el tiempo y 3× la población
tampoco. Se midió entonces lo previo a cualquier inteligencia. El espectro
de la variación abierta es sano: 23 variantes viables y distintas por 1000
ticks por mundo, una de cada cinco crías distintas se asienta (§16b). Y sin
embargo, contra un brazo **congelado** (MUTO y COPY inertes, crías copias
exactas: la misma ecología sin herencia de cambios), la mortalidad per cápita
en la hambruna baja MÁS en el congelado (razón tardía/temprana 0,19) que con
variación abierta (0,45) o cerrada (0,62): lo que baja es ecología, y la
variación heredable es carga (0,73 contra 0,60 per cápita). **El sustrato no
evoluciona bajo esta ecología.** La heredabilidad medida directamente cierra
el cuadro: la energía al empezar la hambruna predice quién sobrevive en casi
todos los mundos; el genoma, en la mitad, con efecto repetible entre
hambrunas. Hay variación heredable en lo que la hambruna mide y no se
convierte en adaptación; las hipótesis que quedan (canje
supervivencia/fecundidad, genoma como proxy de posición) exigen registro por
celda y una medida de selección directa.

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

**La lección metodológica más cara** de esta línea es la cuarta jaula: se
buscó emergencia durante dieciocho corridas en un espacio que la variación no
podía recorrer, y se atribuyó el silencio a la ecología (selección r, falta
de contacto, escala temporal) cuando estaba en la expresividad del operador
de variación. Un control positivo escrito a mano prueba que la función cabe
en el sustrato, no que la variación pueda alcanzarla; la prueba de
alcanzabilidad —¿qué campos puede escribir la variación y qué fracción del
espacio de programas deja accesible?— debe preceder a cualquier búsqueda de
emergencia.

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
