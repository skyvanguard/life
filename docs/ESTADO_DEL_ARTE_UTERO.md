# El Útero — estado del arte (relevamiento 2026-09-26)

**Para qué.** Antes de tocar el sustrato otra vez, saber dónde está el campo:
qué ya se hizo (para no repetirlo), qué dice la literatura sobre NUESTRO cruce
abierto (variación germinal cuando la materia se aquieta, sin RNG ni fitness), y
qué métricas hacen falta para que un resultado del Útero sea comparable y
defendible.

**Cómo.** Tres frentes buscados en paralelo con verificación por URL:
(1) programas y químicas artificiales auto-reescribientes sin fitness;
(2) autómatas celulares con la regla en la materia, no uniformes y
auto-modificantes; (3) teoría y métricas de evolución abierta (OEE) y
autopoiesis computacional. Convención: **[V]** verificado en fuente primaria
(abstract o texto), **[V-p]** verificado en parte (título/abstract sí, detalle
de snippet o memoria), **[NV]** no verificado — no citar sin confirmar.

Referencia rápida a lo nuestro: `docs/EL_UTERO.md` (principios y ledger).
Los tres principios: **P1** reglas-como-estado, **P2** lazo física↔física (la
regla actúa sobre el mundo y sobre sí misma), **P3** persistencia como único
filtro. Más dos rasgos de la encarnación: **variación sin RNG** (la mutación
germinal sale de la materia) y **espacio que crece** por escritura en el borde.
Nuestra vara: **genomas nunca vistos por tramo**.

---

## 1. El mapa en una tabla

| Trabajo | Regla vive en el estado | Reescribe su FORMA | Fitness / juez | Variación | Filtro | Novedad a largo plazo |
|---|---|---|---|---|---|---|
| **Computational Life / BFF** (Agüera y Arcas et al. 2024) [V] | sí (código = datos) | sí (auto-modificación) | no | interacción; **mutación 0 funciona** | sobreescritura (nadie muere) | replicadores emergen; SUBLEQ no |
| **BFF: simple explanations** (Knierim et al. 2026) [V] | — | — | — | — | — | **autocorrección:** un random walk los encuentra igual; la interacción explica la *difusión*, no el *descubrimiento* |
| **Stringmol** (Hickinbotham, Stepney, Hogeweg 2021) [V] | sí | sí (código auto-modificable) | implícito (replicarse) | **RNG de copia** + parásitos | decaimiento aleatorio | **no se estanca en 2M pasos** (8/20); motor = parasitismo |
| **AlChemy** (Fontana & Buss 1994) [V] | sí (λ = función y dato) | sí | no | colisión | ninguno explícito | copiadores triviales saturan; organizaciones si se inhibe la copia |
| **Coreworld** (Rasmussen et al. 1990) [V-p] | sí (código en el core) | sí | no | ruido externo | ninguno | épocas; pariente 1-D más cercano |
| **Tierra** (Ray 1991) [V] | sí | sí | Reaper (edad/errores) | bit flips externos | Reaper | **se seca** (Bedau 1997, Standish 2003) |
| **Amoeba** (Pargellis 1996–2017) [V] | sí | sí | no | mutación externa | ninguno | replicadores desde sopa aleatoria; mide la **pre-vida** (MI entre opcodes) |
| **Kruszewski & Mikolov 2021** (S/K/I) [V] | sí | sí | no (conservación de masa) | aplicación | conservación | diversidad explota y **decae** |
| **Flow-Lenia** (Plantec et al. 2023/2025) [V] | sí (parámetros viajan con la masa) | **no** (kernels fijos) | no (competencia por masa) | **beams gaussianos del experimentador** | masa | la diversidad de parámetros **se estabiliza** para todo p_mut |
| **Evoloop / SDSR** (Sayama 1999; revisión 2024) [V] | **no** (regla del CA fija) | no | no | **contacto fenotípico, sin RNG** | espacio finito | converge al loop mínimo… pero con diversidad residual mayor de la esperada |
| **Sipper, CA no uniformes** (1996–97) [V-p] | sí (una regla por celda) | no (tabla) | **sí** (tarea global) | cruce con vecinos | — | — |
| **SDCA** (Ilachinski & Halpern 1987) [V] | no | no | no | — | — | topología mutable, no regla |
| **Growing NCA** (Mordvintsev et al. 2020) [V] | no | no | **sí** (imagen objetivo) | gradiente | — | regeneración **entrenada** |
| **Chromaria / MCC** (Soros & Stanley 2014–2020) [V] | no | no | **criterio mínimo** | mutación externa | viabilidad mínima | complejidad crece; la *strictness* decide entre estancamiento y divergencia |
| **ASAL** (Kumar et al. 2024) [V] | no | no | **CLIP como juez** | búsqueda | — | vara de novedad fenotípica por embeddings |

**Lectura de la tabla.** Ninguna fila junta lo que el Útero junta: regla que
reescribe su *forma* (no sólo parámetros) dentro de un CA espacial local, sin
juez, con variación derivada de la materia, con muerte por degeneración de la
regla, y espacio que crece. Pero cada pieza por separado **ya existe**, y dos
resultados que consideramos nuestros ya están publicados con más n (ver §3).

---

## 2. Los trabajos que hay que conocer, por frente

### 2.1 Programas y químicas que se reescriben sin fitness

- **Agüera y Arcas, Alakuijala, Evans, Laurie, Mordvintsev, Niklasson, Randazzo,
  Versari (2024). "Computational Life: How Well-formed, Self-replicating Programs
  Emerge from Simple Interaction."** arXiv 2406.19108. [V]
  https://arxiv.org/abs/2406.19108
  Sopa de cintas de 64 bytes en BFF: dos cintas se concatenan, se ejecutan y se
  separan; código y datos en la misma cinta. Replicadores emergen **sin fitness
  y sin mutación de fondo** (~50% de corridas a tasa 0%). Vara: *high-order
  entropy* (Shannon − Kolmogorov aproximada por compresión). Sustratos: Forth
  (casi siempre), Z80/8080, y **SUBLEQ como contraejemplo honesto**.
  *vs Útero:* ya hizo "vida sin fitness, sin RNG, código auto-modificable". No
  tiene filtro de muerte, ni espacio, ni separación regla/materia.
- **Knierim, Versari, Obryk, Agüera y Arcas, Saurous (2026). "BFF: Simple
  explanations for complex phenomena."** arXiv 2607.01483. [V]
  https://arxiv.org/abs/2607.01483
  El mismo grupo se corrige: con un **detector directo de replicador**, un paseo
  aleatorio de mutación los encuentra tan fácil como la interacción; bloquear la
  ancestría no impide la aparición, sólo la toma de la sopa. *vs Útero:* nuestro
  SPAWN con una mutación desde la materia es, funcionalmente, un paseo en el
  espacio de programas. Hay que medir **aparición** y **toma de tejido** por
  separado, con detector directo, no inferir del agregado.
- **Hickinbotham, Stepney, Hogeweg (2021). "Nothing in evolution makes sense
  except in the light of parasitism."** R. Soc. Open Sci. 8:210441. [V]
  https://royalsocietypublishing.org/rsos/article/8/8/210441/96415
  Stringmol: moléculas = programas string auto-modificables, binding suave,
  fitness implícito (replicarse), decaimiento aleatorio, RNG de copia. **8/20
  corridas viven 2M pasos y la evolución no se estanca**: ciclos
  parásito→defensa→relajación→nuevo parásito; "la evolución misma evoluciona"
  (nuevos operadores mutacionales emergentes). *vs Útero:* el más cercano en
  espíritu y **el único verificado donde la novedad no se secó** — con RNG y con
  parásitos como motor. Pista directa para nuestro cruce.
- **Fontana & Buss (1994). PNAS 91:757.** [V]
  https://www.pnas.org/doi/abs/10.1073/pnas.91.2.757 — AlChemy: la regla ES el
  estado (λ-expresiones). Sin freno, los auto-copiadores saturan; inhibida la
  copia, emergen organizaciones auto-mantenidas. *vs Útero:* pariente de nuestra
  "misma cría, parto tras parto".
- **Pargellis (1996, 2001, 2003); Greenbaum & Pargellis (2017), ALife 23(3).** [V]
  https://direct.mit.edu/artl/article-abstract/23/3/318/2891 — Amoeba:
  replicadores desde sopa de opcodes aleatorios, precedidos por una fase de
  **auto-organización pre-vida** medida con información mutua entre pares de
  opcodes. *vs Útero:* vara lista para nuestras llanuras "estériles" vs
  "fértiles".
- **Rasmussen et al. (1990) Coreworld** [V-p]; **Ray (1991) Tierra** [V];
  **Ofria & Wilke (2004) Avida** [V-p] — el linaje clásico. Tierra es el
  precedente canónico de "la novedad se seca" (Bedau & Packard 1997). Avida tiene
  fitness explícito: antípoda de P3.
- **Kruszewski & Mikolov (2021).** arXiv 2103.08245. [V] — lógica combinatoria con
  conservación de masa como única presión; metabolismos emergen; **la diversidad
  decae** a largo plazo.
- **Dittrich, Ziegler, Banzhaf (2001). "Artificial Chemistries — A Review."**
  ALife 7(3). [V] https://direct.mit.edu/artl/article/7/3/225/2373 — el marco
  (S, R, A). Nombra lo nuestro: **R ⊂ S** (las reglas son moléculas).
- 2025–2026: **Vimal, Mathis, Weimer, Forrest (2025)** "Prebiotic Functional
  Programs" arXiv 2509.03534 [V] (AlChemy sin fitness, selección endógena);
  **Cicala et al. (2026)** arXiv 2607.09211 [V] (Z80 con tarea = juez, no es
  nuestro camino); **Horiguchi & Sayama (2026)** Hash Chemistry arXiv 2607.28219
  [V] (fitness por hash, no comparable).

### 2.2 Autómatas con la regla en la materia

- **Plantec, Hamon, Etcheverry, Chan, Oudeyer, Moulin-Frier (2025). "Flow-Lenia."**
  Artificial Life 31(2):228 (ALIFE 2023 best paper). [V]
  https://arxiv.org/abs/2506.08569
  Lenia con conservación de masa y **parámetros localizados** que se advectan con
  la materia y se mezclan al confluir. Selección por competencia de masa, sin
  juez. **Pero** la variación son "beams" gaussianos de 10×10 aplicados por el
  experimentador (las mutaciones de una celda "son absorbidas por los vecinos"),
  los kernels quedan fijos (la *forma* de la ley no muta), y **la diversidad de
  parámetros se estabiliza para todo p_mut**. Miden con actividad evolutiva
  (Bedau & Packard) y árbol PCA. Admiten que "especie = punto único de
  parámetros" infla la diversidad — el mismo defecto de nuestra vara.
  *vs Útero:* es el "reglas-como-estado" citable hoy; su plateau replica nuestro
  secado.
- **Michel et al. (2025)** arXiv 2505.15998 [V] — IMGEP sobre hiperparámetros de
  Flow-Lenia; útil como catálogo de métricas no supervisadas (compresión de
  video, entropía multiescala). **Akhtyrchenko et al. (2026)** MSPD arXiv
  2606.17091 [V] — escalar que mide cómo se organiza la heterogeneidad de las
  leyes locales a través de escalas; aplicable a nuestro tejido como *lente*.
- **Sayama (1999). "Evoloop / SDSR."** ALife 5(4):343. [V-p]; **Sayama & Nehaniv
  (2025). "25 Years After Evoloops."** ALife 31(1):81. [V]
  https://arxiv.org/abs/2402.03961
  CA determinista donde los loops varían **por contacto fenotípico, sin RNG y sin
  fitness**, con actualización asíncrona probada. Resultado original:
  convergencia al loop más chico. La revisión matiza: secuenciados todos los
  individuos, la diversidad fue mayor y siguió evolucionando; y las tres
  respuestas empíricas al secado fueron **colisiones, auto-protección y sexo por
  intercambio en colisión** (Sexyloop, Oros & Nehaniv 2007–2009). Distinguen
  *self-replication* (copia) de *self-reproduction* (variación heredable).
  *vs Útero:* **nuestro cruce abierto es su problema de 1999**, ya con tres
  respuestas. La regla del CA allí es externa: eso sigue siendo nuestro.
- **Hutton (2007)** ALife 13(1):11 [V-p, resultados no verificados]; **Sipper
  (1996–97)** [V-p] — una regla por celda, pero fitness de tarea; **Ilachinski &
  Halpern (1987)** SDCA [V] — topología mutable (pariente de nuestro espacio
  creciente, no de P1).
- **Mordvintsev, Randazzo, Niklasson, Levin (2020). Growing NCA.** Distill. [V]
  https://distill.pub/2020/growing-ca/ — la regeneración es un atractor
  **entrenado** con imagen objetivo. No usar el mismo vocabulario sin aclarar.
- **Hamon et al. (2025). Sensorimotor Lenia.** Science Advances 11(44). [V] — la
  agencia la encuentra un buscador con objetivo; lo aprovechable es su test de
  generalización fuera de distribución como control función-vs-ruido.
- **Kumar et al. (2024/2025). ASAL.** [V] https://arxiv.org/abs/2412.17799 — CLIP
  como juez; ofrece una **vara de novedad fenotípica** (distancia entre embeddings
  de frames) útil post-hoc para controlar que "genoma nuevo" ≠ "fenotipo nuevo".
- **Yin (2026)** arXiv 2603.25239 [V] — barrido de 262.144 reglas outer-totalistic:
  7,7% soportan proliferación, concentradas en λ≈0,15–0,25. Prior sobre dónde vive
  la vida en el espacio de reglas.

### 2.3 Teoría y métricas de evolución abierta

- **Dolson, Vostinar, Wiser, Ofria (2019). "The MODES Toolbox."** ALife 25(1):50.
  [V] https://doi.org/10.1162/artl_a_00280
  Cuatro métricas sobre los componentes que pasan un **filtro de persistencia de
  linaje** (cuenta sólo lo que tiene descendencia t pasos después, para no inflar
  por deriva): *change*, *novelty*, *complexity* (sitios que importan), *ecology*
  (entropía). Hallazgo: la novedad **decae** en NK y Avida; sólo la alta tasa de
  mutación la sostiene. *vs Útero:* **"genomas nunca vistos por tramo" es la
  novelty de MODES sin el filtro de persistencia** — contamos acuñación, no
  supervivencia de la línea. Es exactamente la inflación que MODES quiere evitar.
- **Bedau, Snyder, Packard (1998).** ALife VI. [V] — actividad evolutiva con
  *shadow* neutral emparejado; clases 1/2/3 de dinámica. **Channon (2024).**
  ALife 30(3):345. [V] — procedimiento por pasos para reclamar OEE "Tokyo tipo 1";
  ejemplo 2026 (de Pinho & Sinapayen, arXiv 2603.01701): ToLSim pasa 8/20 el paso
  1 y **0/20** el paso 3. *vs Útero:* nuestro 2/40 debe reportarse así.
- **Taylor et al. (2016)** ALife 22(3) [V]; **Banzhaf et al. (2016)** Theory in
  Biosciences [V]; **Packard et al. (2019)** ALife 25(2) [V]. Hallmarks York →
  categorías **Tokyo**: (1) nuevas clases de entidades, (2) **evolución de la
  evolvabilidad**, (3) transiciones mayores, (4) evolución semántica. Banzhaf:
  novedad = variación / innovación / emergencia. *vs Útero:* nuestra novedad es
  **variación (tipo 0)**; lo que buscamos en el cruce ("que la variación no
  dependa de la materia quieta") es literalmente **Tokyo 2**. Con genoma de 16
  instrucciones fijo, la combinatoria de un nivel es finita: Banzhaf predice
  agotamiento salvo que aparezcan niveles.
- **Hughes et al. (2024). "Open-Endedness is Essential for ASI."** ICML. [V]
  https://arxiv.org/abs/2406.04268 — open-ended ⇔ **novedad** (menos predecible
  con modelo fijo) **y aprendibilidad** (más historia mejora la predicción),
  respecto a un observador. *vs Útero:* medimos sólo novedad; un compresor o
  n-grama sobre genomas por tramo daría la mitad que falta y formaliza nuestro
  control ruido-vs-función.
- **Soros & Stanley (2014); Soros, Cheney, Stanley (2016); Brant & Stanley
  (2017, 2019, 2020).** [V] Criterio mínimo (MC): el único filtro es una
  viabilidad mínima. **La *strictness* del MC decide entre estancamiento (en
  ambos extremos) y divergencia ordenada.** MCC: coevolución interbloqueada y
  límite de recursos preservan diversidad. *vs Útero:* P3 es un MC implícito y
  **`PROBE_EPS` es nuestra strictness**: hay que barrerla, no dejarla fija como
  "mano declarada". Nuestra "fertilidad" es su condición 2 (la evolución crea
  nuevas oportunidades de cumplir el criterio). Violamos su condición 4 (genoma
  de longitud fija).
- **Beer (2004, 2014, 2015, 2020).** Autopoiesis en el Game of Life. [V]
  Perturbaciones **destructivas** vs **no destructivas**; *dominio cognitivo* de
  una entidad = conjunto de perturbaciones que no la desintegran; tasas de
  creación/persistencia/destrucción de gliders. **McMullin (2004)** [V] revisa el
  modelo de Varela–Maturana–Uribe. **Davis (2024)** arXiv 2407.21086 [V]: la
  autopoiesis de un glider en Lenia depende de la resolución — aviso de que
  `PROBE_EPS` y la discretización pueden ser constitutivas de lo que "vive".
  *vs Útero:* criterios operacionales listos para nuestras estructuras
  itinerantes y para generalizar la "regeneración post-ablación".

---

### 2.4 Morfogénesis y cognición basal: la inteligencia de las estructuras organizadas (agregado 2026-09-27)

Frente que Fran señaló como el más alineado con lo que busca (recordaba "a
Zapata"; la investigación original no está en el historial de sesiones de
Claude Code: se identificó por búsqueda).

- **Carrillo-Zapata, Sharpe, Winfield, Giuggioli, Hauert (2019). Toward
  controllable morphogenesis in large robot swarms.** IEEE RA-L 4(4):3386. [V,
  preprint leído] https://research-information.bris.ac.uk/ws/files/202534060/Towards_controllable_morphogenesis_in_large_robot_swarms_preprint.pdf
  — 300 kilobots idénticos, SIN auto-localización, SIN mapa y SIN programa de
  la forma, hacen crecer formas sólo con comunicación local (reacción-difusión
  de "morfógenos" virtuales + gradientes locales), **regeneran las partes
  que se les cortan a mano** y rodean obstáculos. Más de 2000 simulaciones y
  3 enjambres reales. Tres parámetros dan un morfoespacio controlable.
- **Slavkov, Carrillo-Zapata, …, Hauert, Sharpe (2018). Morphogenesis in
  robot swarms.** Science Robotics 3(25):eaau9178. [V-p: existencia y
  coautoría por búsqueda] — la primera demostración de morfogénesis
  completamente auto-organizada en un enjambre real, inspirada en los
  patrones de Turing del desarrollo (Sharpe estudia la formación de dedos).
- **Levin (2022). TAME.** Frontiers in Systems Neuroscience, arXiv 2201.10346.
  [V-p: resumen] — la cognición basal en células, tejidos y enjambres. Toma de
  William James el criterio funcional de inteligencia: **alcanzar el mismo fin
  por medios distintos**, con competencia ante lo nuevo; no depende de tener
  cerebro.
- **Ashby (1948/1952). Homeostato; Design for a Brain.** [conocido, no
  consultado en esta sesión] — ultraestabilidad: reconfigurarse cuando las
  variables esenciales salen de rango. Base de §43.

*vs Útero.* Los robots de Carrillo-Zapata tienen reglas FIJAS e idénticas: la
emergencia sale de la interacción, no de reescribirse. El útero tiene la regla
como estado. Lo que ellos tienen y el útero casi no: **regeneración de la
forma** (en el útero, auto-reparación en 1 de 40 semillas, v5). Lo que aporta
para la vara: la regeneración es la prueba de James/Levin hecha medible —
cortar, y ver si el tejido vuelve al MISMO estado por un camino distinto, y
no a cualquier estado. Eso distingue una estructura organizada con algo
parecido a una meta de un patrón que sólo se repite.

## 3. Riesgos de repetición (lo que ya está publicado)

1. **"Replicadores emergen sin fitness y sin RNG"** — Computational Life 2024, y
   relativizado por su propio grupo en 2026 (un random walk basta). Reclamarlo es
   repetir; reclamarlo sin detector directo es repetir peor.
2. **"Código auto-modificable / código = datos"** — BFF, Stringmol, Tierra,
   Coreworld, AlChemy.
3. **"La regla viaja con la materia y hay selección sin juez"** — Flow-Lenia
   2023/2025, con actividad evolutiva y árbol PCA.
4. **"Variación por contacto sin RNG, sin fitness, asíncrono, converge a lo
   mínimo"** — Evoloop 1999, con 25 años de literatura y tres respuestas.
5. **"Fase de pre-vida / tejido que se auto-organiza antes del replicador"** —
   Pargellis 1996–2017, con métrica (MI entre opcodes).
6. **"La novedad se seca / se estabiliza"** — Tierra, MODES en NK/Avida,
   Kruszewski 2021, Flow-Lenia 2025, ToLSim 2026. Es el resultado **por defecto**.
   Lo publicable no es el secado sino su **mecanismo** (y ahí la fertilidad de las
   llanuras es un candidato real).
7. **"Persistencia como único filtro"** ya está en Chromaria/MCC/BFF/Stringmol;
   sin las métricas de §5, nuestro 2/40 no se distingue de una novedad por deriva
   ni de una clase-1 de Bedau.
8. **"Gliders que se auto-reparan"** ya están caracterizados autopoiéticamente
   (Beer); reclamar auto-reparación sin clasificar perturbaciones repite con menos
   rigor.
9. **Riesgo de vara:** "genoma nuevo" cuenta un bit distinto en un NOP muerto.
   Flow-Lenia admite el mismo defecto. Sin filtro de persistencia de linaje y sin
   una vara fenotípica de control, la novedad está inflada por construcción.

## 4. Huecos (lo que nadie hizo así)

1. **Muerte por degeneración de la regla** (ciega a la materia bajo sonda) como
   **único** filtro. Todos filtran por sobreescritura, reaper, decaimiento,
   espacio o masa. Nadie usa la persistencia *de la ley*.
2. **Ley cuya FORMA es estado mutable y actúa sobre sí misma dentro de un CA
   espacial local.** Flow-Lenia muta parámetros con kernels fijos; Evoloop y
   Sipper tienen regla externa; BFF no es espacial-local. Y en el Útero la regla y
   la materia están **separadas**, lo que permite preguntar "¿cambió la ley o
   cambió la materia?" — pregunta que BFF no puede formular.
3. **Variación derivada de la materia local, cero RNG, con filtro de muerte.**
   BFF es cero-RNG sin muerte; Stringmol tiene muerte con RNG. Nadie probó "la
   mutación es una función determinista del estado local" y midió si eso se seca
   — nosotros sí, y se seca por un mecanismo nombrable (la misma cría).
4. **Espacio que crece sólo por escritura de una física en el borde.** Ningún
   sustrato revisado tiene topología endógena decidida por un programa.
5. **Auto-reparación sin objetivo anclada a la fertilidad del tejido.** NCA la
   entrena; Sensorimotor Lenia la busca; nadie la reporta como propiedad de un
   tejido evolucionado sin juez ni la ancla a diversidad/viabilidad de las crías.
   Es una instancia medible de la condición 2 de Soros que nadie aisló. **Ahí
   está lo publicable — con n>2 semillas y con las métricas de §5.**

## 5. Lo que la literatura dice sobre nuestro cruce abierto

El cruce: la variación germinal (SPAWN con una mutación desde la materia) se
vuelve determinista cuando la materia se asienta → misma cría, muerta al nacer →
llanuras estériles → sin auto-reparación. Sin RNG y sin fitness, ¿de dónde sale
la variación cuando el fondo se aquieta?

- **Evoloop (1999–2025):** mismo problema; respuestas que funcionaron:
  **colisiones** entre entidades (variación por contacto, no por parto),
  **auto-protección** (que promueve diversidad de especies) y **sexo** por
  intercambio en colisión (Sexyloop). Traducido al Útero: la variación puede
  venir de **COPY de reglas ajenas** (ya tenemos la op) más que de la mutación
  germinal — es decir, de la interacción regla↔regla, no de la materia.
- **Stringmol (2021):** la única línea donde la novedad no se secó, y el motor es
  el **parasitismo**: una regla que explota a otra obliga a la otra a cambiar. En
  el Útero, COPY desde un vecino es parasitismo/sexo en potencia; nunca medimos
  si ocurre ni si sostiene variación.
- **MCC / Soros (2016–2020):** la *strictness* del criterio mínimo (nuestro
  `PROBE_EPS`) decide entre estancamiento y divergencia; el **límite de recursos**
  (cuántos pueden usar el mismo nicho) preserva diversidad. Nuestro vacío es un
  recurso sin límite de uso.
- **Tokyo 2 / Banzhaf:** lo que buscamos es que el *operador de variación*
  evolucione. Con genoma de longitud fija y un solo nivel, la teoría predice
  agotamiento; Stringmol lo vio emerger con parásitos.
- **BFF 2026:** cualquier mecanismo nuevo de variación debe medirse con detector
  directo (aparición vs toma de tejido), o un paseo aleatorio lo explicará.
- **AlChemy:** si la copia trivial satura, la novedad aparece cuando se **inhibe
  la copia exacta**. Nuestra "misma cría" es la copia trivial disfrazada.

**Síntesis:** la literatura converge en que el motor sostenido es **ecológico**
(interacción entre reglas: parasitismo, sexo, colisión, competencia por
recurso limitado), no **germinal** (una mutación mejor en el parto). Antes de
diseñar una variación germinal nueva, conviene medir si el Útero ya tiene
interacción regla↔regla efectiva (COPY entre vecinos distintos) y si la 13 la
tiene y la 35 no.

## 6. Métricas a adoptar para ser comparables (en orden de costo/valor)

1. **Filtro de persistencia de linaje (MODES).** IDs de linaje propagados por
   SPAWN y COPY; contar como "nuevo" sólo lo que tiene descendencia t ticks
   después (t = tiempo de recambio medido). Reportar *novelty* filtrada, *change*,
   *ecology* (Shannon de genomas persistentes por tramo) y *complexity* (nº de
   instrucciones que importan bajo knockout con la propia sonda). Barato: es
   contabilidad sobre lo que ya registramos.
2. **Shadow emparejado (Bedau / Channon 2024).** Misma semilla de orden, mismos
   eventos de escritura, filtro de persistencia sustituido por muerte aleatoria a
   tasa igualada. Reportar A_new y A_cum normalizadas y los pasos 1–3 de Channon.
   Convierte "2/40 semillas" en una tasa de aprobación por paso.
3. **Novedad + aprendibilidad (Hughes 2024).** Compresor o n-grama sobre los
   genomas por tramo; novedad que no baja la pérdida al condicionar en más
   historia = ruido. Formaliza ruido-vs-función.
4. **Detector directo de replicador / toma de tejido (Knierim 2026).** Separar
   "se acuñó un genoma" de "colonizó y persistió".
5. **Vara fenotípica de control** (compresión de video o MSPD): que "genoma
   nuevo" no sea un bit en un NOP muerto.
6. **Barrido de strictness** de `PROBE_EPS` (Soros 2016) y prueba con genoma de
   longitud variable (condición 4).
7. **Autopoiesis operacional (Beer):** dominio cognitivo de las estructuras
   itinerantes; tasas de creación/persistencia/destrucción por tramo. Generaliza
   la ablación.
8. **Pre-vida (Pargellis):** información mutua entre pares de instrucciones en las
   llanuras, como vara de fertilidad medible sin ablar.

## 7. Recomendación (mía, para que Fran decida)

No tocar el sustrato todavía. Dos pasos previos, ambos baratos:

1. **Hacer defendible lo que ya tenemos**: filtro de persistencia de linaje +
   shadow emparejado sobre las corridas existentes (v3/v5, 40 semillas). Si el
   2/40 sobrevive a eso, tenemos un resultado comparable con MODES/Channon; si no,
   nos ahorramos construir sobre una vara inflada.
2. **Medir la interacción regla↔regla que ya existe** (COPY efectivo entre
   vecinos de genoma distinto, por tramo, en 13 vs 35 y en las llanuras vs la
   bomba). La literatura dice que ahí vive el motor sostenido; si la 13 lo tiene y
   la 35 no, la fertilidad de las llanuras tiene un mecanismo y el próximo cruce
   se elige con datos.

Recién después, el cruce de diseño — y con la advertencia de Evoloop/Stringmol
de que la respuesta probablemente sea ecológica (COPY, parasitismo, límite de
uso del vacío), no una mutación germinal más ingeniosa.

## 8. No verificado (confirmar antes de citar)

- Bedau & Packard 1992 (sólo bibliográfico); Varela, Maturana & Uribe 1974 (vía
  McMullin); las cuatro condiciones de Soros & Stanley 2014 (fuentes secundarias);
  Stanley, Lehman & Soros 2017 (existencia sí, contenido no).
- Resultados evolutivos concretos de Hutton 2007 (PDF bloqueado); detalle de
  fitness local y cruce vecinal en Sipper 1996; hallazgos de Bohm, Zhang & Dolson
  2024; Lenia original de Chan (no consultada en esta sesión).
- Nature Reviews Genetics 2025 "Rethinking life through digital evolution"
  (paywall); charla de Agüera y Arcas en ALife 2025 (sólo snippet).
