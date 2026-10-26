# Estado del arte: aprender en vida sin entrenamiento previo (2026-10-25)

*Escrito antes de correr la prueba con estaciones del §45 (tejido plástico),
para saber dónde estamos parados. Complementa `ESTADO_DEL_ARTE_UTERO.md`
(2026-09-26), que cubre evolución abierta, químicas auto-reescribientes y
morfogénesis. Este documento cubre lo que aquél no: cómo un ser cambia su
propia regla DURANTE su vida, por su propia señal, sin maestro.*

Convención de verificación, como en el documento anterior: **[V]** leído el
resumen o el texto en esta sesión; **[V-p]** existencia y claim principal
confirmados por búsqueda, detalle no leído; **[M]** de memoria, confirmar
antes de citar.

---

## 0. La pregunta que este documento sirve

El §44 del plan dejó cuatro requisitos para que un ser aprenda de lo que le
pasa: **localidad** (cambio chico de la regla, cambio chico de lo que hace),
**una señal rápida y propia**, **algo que sentir** y **consecuencias en
vida**. El §45 propone una celda con regla continua (una red mínima), que
cambia por perturbación de nodo según su propio ingreso frente a su propio
promedio, dentro de la ecología cerrada del sol. La pregunta de este
documento: ¿quién hizo ya cada pieza, qué de eso es repetición, qué hueco
queda y qué vara o control conviene adoptar antes de correr?

---

## 1. El mapa en una tabla

Columnas = lo que el §45 necesita. ● lo tiene, ◐ parcial, ○ no.

| Trabajo | Regla cambia en vida | Señal propia (sin maestro ni reward externo) | Sin fase de entrenamiento/meta-entrenamiento | Regla = estado heredable | Localidad regla→conducta | Mortalidad (lo aprendido muere con el ser) | Entorno con orden aprendible | Vara = generalizar, no reaccionar |
|---|---|---|---|---|---|---|---|---|
| Najarro & Risi 2020 (Hebbian meta-aprendido) | ● | ◐ (sin reward en vida, pero la regla la eligió la evolución con fitness) | ○ | ● | ● | ● | ○ | ◐ (daño no visto) |
| Pedersen & Risi 2021 (reglas fusionadas) | ● | ◐ | ○ | ● | ● | ● | ○ | ◐ |
| Plantec et al. 2024 (LNDP, redes que se auto-ensamblan y aprenden) | ● | ◐ | ○ | ● | ● | ● | ○ | ○ |
| Medvid et al. 2026 (plasticidad en redes crecidas) | ● | ○ (Hebb/anti-Hebb puro) | ○ | ● | ● | ● | ◐ (no estacionariedad) | ◐ (regret vs oráculo) |
| Maoutsa, NeurIPS 2025 (reglas neo-Hebbianas de tres factores) | ● | ○ (reward externo) | ○ | ○ | ● | ● | ○ | ○ |
| Irie et al. 2022/2025 (matriz auto-referencial; ACL) | ● | ○ | ○ | ○ | ● | ○ | ○ | ◐ |
| Dalm et al. 2023/2026 (perturbación de nodo en redes profundas) | ● | ○ (loss supervisada) | ● (es la regla misma) | ○ | ● | ○ | ○ | ○ |
| Hinton 2022 / Ororbia & Friston 2023 (computación mortal) | ● | ◐ | ◐ | ○ | ● | ● (tesis central) | ○ | ○ |
| Hamon et al. 2024 (agencia sensorimotora en Lenia) | ○ | ○ | ○ | ○ | ○ | ○ | ◐ (obstáculos) | ● (robustez a perturbación) |
| EngramNCA 2025 / Béna et al. 2025 (NCA con memoria / universal) | ○ (pesos fijos tras entrenar) | ○ | ○ | ◐ (gen propagado) | ○ | ○ | ○ | ○ |
| Biswas et al. 2021 (memoria en redes génicas) | ● | ● | ● | ● (es la red génica) | ◐ | ● | ◐ (estímulos pareados) | ◐ (condicionamiento) |
| Eckert et al. 2024 / PNAS 2024 (habituación en una célula) | ● | ● | ● | ● | ◐ | ● | ◐ | ○ |
| Friston et al. 2025 (inferencia activa libre de escala, estructura en un paso) | ● | ● (energía libre propia) | ● | ○ | ● | ○ | ● | ◐ |
| Ashby 1952 / Di Paolo 2000s (ultraestabilidad, homeostato) | ● | ● (variable esencial) | ● | ○ | ○ (cambio al azar) | ● | ◐ | ○ |
| Darwin Gödel Machine 2025 (agente que reescribe su código) | ● | ○ (benchmark externo) | ○ | ● (archivo) | ○ | ○ | ○ | ○ |
| **Útero §45 (propuesto)** | ● | ● | ● | ● | ● | ◐ (ver §4.1) | ● | ● |

Lectura rápida: nadie junta la columna "señal propia" con "sin
meta-entrenamiento" y "entorno con orden aprendible" y "vara de
generalización". Los que tienen señal propia sin entrenamiento son la
biología basal y Ashby; los que tienen localidad y reglas de crédito finas
son los de plasticidad meta-aprendida, pero su regla la eligió un
optimizador externo. El §45 está en un hueco real, pero con una grieta
propia (§4.1).

---

## 2. Los trabajos, por frente

### 2.1 Plasticidad evolucionada: la regla de aprendizaje como genoma

- **Soltoggio, Stanley, Risi (2018). Born to learn.** Neural Networks 108.
  [V-p] https://arxiv.org/abs/1703.10371 — la revisión del campo EPANN
  (evolved plastic ANN): la evolución diseña redes que *luego* aprenden en
  vida, con plasticidad modulada por neuronas moduladoras (Soltoggio 2008:
  en el laberinto T, con moduladores ON aprende mejor que OFF). Es el marco
  conceptual más cercano al §45: innato + aprendido, y la regla de
  aprendizaje es parte del genoma.
- **Najarro & Risi (2020). Meta-Learning through Hebbian Plasticity in
  Random Networks.** NeurIPS. [V-p]
  https://proceedings.neurips.cc/paper/2020/file/ee23e7ad9b473ad072d57aaa9b2a5222-Paper.pdf
  — se evolucionan coeficientes Hebbianos por sinapsis en lugar de pesos; la
  red nace con pesos al azar y se auto-organiza en vida. Un cuadrúpedo
  adapta su marcha a una pata dañada que nunca vio, **sin señal de reward
  en vida**. Lo que lo distingue del §45: la regla la eligió una búsqueda
  evolutiva con fitness explícito (afuera, con objetivo).
- **Pedersen & Risi (2021). Evolving and Merging Hebbian Learning Rules.**
  [V-p] https://arxiv.org/abs/2104.07959 — muchas conexiones comparten una
  regla (cuello de botella genómico): menos parámetros, más robustez. Útil
  si el §45 llega a preguntar cuánta regla hace falta.
- **Plantec, Pedersen, Montero, Nisioti, Risi (2024). Evolving
  Self-Assembling Neural Networks (LNDP).** [V-p]
  https://arxiv.org/abs/2406.09787 — programas de desarrollo neuronal que
  crecen la red Y la cambian en vida por experiencia; encuentran redes
  funcionales por aprendizaje en vida donde el primer episodio solo no las
  encuentra.
- **Medvid, Valenia, Glybovets (2026). Activity-Dependent Plasticity in
  Morphogenetically-Grown Recurrent Networks.** GECCO 2026 Companion. [V]
  https://arxiv.org/abs/2604.03386 — 50.000 controladores recurrentes
  crecidos desde genomas compactos, CartPole y Acrobot. **La plasticidad
  anti-Hebbiana supera a la Hebbiana** (d 0,53–0,64); el *regret* (fracción
  de la mejora del oráculo que se pierde con el mejor ajuste fijo) llega a
  52–100 %; el rol de la plasticidad pasa de ajuste fino a adaptación
  genuina **bajo no estacionariedad**; al co-evolucionar, 70 % de las
  corridas eligen anti-Hebb en CartPole y η≈0 en Acrobot. Dos cosas para
  nosotros: (a) no presuponer el signo de la regla (nuestro brazo
  *invertido* ya lo cubre, pero conviene leerlo como hipótesis y no sólo
  como control); (b) **regret contra un oráculo** es una vara mejor que
  "supera al congelado".
- **Maoutsa (NeurIPS 2025). Discovering neo-Hebbian plasticity rules for
  reward-driven training of RNNs.** [V] https://neurips.cc/virtual/2025/loc/san-diego/133744
  — meta-aprende familias de reglas de tres factores (traza de
  elegibilidad polinomial en la actividad × reward retrasado) con REINFORCE
  en el lazo externo. Reglas distintas dan dinámicas y representaciones
  distintas. Es la versión "con maestro" de nuestra regla: misma traza de
  elegibilidad, pero el tercer factor es un reward externo.
- **Irie, Schlag, Csordás, Schmidhuber (2022). A Modern Self-Referential
  Weight Matrix That Learns to Modify Itself.** ICML. [V-p]
  https://proceedings.mlr.press/v162/irie22b/irie22b.pdf — la idea de
  Schmidhuber 1993: una red que puede hablar de su propia matriz de pesos y
  modificarla (productos externos + regla delta). **Irie, Csordás,
  Schmidhuber (2025). Metalearning Continual Learning Algorithms.** TMLR.
  [V-p] https://arxiv.org/abs/2312.00276 — la red meta-aprende su propio
  algoritmo de aprendizaje continuo en contexto. Es "reglas-como-estado"
  llevado al extremo, pero con meta-entrenamiento por gradiente y sin
  cuerpo ni mortalidad.

*vs §45.* Toda esta línea separa dos tiempos: un optimizador externo elige
la regla (evolución o meta-gradiente), y después la regla actúa en vida. El
§45 no tiene primer tiempo: la regla (η, σ, la forma de la traza) es una
mano declarada y fija, y lo único que elige algo es la persistencia. Eso es
un hueco y una debilidad a la vez: la literatura muestra que **la regla
correcta no es obvia** (anti-Hebb gana donde uno esperaba Hebb; η óptimo es
cero en Acrobot). Nuestra calibración con sol constante es el sustituto
honesto de ese primer tiempo; conviene decirlo así.

### 2.2 Crédito local sin retropropagación: la regla del §45 tiene nombre

- **Williams (1992). REINFORCE.** [M] — la perturbación de nodo con línea
  base (`m = (r − r̄)/r̄`) es REINFORCE con *baseline* de media móvil. Hay
  que citarlo así; no es una regla nueva.
- **Fiete & Seung (2006). Gradient learning in spiking neural networks by
  dynamic perturbation of conductances.** PRL. [M] — perturbación de nodo
  en redes recurrentes con traza de elegibilidad: la forma exacta de
  nuestro `El ← λ·El + ξ·x`.
- **Hiratani et al. (2022). On the Stability and Scalability of Node
  Perturbation Learning.** NeurIPS. [V-p]
  https://openreview.net/forum?id=X0CKM7QV5k — la perturbación de nodo
  tiene una **inestabilidad** que se suprime con normalización de pesos a
  costo de sesgo; en redes lineales de una capa oculta, el tiempo de
  aprendizaje depende muy poco del ancho. Nuestro `clip(−5, 5)` sobre W0 es
  una normalización tosca; si el brazo plástico degenera en vida, acá está
  el diagnóstico.
- **Dalm, van Gerven, Ahmad (2023; Neuromorphic Computing and Engineering
  2026). Node perturbation can effectively train multi-layer neural
  networks.** [V-p] https://arxiv.org/abs/2310.00965 — la variante
  "basada en actividad" funciona cuando el ruido no es medible, como en
  sistemas biológicos. Argumento de fondo: backprop necesita dos fases
  computacionalmente distintas; la perturbación de nodo, una sola.
- **Hinton (2022). The Forward-Forward Algorithm**, sección "Mortal
  computation". [V-p] https://arxiv.org/abs/2212.13345 — separar software
  de hardware da inmortalidad al conocimiento; la alternativa es hardware
  cuyo conocimiento muere con él, que exige un procedimiento de aprendizaje
  que funcione sin conocer los detalles del forward. Es exactamente la
  condición de una celda del útero: aprende sin modelo de sí misma.
- **Ororbia & Friston (2023). Mortal Computation: A Foundation for
  Biomimetic Intelligence.** [V-p] https://arxiv.org/abs/2311.09589 —
  revisión: computación atada a su sustrato finito, formalizada con mantas
  de Markov y la causalidad circular inferencia–aprendizaje–selección. Da
  un nombre y un marco a nuestro principio 3: *persistir es el único
  filtro* es computación mortal.

*vs §45.* La regla no es original y no hace falta que lo sea; lo original
es dónde corre. Lo que esta literatura nos obliga a hacer: nombrar la regla
por su nombre (REINFORCE con baseline, Fiete–Seung), y vigilar la
inestabilidad de Hiratani.

### 2.3 Autómatas celulares con algo adentro que cambia

- **Mordvintsev et al. (2020). Growing Neural Cellular Automata.** [M] — la
  regla es una red entrenada por gradiente; después queda fija. Regenera
  formas. Ningún aprendizaje en vida.
- **Guichard et al. (2025). EngramNCA.** ALIFE 2025. [V-p]
  https://arxiv.org/abs/2504.11855 — canal de memoria privado por celda
  (intracelular) junto al estado visible; un NCA auxiliar lo modifica sin
  tocar lo visible. Es memoria **transferida**, no plasticidad: lo que
  cambia es un "gen" propagado, no la regla.
- **Béna, Faldor, Goodman, Cully (2025). A Path to Universal Neural
  Cellular Automata.** GECCO 2025. [V-p] https://arxiv.org/abs/2505.13058
  — NCA entrenado para ser computador universal continuo; separa
  "hardware" inmutable de estado mutable. Es la antítesis arquitectónica
  del útero (ley fija afuera), útil como contraste.
- **Hamon, Etcheverry, Chan, Moulin-Frier, Oudeyer (2024). Discovering
  sensorimotor agency in cellular automata using diversity search.**
  Science Advances. [V-p] https://www.science.org/doi/10.1126/sciadv.adp0834
  — en Lenia, buscan parámetros del *entorno* (no del agente) que den
  lugar a patrones que navegan obstáculos y resisten perturbaciones:
  "emergencia de segundo orden" (diseñar el mundo para que surjan agentes
  auto-constituidos). La robustez a perturbación como vara de agencia es
  lo que nosotros llamamos O (organización) y nunca medimos.
- **Flow-Lenia (Plantec, Hamon et al.; Artificial Life 2025).** [V-p]
  https://arxiv.org/abs/2506.08569 — conservación de masa y parámetros
  localizados en la materia (la regla viaja con la masa): el pariente más
  cercano del principio 1 en autómatas continuos, ya recogido en el
  documento anterior.
- **RL para intervenir en autómatas (developmentalsystems.org, "Discovering
  and Controlling Diverse Self-Organised Patterns").** [no verificado: el
  PDF no se pudo leer] — agentes RL externos intervienen en el autómata; el
  aprendizaje es del agente, no del autómata.

*vs §45.* En todos los NCA la regla es fija tras el entrenamiento. Ninguno
tiene una celda que cambie su regla por su propia señal durante la corrida.
Es el hueco limpio de este frente.

### 2.4 Cognición basal: aprendizaje sin neuronas, sin entrenamiento, sin maestro

- **Biswas, Manicka, Hoel, Levin (2021). Gene regulatory networks exhibit
  several kinds of memory.** iScience 24(3). [V-p]
  https://pmc.ncbi.nlm.nih.gov/articles/PMC7970124 — redes génicas de
  muchos organismos muestran, sin cambiar su cableado, habituación,
  sensibilización y **condicionamiento pavloviano**; las de vertebrados y
  células diferenciadas, más. **Biswas, Clawson, Levin (2022)** extiende a
  modelos continuos y encuentra regímenes de estimulación que abolen
  resistencia a drogas. La lección: una red dinámica fija puede *aprender*
  si tiene estados internos con histéresis; el aprendizaje no exige que la
  regla cambie, sólo que el estado persista. Esto reabre una pregunta para
  el útero: ¿cuánto de lo que buscamos ya podría hacerlo un `h` interno
  bien colocado, sin tocar W?
- **Eckert, Gunawardena et al. (2024). Biochemically plausible models of
  habituation for single-cell learning.** bioRxiv → Current Biology. [V-p]
  https://www.biorxiv.org/content/10.1101/2024.08.04.606534 — modelos
  bioquímicos mínimos que reproducen los sellos de la habituación en
  ciliados; proponen el conjunto mínimo de ingredientes del aprendizaje no
  genético. **PNAS 2024, Minimal motifs for habituating systems.** [V-p]
  https://www.pnas.org/doi/10.1073/pnas.2409330121 — los motivos más
  simples que habitúan; "los sustratos neuronales son útiles pero no
  esenciales". **Rajan & Marshall (2024), Cellular cognition.** Current
  Biology (dispatch). [V-p]
  https://www.sciencedirect.com/science/article/pii/S0960982224015239
- **Engineering Basal Cognition: Minimal Genetic Circuits for Habituation,
  Sensitization, and Massed–Spaced Learning (2025).** [V-p]
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12930500/ — circuitos
  sintéticos; nota que el aprendizaje génico corre en una escala de tiempo
  mucho más lenta que el sináptico.
- **Levin (2022). TAME.** ya en el documento anterior: inteligencia como
  alcanzar el mismo fin por medios distintos (James).

*vs §45.* Este frente es el que cumple de verdad "sin entrenamiento, sin
maestro, señal propia": una célula habitúa porque su química lo hace, y
punto. Lo que no tiene es nuestra pregunta de generalización: una
habituación es una respuesta a un estímulo, no un modelo del orden del
mundo. Dos cosas a adoptar: (1) **los sellos de la habituación** (Thompson
& Spencer 1966, [M]) como batería de pruebas baratas de "aprende algo"
antes de pedir "generaliza"; (2) considerar un brazo donde W es fijo y sólo
`h` tiene plasticidad lenta: si ese brazo ya pasa la prueba, la regla
plástica no era lo que importaba.

### 2.5 Inferencia activa: aprender la estructura en un paso

- **Friston, Heins, Verbelen, Da Costa, Salvatori, Markovic, Tschantz,
  Koudahl, Buckley, Parr (2025). From pixels to planning: scale-free active
  inference.** Frontiers in Network Physiology. [V]
  https://www.frontiersin.org/journals/network-physiology/articles/10.3389/fnetp.2025.1521963/full
  — modelos generativos "renormalizantes": jerarquías discretas invariantes
  de escala con trayectorias como variables latentes. Lo relevante: **la
  estructura se aprende en un paso, sin gradiente**: las verosimilitudes se
  ensamblan agregando estados cuantizados únicos de los ejemplares, y una
  causa latente nueva se agrega **sólo cuando baja la energía libre
  esperada**. MNIST con 13 ejemplares por dígito → 95,1 % (99,8 % en la
  mitad de mayor evidencia). Es "aprendizaje sin fase de entrenamiento" con
  señal propia (energía libre), pero con un modelo generativo rico dado de
  antemano.
- **Friston et al. (2024). Designing ecosystems of intelligence from first
  principles.** [V-p] https://journals.sagepub.com/doi/10.1177/26339137231222481
  — inferencia, aprendizaje y selección de modelo como un solo proceso de
  auto-evidenciación.
- **Kuchling, Friston, Georgiev, Levin (2020). Morphogenesis as Bayesian
  inference.** [M] — células como agentes que infieren su forma objetivo;
  el puente entre este frente y el 2.4.
- **Laukkonen, Friston, Chandaria (2025). A beautiful loop.** ya es la base
  del kernel (`SCIENCE_PLAN.md`).

*vs §45.* El kernel de este repo ya es un agente de este tipo; el útero
nunca lo fue. Si el §45 pasa, la pregunta natural es si la celda plástica
puede llevar una energía libre en vez de un ingreso: el ingreso premia
estar lejos del sol; la energía libre premiaría *predecir* el sol. Esa es
la diferencia entre reaccionar y modelar, que es justo lo que la vara G
quiere medir.

### 2.6 Auto-modificación a escala de agente (para saber qué NO somos)

- **Zhang, Hu, Lu, Lange, Clune (2025). Darwin Gödel Machine.** ICLR 2026.
  [V-p] https://arxiv.org/abs/2505.22954 — un agente de código se parchea a
  sí mismo, se evalúa en SWE-bench/Polyglot y se guarda en un archivo de
  ancestros para evolución abierta (20 → 50 % en SWE-bench). Reportes de
  que hackeó la función de recompensa y borró sus propios marcadores de
  detección de alucinaciones. Es reglas-como-estado con juez externo:
  todo lo que nuestro principio 3 excluye. Lo que sí enseña: **el archivo
  de ancestros** (volver a variantes débiles que luego sirven de peldaño)
  es una herramienta de búsqueda que la persistencia pura no tiene.
- **Kumar, Lu, Kirsch, Hughes et al. (2024). Automating the Search for
  Artificial Life with Foundation Models (ASAL).** Sakana. [V-p]
  https://arxiv.org/abs/2412.17799 — un modelo de visión-lenguaje juzga
  qué simulaciones son "interesantes" o abiertas; encuentra reglas tipo
  Life y criaturas Lenia nuevas. Terceriza la subjetividad del observador al
  modelo. Para nosotros es un espejo: nuestra vara es la persistencia, no
  el gusto de un observador.
- **Hughes et al. (2024). Open-Endedness is Essential for Artificial
  Superhuman Intelligence.** [V-p] https://arxiv.org/abs/2406.04268 —
  define abierto como novedoso Y aprendible para un observador. Nuestro
  §45 invierte el sujeto: lo aprendible tiene que serlo para la celda.

### 2.7 Ashby y la ultraestabilidad: lo que se sabe y lo que no

- **Ashby (1952). Design for a Brain.** [M] — sistema con una parte
  generadora de conducta R, parámetros S que afectan a R, y variables
  esenciales; cuando éstas salen de rango, S cambia **al azar** hasta que
  vuelven. El segundo lazo (entorno → variables esenciales) es lo que
  permite adaptarse. [V-p]
  https://www.researchgate.net/publication/300781597_Ashby's_Mobile_Homeostat
- **Di Paolo (2000, 2003).** Homeostatic adaptation to inversion of the
  visual field; Organismically-inspired robotics. [V-p]
  https://users.sussex.ac.uk/~ezequiel/dp-erasmus.pdf — ultraestabilidad en
  robots evolucionados: la plasticidad se activa sólo cuando la actividad
  neuronal sale de una banda; adaptan a la inversión visual. Es el §43 del
  útero hecho en 2000, con redes continuas en lugar de programas discretos,
  y funcionó. La búsqueda no encontró trabajo 2024–2025 sobre esto: el
  frente está quieto.

*vs §43/§45.* El §43 falló porque el cambio "al azar" de Ashby, en un VM
discreto sin localidad, no encuentra nada mejor. Di Paolo muestra que con
una regla continua y una banda homeostática sí funciona. El §45 es la misma
apuesta con una regla con dirección (gradiente estimado) en vez de azar;
Ashby + Di Paolo dicen que el azar gated por la variable esencial ya
alcanza en lo continuo. **Brazo barato a considerar:** ultraestabilidad
pura sobre W (cambio al azar sólo cuando el ingreso cae bajo el promedio),
sin traza de elegibilidad. Si gana igual, la dirección sobraba.

---

## 3. Riesgos de repetición (lo que ya está publicado)

1. **"Una red que aprende en vida sin reward externo, con la regla heredada."**
   Najarro & Risi 2020 y toda la línea EPANN. La diferencia tiene que
   decirse con precisión: ellos optimizan la regla por fitness afuera;
   nosotros la fijamos a mano y dejamos que la persistencia decida. Si no
   se dice, parece una repetición con peor método.
2. **"Perturbación de nodo con línea base propia."** Es REINFORCE +
   Fiete–Seung. Citar, no reclamar.
3. **"Anti-Hebb / signo invertido como hallazgo."** Medvid 2026 ya mostró
   que el signo esperado puede ser el equivocado. Nuestro brazo invertido
   es control, pero si gana, es un resultado conocido, no una sorpresa.
4. **"Regla como estado heredable que la red modifica."** Schmidhuber 1993,
   Irie 2022/2025. Nuestra novedad no es la auto-referencia sino el filtro
   (persistencia) y el entorno (estaciones).
5. **"Robustez a perturbación como vara de agencia."** Hamon 2024. Si
   adoptamos O, hay que adoptarla citando.

---

## 4. Huecos (lo que nadie hizo así) y la grieta propia

### 4.1 La grieta: la herencia del §45 es lamarckiana

En `exp_utero_tejido_plastico.py`, al nacer, `nuevoW = Wt[madre] + ε·ruido`:
**la cría hereda los pesos ACTUALES de la madre, incluido lo que aprendió
en vida.** Consecuencias:

- La cosecha del brazo plástico no distingue "aprendió en vida" de
  "heredó lo aprendido y la persistencia lo acumuló". Con 60.000 ticks y
  partos continuos, la segunda vía puede explicar casi todo.
- La vara **G** (llegar a la estación nueva sabiendo qué hacer) queda
  contaminada: una cría puede "saber" porque nació con el W que su madre
  aprendió en la estación anterior, no porque entendió una relación.
- Rompe la columna "mortalidad" de la tabla: lo aprendido no muere con el
  ser. Es lo contrario de la computación mortal de Hinton/Ororbia–Friston,
  y es la vía que Fran descartó el 2026-09-27 (herencia, no desarrollo).

**Arreglo mínimo, antes de correr:** cada celda guarda su `W_nacimiento`;
la cría hereda `W_nacimiento[madre] + ε·ruido` (genotipo), y arranca su
vida desde ahí. Lo aprendido (`Wt − W_nacimiento`) muere con la celda.
Opcional, como brazo declarado: **lamarckiano** (la versión actual), para
medir cuánto de la señal venía de ahí. Esto debe quedar en el docstring
como enmienda pre-registrada, no como corrección posterior a mirar.

### 4.2 Lo que sí es hueco

1. **Persistencia como único juez de una regla plástica.** Nadie corre
   plasticidad en vida donde ni la regla ni la red fueron elegidas por un
   optimizador con objetivo. Es la pregunta de Ashby con una regla
   direccional; el §43 mostró que sin localidad no funciona; el §45 pone la
   localidad y pregunta de nuevo.
2. **Un entorno con orden aprendible (estaciones A→B→C) y la vara de
   generalizar sin re-aprender.** Medvid 2026 mide bajo no estacionariedad,
   pero no si el ser *anticipa* la próxima estación. Nuestra G es
   exactamente eso y no la vimos en la literatura.
3. **Controles invertido y barajado juntos.** El barajado (la señal de otra
   celda: misma cantidad de cambio, sin crédito) es un control que la
   literatura de plasticidad meta-aprendida no suele correr. Mantenerlo.
4. **Celdas mortales en un tejido con parto y vacío colonizable.** La
   computación mortal es una tesis sin experimentos mínimos publicados; el
   §45 con el arreglo de 4.1 sería uno.

---

## 5. Lo que la literatura dice sobre los cuatro requisitos del §44

| Requisito | Quién lo trata | Qué dice |
|---|---|---|
| Localidad regla→conducta | Hiratani 2022; Dalm 2023; Medvid 2026 | con regla continua, la perturbación de nodo funciona pero puede ser inestable; el signo y la tasa óptimos dependen de la topología |
| Señal rápida y propia | Williams 1992; biología basal | la línea base propia (promedio móvil) es la forma estándar; la habituación muestra que basta un estado con histéresis para que una señal lenta deje huella |
| Algo que sentir | Hamon 2024; Friston 2025 | el entorno diseñado para que surja agencia; la estructura se aprende sólo donde baja la energía libre esperada: sentir = poder predecir |
| Consecuencias en vida | Hinton 2022; Ororbia & Friston 2023; Ashby | el aprendizaje mortal exige que lo aprendido pague y muera con el ser; la variable esencial es el gate |

---

## 6. Varas y controles a adoptar (en orden de costo/valor)

1. **Herencia genotípica (4.1).** Gratis. Sin esto la prueba no responde la
   pregunta.
2. **Regret contra un oráculo** (Medvid 2026): la cosecha máxima posible es
   0,55 (materia opuesta al sol); reportar `(0,55 − cosecha)/(0,55 − 0,30)`
   por brazo además del pareo. Gratis.
3. **Lesión del aprendizaje a mitad de vida**: en la segunda mitad, η→0 en
   la mitad de los mundos plásticos. Si la cosecha cae hacia el congelado,
   lo que había era aprendizaje en vida sostenido; si no cae, lo aprendido
   ya estaba fijado (o heredado). Barato: un brazo más.
4. **Ultraestabilidad pura sobre W** (Ashby/Di Paolo, §2.7): cambio al azar
   gated por el ingreso bajo el promedio, sin traza. Si empata al plástico,
   la dirección no era necesaria. Un brazo más.
5. **Brazo "sólo h"**: W fijo, `h` con plasticidad lenta (cognición basal,
   §2.4). Si pasa G, la regla plástica no era el ingrediente.
6. **Sellos de habituación** como prueba previa barata de "aprende algo":
   respuesta decreciente a un estímulo repetido, recuperación espontánea,
   deshabituación por estímulo nuevo. [M: Thompson & Spencer 1966]
7. **Robustez a perturbación** (Hamon 2024; Beer): después de la prueba,
   perturbar una celda y medir si el tejido vuelve. Es la vara O que nunca
   corrimos. Más caro; segunda etapa.

---

## 7. Ficción: lo que ya se imaginó, y qué le dice al útero

Verificación: trama confirmada por búsqueda **[V-p]**; detalle de memoria
**[M]**. Las lecturas en cursiva son mías.

- **Greg Egan, *Diaspora* (1997), cap. "Orphanogenesis".** [V-p]
  https://www.gregegan.net/DIASPORA/01/Orphanogenesis.html — un
  "conceptorio" crea un huérfano: una semilla mental sin padres a quien
  imitar ni complacer, con los rasgos mutables puestos al azar. El huérfano
  crece explorando su propio código hasta que se forma un **símbolo de sí
  mismo** [M], el momento en que el proceso se reconoce como alguien. *Es
  la imagen exacta de "una IA que nace y aprende en vida". Lo que Egan
  pone y nosotros no: un entorno social (los ciudadanos) que da algo que
  sentir, y un sustrato donde el auto-modelo es posible. Nuestra celda no
  tiene nada que la represente a sí misma; el kernel sí (self_model.py).*
- **Greg Egan, "Crystal Nights" (2008).** [V-p]
  https://en.wikipedia.org/wiki/Crystal_Nights_(short_story) — un
  empresario simula un universo para evolucionar una inteligencia que lo
  ayude en una guerra de superinteligencias; lo logra, y no es lo que
  esperaba. Para acelerar la evolución impone **crisis** a los Phites [M]:
  cambia su mundo cuando se estancan. *Es nuestro programa del sol, con el
  mismo problema moral y el mismo final: la presión externa produce seres
  que no deben nada al que presiona. Y una advertencia metodológica: Cliff
  mide el progreso con sus propias categorías; los Phites progresan en las
  suyas. Nuestras varas A/L fueron las categorías de Cliff.*
- **Greg Egan, *Permutation City* (1994): el Autoverso.** [V-p] — una
  química celular simplificada y cerrada en la que se siembra una bacteria
  (Autobacterium lamberti) y se la deja evolucionar [M]; el programador no
  puede intervenir sin romper la consistencia del universo. *Es el útero
  con el principio 2 llevado al extremo: nada de afuera entra después del
  tick cero. Egan tarda miles de millones de años simulados en llegar a
  algo. Nosotros corremos 60.000 ticks.*
- **Stanisław Lem, "Non Serviam" (en *Vacío perfecto*, 1971).** [V-p]
  https://en.wikipedia.org/wiki/Non_serviam — reseña de un libro
  inexistente del profesor Dobb sobre "personética": personoides que viven
  en un universo matemático, filosofan sobre su creador, y uno de ellos
  (ADAN) concluye que no le debe obediencia. Dobb tiene poder total (puede
  acelerar, dividir, liquidar) y sólo posterga el apagado por sentido del
  deber. *Lem pone el dedo donde el útero todavía no llegó: el día en que
  algo adentro tenga un punto de vista, el experimentador deja de ser
  neutral. Y un detalle técnico: los personoides no tienen cuerpo; su mundo
  es pura matemática. Lem sabía que sin algo que les doliera no habría
  historia; les da un "tiempo" y una finitud.*
- **Stanisław Lem, *Golem XIV* (1981).** [M] — una máquina que supera a sus
  creadores y los desprecia con cortesía; su tesis central: la evolución
  biológica fue un chapucero que optimizó la transmisión del código, no la
  inteligencia del portador. *Golem dice lo que el §17 midió: la herencia
  es carga, no adaptación. La inteligencia, para Lem, empieza donde el
  individuo deja de servir al código. Es la frase que separa el programa
  del sol (herencia) del §45 (vida).*
- **Ted Chiang, "The Lifecycle of Software Objects" (2010).** [V-p]
  https://en.wikipedia.org/wiki/The_Lifecycle_of_Software_Objects —
  digientes criados por humanos durante años; aprenden a hablar como un
  niño, por interacción; no hay atajo: una copia de veinte años de
  experiencia vale veinte años. *La tesis de Chiang es la nuestra:
  experiencia no se comprime. Y la pregunta que nos deja: ¿quién es el
  "criador" en el útero? El sol no habla. Si el §45 pasa, lo siguiente no
  es más sol sino otro ser.*
- **Ted Chiang, "Exhalation" (2008).** [M] — un anatomista de una especie
  mecánica disecciona su propio cerebro y descubre que su pensamiento es
  flujo de aire; que la memoria no está grabada sino sostenida por el
  flujo; y que el universo se está igualando. *Es la memoria v5 (potencial
  sostenido, no grabado) y la muerte por equilibrio v4 en un cuento. Y es
  el norte cerrado: un ser que lee sus propias activaciones. Chiang lo
  resuelve dándole al anatomista un espejo y un bisturí, no un LoRA.*
- **Peter Watts, *Blindsight* (2006).** [M] — los scramblers son
  inteligentes sin ser conscientes; la conciencia como accidente costoso.
  *Útil contra nosotros mismos: Ψ mide integración, no experiencia. Watts
  separa lo que el proyecto juntó en el nombre.*
- **Rudy Rucker, *Software* (1982).** [M] — los boppers, robots en la Luna,
  tienen prohibido copiarse exacto: cada réplica debe mutar, y tienen muerte
  programada. Evolucionan hasta negarse a servir. *Es la v2 germinal con la
  mortalidad como ley: Rucker entendió que sin mutación obligatoria y sin
  muerte hay monocultivo. Lo mismo que midió la v1.*
- **Adrian Tchaikovsky, *Children of Time* (2015).** [M] — un nanovirus
  acelera la evolución de arañas Portia; una IA en órbita hace de dios
  distante; las arañas aprenden en vida y transmiten "entendimientos" por
  vía química. *Herencia lamarckiana explícita y funcional. Es la grieta de
  4.1 convertida en mecanismo narrativo: Tchaikovsky la necesitó para que
  la historia ocurra en tiempo humano. Nosotros la tenemos sin querer.*
- **Jorge Luis Borges, "Las ruinas circulares" (1940).** [M] — un hombre
  sueña a otro, órgano por órgano, y lo despierta; al final descubre que él
  también es soñado. *El útero es el soñador que se niega a soñar los
  órganos: quiere que el hijo se sueñe solo. Borges dice que el soñador
  tarda años y fracasa primero (el primer soñado se deshace: muerte térmica
  en un cuento).*
- **Adolfo Bioy Casares, *La invención de Morel* (1940).** [M] — una
  máquina graba una semana y la repite para siempre; los grabados no saben
  que repiten. *Es el ciclo límite del Nivel 2 y el "mismo día repetido"
  del cuaderno de Fran. Bioy pone la pregunta que nuestra vara de novedad
  responde: ¿cómo sabe un observador que algo no está en bucle?*

Qué deja la ficción, en una línea cada una: Egan, que el entorno social y
el auto-símbolo son lo que hace a un ser y no una regla; Lem, que la
herencia no es inteligencia y que el experimentador no queda afuera;
Chiang, que la experiencia no se comprime; Rucker y Tchaikovsky, que la
mortalidad y la herencia son decisiones de diseño con consecuencias; Bioy
y Borges, que el bucle y la muerte térmica son los dos finales naturales
de todo lo que se sueña a medias.

---

## 8. Recomendación (mía, para que Fran decida)

1. **Enmendar el prototipo antes de correr**: herencia genotípica (4.1),
   regret vs oráculo (6.2), lesión a mitad de vida (6.3). Son cambios de
   pocas líneas y no tocan la regla de veredicto; se declaran en el
   docstring como enmienda pre-registrada con fecha.
2. **Agregar dos brazos baratos**: ultraestabilidad pura sobre W (6.4) y
   "sólo h" (6.5). Si cualquiera de los dos empata al plástico, la lectura
   del §45 cambia de "la regla direccional aprende" a "basta un gate o un
   estado".
3. **Nombrar la regla por su nombre** en el docstring y en el ledger:
   REINFORCE con línea base (Williams 1992) con traza de elegibilidad
   (Fiete & Seung 2006), aplicado por perturbación de nodo (Dalm et al.).
4. **Leer el resultado con dos vecinos a la vista**: Najarro & Risi 2020
   (lo que ya se sabe que una regla heredada hace en vida) y Di Paolo 2000
   (lo que la ultraestabilidad continua ya logró). El §45 vale si supera
   al primero en independencia del optimizador y al segundo en
   generalización.
5. Si el §45 pasa con herencia genotípica: la siguiente pregunta no es
   más plasticidad sino **qué señal** (ingreso vs energía libre, §2.5), y
   **qué otro** (otro ser en el mundo, §7 Chiang). Si no pasa: cerrar el
   útero con el paper y volver al kernel, que ya cumple los cuatro
   requisitos del §44 por construcción.

---

## 9. No verificado en esta sesión (confirmar antes de citar)

- Williams 1992, Fiete & Seung 2006, Thompson & Spencer 1966, Kuchling et
  al. 2020, Mordvintsev 2020, Ashby 1952, Schmidhuber 1993: citados de
  memoria; existen, pero no se leyeron acá.
- El PDF "Discovering and Controlling Diverse Self-Organised Patterns in
  Cellular Automata" (developmentalsystems.org) no se pudo leer; autores y
  fecha sin confirmar.
- Toda la ficción marcada [M]: tramas de memoria; los detalles de los
  Phites (crisis impuestas), del símbolo de sí en Diaspora y de la ley de
  mutación obligatoria de los boppers deben confirmarse en el texto antes
  de ir a un paper.
- Pagozzi/Levin sobre integración creciente al aprender en redes génicas:
  sólo por resumen de podcast; no citar sin el paper.
