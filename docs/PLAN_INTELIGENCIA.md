# Plan: del orden a la inteligencia — darle mundo a El Útero

*Escrito 2026-09-26, antes de tocar código. Fran pidió: "sigue avanzando hasta
que consigamos ver un vestigio de inteligencia". Este documento fija qué
contaría como vestigio ANTES de mirar, para que el hallazgo, si llega, no sea
una lectura generosa de un patrón.*

## 1. Diagnóstico

Diecinueve experimentos midieron **novedad**: cuántas formas nuevas acuña el
tejido y si persisten. Eso es orden, en el sentido de Conway. Un tejido puede
acuñar cien mil genomas sin ser más inteligente que una tormenta. Y hay una
razón estructural: **ninguna versión del Útero tiene mundo**. La única presión
es no ser ciego a la materia. Un organismo que no tiene nada que regular no
puede mostrar que regula.

## 2. Definición operativa (sin entrenamiento, sin maestro)

Adoptamos la línea Ashby → Conant y Ashby → Beer: **un sistema es inteligente
en la medida en que su estado interno modela su entorno y usa ese modelo para
seguir siendo.** Cuatro varas, cada una con su control:

| Vara | Pregunta | Cómo se mide | Control |
|---|---|---|---|
| **R. Regulación** | ¿el tejido se sostiene bajo un entorno que cambia? | vivas y novedad persistente a lo largo de los cambios de régimen; amortiguación: varianza de la materia interior / varianza del borde | mismo tejido sin sol; sombra (muertes al azar) |
| **A. Anticipación** | ¿el tejido reacciona ANTES del cambio, donde el cambio es regular? | en estaciones más largas que lo típico, actividad interna alrededor del instante en que el cambio *solía* ocurrir, sin que haya ocurrido | ventanas emparejadas antes de ese instante; sombra; tejido sin sol |
| **L. Aprendizaje por recurrencia** | ¿la respuesta a una estación que vuelve cambia con la repetición? | magnitud de la perturbación interna (muertes + reescrituras) en los primeros 100 ticks de cada ocurrencia de la misma estación: 1ª vs 2ª vs 3ª… | sombra; permutación del orden de ocurrencias |
| **O. Organización** | ¿las estructuras persistentes soportan perturbaciones sin desintegrarse? | dominio de perturbación (Beer): fracción de perturbaciones unicelda que la estructura absorbe | estructuras de la sombra |

**Vestigio** = al menos una de A o L positiva con su control, en ≥ 3 de 40
semillas, con R no negativa (el sol no mata al tejido). A y L son las que
distinguen inteligencia de orden: un cristal falla ambas; una tormenta falla R.

## 3. El sol: un entorno con estructura aprendible

No es una mano que dirige: es clima. La materia del *más allá* (los vecinos
fuera del mundo, que hoy valen 0) sigue una señal externa `s(t)` en `[0,1)`.
El tejido no puede leer el código del sol (no hay código) ni saber cuándo
cambia: sólo siente la materia de su borde.

Estructura de `s(t)`, deterministic y sembrada aparte (el observador la conoce,
el tejido no):
- **Estaciones** en orden fijo y cíclico: A (calma, nivel bajo), B (día largo,
  amplitud alta), C (día corto, nivel medio). El orden es la regularidad
  aprendible: después de A siempre viene B.
- **Duraciones** de cada estación tomadas de un mapa logístico (r=3.9) escalado
  a `[300, 900]` ticks: típicas pero impredecibles desde la señal. Eso hace
  medible la anticipación: en una estación *larga*, el instante típico de cambio
  pasa sin que el sol cambie; si el tejido "esperaba" el cambio, se nota.
- **Día**: dentro de cada estación, `s(t) = base + amp·(0.5+0.5·sin(2πt/T))`
  mod 1, con `T` propio de la estación.

Manos declaradas: la forma de `s(t)`, sus tres regímenes, el rango de
duraciones. Se barren en el control (§6).

## 4. Sustrato

Se parte de la mejor encarnación 1-D conocida (memoria + invasión asentada,
`eq_window=100`): es la que mantiene vivos los mundos (246 celdas contra 12)
y la más barata de correr con 40 semillas y sombra. El plano (v8) queda como
segunda etapa si el 1-D no muestra nada: tiene más estructura espacial y el
sondeo dio mucha más novedad, pero cuesta veinte veces más por corrida.

Flag `sol=Sol(...)` en `UteroCreciente` (y luego `UteroPlano`): el más allá
devuelve `s(t)` en vez de 0. `sol=None` byte-idéntico (test).

## 5. Fases

1. **Sol + varas** (`utero/sol.py`, `utero/inteligencia.py`, tests):
   generador de estaciones; extracción de series internas por tick (vivas,
   muertes, reescrituras, materia media interior y de borde, novedad); las
   cuatro medidas con sus controles.
2. **Experimento `exp_utero_sol.py`** (1-D, 40 semillas, 20000 ticks: ~25
   estaciones por corrida): brazos *sol* vs *sin sol*, sombra para *sol*;
   veredicto pre-registrado (§2). Si hay vestigio: replicar con otro sembrado
   del sol y con el orden de estaciones permutado (¿aprende ESE orden o
   cualquier cosa?).
3. **Si no hay vestigio en 1-D**: el plano con sol (una cara de la placa es el
   sol), 20 semillas.
4. **Si hay vestigio**: profundizar en el mecanismo (¿qué celdas lo portan?,
   ¿sobrevive a la ablación?) y buscar la vara O sobre las estructuras que lo
   portan.

## 6. Controles obligatorios antes de creer

- **Sombra**: muertes al azar en vez de sonda, mismo sol. Lo que la sombra
  "anticipa" es artefacto de la señal.
- **Tejido sin sol**: descarta que la "respuesta" sea dinámica interna
  periódica que coincide por azar.
- **Permutación**: para L, barajar el orden de las ocurrencias antes de medir
  la tendencia; para A, sembrar otro sol con otras duraciones.
- **Reflejo**: un modelo sin memoria del sol (`x_t = f(s_t)`) no puede pasar A
  ni L por construcción; si nuestras medidas se lo atribuyen, están mal.
- **Barrido de manos**: rango de duraciones y amplitudes del sol.

## 6b. Enmienda (2026-09-26, tras la réplica): la vara del vestigio era débil

La corrida 2 disparó "vestigio" con 3/40 al 5%: la tasa nominal ya da 2, y la
réplica lo mostró falso positivo (sol1 3, sol2 2, permutado 6, 8/120 contra 6
esperados). Para toda corrida posterior a esta enmienda:

- **Vestigio por conteo** exige p binomial < 0.05 contra la tasa nominal
  (≥ 5/40) Y ≥ 2× el máximo de los controles Y ≥ 2× el brazo con orden
  permutado (el control que quita la regularidad y deja todo lo demás igual).
- **Condición de contacto previa**: el estadístico de anticipación dispara en
  tejidos que no sienten el clima (muertes 0 en maduro). Antes de leer A o L,
  el brazo debe mostrar respuesta al inicio de estación (muertes post/pre ≥
  1.2 en mediana); si no, el resultado se lee como "sin contacto".
- Las corridas ya lanzadas conservan su regla pre-registrada; la enmienda se
  aplica a las siguientes y se declara en cada docstring.

## 7. Reglas de parada honestas

- Si tras las fases 2 y 3 no hay vestigio: se reporta como negativo con el
  mismo cuidado que los anteriores, y el paper cierra con "novedad sí,
  inteligencia no medible en este sustrato con este entorno".
- Nunca se relaja una vara después de mirar. Si una vara resulta mal
  diseñada, se declara (como la cuota de v6) y se corrige en un experimento
  nuevo, no en el mismo.


## 8. Estado al cierre de la sesión 2026-09-26

Fases 1–3 ejecutadas y extendidas: ocho diseños pre-registrados (sol visible,
sonda climática, réplica, calor, plano, disolución, metabolismo, percepción),
todos negativos por sus propias reglas; un falso positivo detectado por la
réplica; vara enmendada (§6b). Regla de parada de §7 aplicada: se reporta como
negativo con el mismo cuidado que los anteriores. Lo que un intento futuro
debería cambiar, según lo medido: (a) variables internas lentas y legibles
diseñadas desde el sustrato, no añadidas; (b) un régimen que no sea ni cristal
(sin costo) ni recambio total (con costo), calibrado por la escala temporal
interna frente a la del clima; (c) el plano, por su superficie de contacto y
su no-cristalización, como sustrato base del programa. Ver ledger en
`EL_UTERO.md` y `results/utero_sol_*_run.txt`.

## 9. Estado al segundo cierre (misma sesión, tras la orden de seguir)

Cuatro diseños más (v9 metabolismo, v10 percepción, v11 fotosíntesis ×2, v12
luz finita ×4). v12 —capacidad de carga estacional— dio por primera vez un
régimen intermedio real (población que sigue a la estación, muertes
concentradas en la hambruna) y dos lecturas tentadoras (ahorro antes de la
hambruna: 9/40 y 5/40) que sus réplicas y el brazo permutado desmontaron como
artefacto de acumulación. Trece corridas, cero vestigios. Lección de método
añadida a §6b: toda lectura sobre una serie que se acumula dentro de la
estación (energía, población) debe usarse SIN deriva (residuo respecto de la
tendencia previa) y compararse contra el brazo permutado, no sólo contra sin
sol y sombra.

## 10. Cierre definitivo de la sesión 2026-09-26

v13 (registros lentos, τ = 300, sobre la ecología de v12): NADA; la
anticipación sobre actividad dispara igual en el brazo permutado (7 vs 5) y las
lecturas de energía sólo en él (10 y 9). Catorce corridas, trece diseños, cero
vestigios, cuatro señales desmontadas. Lo que un programa futuro debería
cambiar no es un mecanismo más sino la pregunta: buscar la regulación en
entidades (estructuras itinerantes, Beer) y no en el tejido entero, con un
entorno cuya regularidad tenga la escala temporal de esas entidades; y
construir primero el POSITIVO CONTROL —un organismo diseñado a mano que sí
anticipe en este sustrato— para saber que las varas pueden verlo.

## 11. El control positivo (2026-09-26)

Un anticipador diseñado a mano (detector de estación en un registro lento +
SPAWN auto-reescrito según la estación) es viable (18/20), estable bajo
mutación y muere en la hambruna la mitad que el tejido evolucionado, y un 58%
menos bajo el orden regular que bajo el permutado. Las varas A/L no lo ven:
buscan cambios anclados al instante esperado y un reflejo estacional no los
produce. R2 (mortalidad en la hambruna, regular vs permutado) sí. Enmienda:
R2 pasa a ser la lectura PRIMARIA de regulación en esta ecología; A/L quedan
como lecturas de anticipación temporal fina. Siguiente y último paso: invasión
desde raro (¿la selección favorece al ahorrador frente al tejido
evolucionado bajo el orden regular y no bajo el permutado?).

## 12. Invasión desde raro y cierre (2026-09-26)

El ahorrador diseñado no es seleccionado frente al tejido evolucionado: toma
4–5/20 con y sin costo de parto, con y sin regularidad de orden, en las mismas
semillas (colapsos de la población aleatoria, no selección). La explicación de
los dieciséis negativos es mecánica: esta ecología no selecciona la
anticipación. Un entorno diseñado para seleccionarla equivaldría a elegir la
respuesta: es una decisión de programa, no de ejecución. Programa cerrado.

## 13. Evolución experimental bajo un régimen declarado (v14)

Corrijo un argumento propio de §12: elegir el régimen selectivo no es elegir
la respuesta, es elegir la PREGUNTA (evolución experimental). La respuesta
—¿un tejido de genomas aleatorios desarrolla comportamiento regulado por la
estación?— sigue abierta y se mide contra los mismos controles (sin sol,
sombra, orden permutado, segundo orden cíclico). El régimen: luz casi nula en
A (base 0.08, calibrada por viabilidad estacional en 6 semillas × 9
configuraciones: 5/6 viven, N cae en A y se recupera, partos en A ≈ 0) y
parto costoso (e_costo = 1.0). Nada sembrado. Lectura primaria: R2_A, la
mortalidad durante la hambruna bajo el orden regular contra el permutado,
pareada entre mundos vivos, con ciclo2 como control de tipos de transición.
Un tejido que regula según la estación previa muere menos cuando la hambruna
sigue siempre a la estación templada. Secundarias: estructura de partos A/B y
las lecturas de anticipación con la vara enmendada.

**Corrida 1 (sol seed 0):** NADA. R2_A no (clima < permutado en 7/26 pares
vivos; razón 1.21: la hambruna mata más bajo el orden regular, no menos);
partos A/B 0.01 en todos los brazos; las lecturas de anticipación en clima al
nivel de los controles. Dos fallas propias, registradas: el código de veredicto
sólo evaluó clima (corregido), y una lectura post hoc en el brazo ciclo2 —A_n =
9/40— comparaba estaciones B largas contra brazos que miran C o todas
(`PRECEDE_A`): no compara iguales. Réplica declarada antes de correr: sol seed
1, ciclo2 como brazo evaluado, A_nD (sin deriva) y A_nB/A_nBD (la misma lectura
sobre B largas en todos los brazos; donde a B no le sigue la hambruna, un valor
alto es saturación demográfica). Se cree sólo si A_n y A_nD cumplen en ciclo2
y superan 2× ese control emparejado.

**Corrida 2 (réplica, sol seed 1): NADA.** A_n en ciclo2 2/40 (era 9/40), A_nD
0/40, A_nB 2/40; R2_A no en ambos brazos regulares. Falso positivo de
calendario. Balance del programa: 17 corridas pre-registradas de emergencia
sobre 14 diseños, un control positivo, dos ensayos de invasión, cinco señuelos
cazados por réplica o control. La explicación mecánica de §12 sigue en pie y
v14 la refuerza: aun con hambruna dura y parto costoso, la mortalidad en la
hambruna no es menor bajo el orden regular. La población se derrumba en A y
recoloniza en B sea cual sea el orden; sobrevivir a la hambruna no otorga
descendencia porque el vacío se rellena igual de rápido desde cualquier
superviviente.

## 14. Tierra quemada: selección K (v15, 2026-09-26)

La cadena de §12–§13 termina en una frase mecánica: sobrevivir a la hambruna
no da descendencia porque el vacío se rellena igual de rápido desde cualquier
superviviente. Si esa frase es la explicación, tiene una consecuencia
comprobable: un mundo donde el vacío NO se rellena rápido —el lugar de una
celda muerta queda quemado T ticks— debería convertir la supervivencia en
territorio y, con ello, hacer seleccionable cualquier regulación interna que
baje la mortalidad en la hambruna. Es un cambio del mundo, no del tejido, y
sigue siendo una pregunta (¿emerge?), no una respuesta sembrada. `refractario`
en `UteroCreciente`, byte-idéntico apagado, tests en `test_utero_refractario`.
T = 300 declarado tras calibración (todas las T viables; 600 perdía el
contacto). Mismos brazos, lecturas y veredicto que v14 corrida 2. Si NADA: la
recolonización rápida no era el cuello de botella, y la explicación mecánica
debe revisarse hacia el CAMINO mutacional (la anticipación diseñada es viable,
pero ninguna trayectoria de MUTO/COPY la alcanza desde genomas aleatorios).

**Resultado v15: NADA.** R2_A no en clima (5/25, razón 1.29) ni en ciclo2
(7/25, 1.16); L_A 6/40 y A_m 6/40 en clima con controles a 3–8. Con esto la
explicación "sobrevivir no da descendencia porque el vacío se rellena rápido"
queda refutada como cuello de botella único: aun cuando el lugar se conserva
sólo sobreviviendo, no emerge nada que baje la mortalidad en la hambruna bajo
el orden regular. Queda en pie la otra mitad de §12: el CAMINO. El anticipador
diseñado es viable y ventajoso; la pregunta es si alguna trayectoria de
MUTO/COPY lo alcanza desde genomas aleatorios, o si las instrucciones que lo
componen son individualmente neutras o letales (un valle). Eso se mide sin
evolucionar: §15.

## 15. La cuarta jaula: la variación no escribe operandos (2026-09-26)

Hecho estructural, leído en el VM y medido: MUTO, el germinal, COPY y SPAWN
sólo cambian opcodes o trasladan filas enteras que ya existen. Ningún camino
escribe los campos a, b, c. El conjunto de tríos de operandos de un mundo es
el de su sopa inicial —6.06% de los 4096 posibles— para siempre. Sobre las 40
semillas de v14/v15, sólo 3 sopas contienen los operandos de todas las piezas
del ahorrador (cota superior; Monte Carlo poblacional 0.157), antes de
ensamblarlas con COPY, cuyos operandos también están congelados.

Corrige la explicación mecánica de §12–§14: no es que la ecología no
seleccione la anticipación ni que la recolonización la borre; es que la
variación no puede componerla. Dieciocho corridas buscaron emergencia en un
espacio donde tres de cada cuatro campos del programa estaban fijos desde el
tick 0. La jaula está en la variación.

Respuesta (v16, `escritura_total`): MUTO y el germinal escriben la
instrucción ENTERA desde los registros —opcode desde |R_b| como siempre, y
a, b, c desde |R_{b+1}|, |R_{b+2}|, |R_{b+3}| (mod m), escalados a 16—. Sigue
sin haber RNG nuestro: la materia escribe el programa completo. Abre el
espacio; no siembra ninguna respuesta. Pre-registro: misma ecología, brazos,
lecturas y veredicto que v14 corrida 2; calibración previa por viabilidad
(la apertura puede volver letal la mutación).

**Calibración v16** (6 semillas × {apagado, encendido}, 12000 ticks): viable
(5/6 vivas, N_A 29 vs 22, contacto conservado) y abierto de verdad: 16656
genomas nunca vistos por mundo contra 198 (84×), 52 tríos de operandos nuevos
contra 0. La semilla 13 se extingue con el flag (la apertura también hace
letal la mutación). Lanzado tal cual, sin ajustar nada más:
`exp_utero_total.py`.

**Resultado v16: SIN CONTACTO / NADA.** Muertes post/pre 0.92 en clima (el
recambio continuo de la variación abierta tapa la hambruna); R2_A no (2/22,
1.30); L_A 1/40. Con el espacio abierto tampoco aparece adaptación medible en
30000 ticks con ~30 vivas (~300 generaciones, ~9000 partos por mundo, ~15
hambrunas). La evolución experimental real opera sobre 10³–10⁴ generaciones y
poblaciones de 10³+. Siguiente (§16): antes de buscar regulación, establecer si
el sustrato abierto EVOLUCIONA —adaptación refleja a la hambruna: la
mortalidad en hambrunas sucesivas baja dentro de un mundo (L_A), visible en
clima y permutado y no en sombra— con más tiempo y más población.

## 16. Escala: ¿evoluciona el sustrato abierto? (2026-09-27)

Pregunta previa a la de regulación: con la variación capaz de escribir el
programa entero, ¿aparece adaptación —del tipo que sea— con más tiempo y más
población? 120000 ticks (4×), L0 = 9 (≈3× vivas), 20 semillas, brazos clima /
permutado / sombra. Adaptación refleja = la mortalidad en las hambrunas
tardías es menor que en las tempranas dentro del mismo mundo; no necesita
regularidad, así que se cuenta en clima y permutado juntos, contra la sombra
(muertes al azar en igual número: la demografía sola). R2_A sigue midiendo
regulación por el orden. Si EVOLUCIONA sin vestigio, la pregunta pasa a ser
sólo de tiempo; si NADA, la variación abierta es letal o neutra y lo siguiente
es medir su espectro de efectos (¿qué fracción de escrituras totales deja una
cría viable?), no otra ecología.

**§16b, espectro de la variación (medido antes del resultado de la escala):**
abierto = 23 variantes viables y distintas por 1000 ticks por mundo (21% de las
crías distintas sobreviven 500 ticks; 71% de los cambios tocan operandos);
cerrado = 9 (99% sólo opcode, 5% sobreviven). La oferta mutacional existe: si
§16 da NADA, hay que medir el EFECTO de las variantes sobre la mortalidad en
la hambruna, no la oferta.

**Resultado §16: NADA** (R2_A 2/14; L_A 0/40) y la lectura de adaptación
resultó confundible: la razón tardía/temprana de muertes por tick baja también
en la sombra porque la sombra se extingue. Corrección de método, declarada:
(a) mortalidad en la hambruna PER CÁPITA (muertes / vivas medias en A);
(b) el nulo de "¿evoluciona?" no es la sombra (extinta en v14–§16) ni el orden
permutado (allí también puede haber adaptación), sino un brazo CONGELADO: la
misma ecología con MUTO y COPY inertes y sin germinal, es decir, sin herencia
de cambios. Si la mortalidad per cápita en hambrunas tardías baja en el brazo
abierto y no en el congelado, el sustrato evoluciona; si baja igual en ambos,
es ecología (recambio, densidad), no evolución. §17.

## 17. ¿Evoluciona? El nulo congelado (2026-09-27)

`congelado=True`: MUTO y COPY inertes, el germinal no escribe. Misma sopa,
misma física actuando sobre la materia, misma ecología y demografía; nada
nuevo se hereda. Es el único nulo real para "¿evoluciona?" (la sombra se
extingue; el permutado también puede adaptarse). Lectura primaria: mortalidad
per cápita en la hambruna, tardía / temprana, pareada por semilla contra el
congelado, en el brazo abierto (v16) y en el cerrado (v14). Si EVOLUCIONA en
el abierto y no en el cerrado, la cuarta jaula era el cuello y la línea sigue
(más tiempo, luego regulación). Si NO EVOLUCIONA en ninguno con 23 variantes
viables por 1000 ticks, las variantes no difieren en lo que la hambruna mide:
lo siguiente es medir qué rasgo heredable varía entre linajes (fenotipo), no
correr más.

**Resultado §17: NO EVOLUCIONA.** Razón tardía/temprana per cápita: congelado
0.19, abierto 0.45, cerrado 0.62; abierto < congelado en 3/14 pares, cerrado
6/16. La caída es ecológica y la variación heredable no la mejora: en el brazo
abierto la mortalidad per cápita en A es mayor (0.73 vs 0.60). Conclusión de
método para toda la línea: **el sustrato no evoluciona bajo esta ecología**,
con o sin la cuarta jaula abierta. La búsqueda de inteligencia presuponía
evolución; la evolución presupone un fenotipo heredable con varianza sobre el
que el filtro discrimine. §18 mide eso directamente: entre las celdas vivas
al empezar cada hambruna, ¿la supervivencia se predice por el genoma (ICC
entre portadores del mismo genoma contra un nulo por permutación de destinos)
y se repite para el mismo genoma en hambrunas sucesivas?

## 18. ¿Hay fenotipo heredable? (2026-09-27)

La cadena de esta noche: no hay regulación (18 corridas) → no hay adaptación
(§17, contra el nulo congelado) → ¿hay siquiera algo heredable sobre lo que la
hambruna discrimine? Se mide sin evolucionar: entre las vivas al empezar cada
hambruna, si sobrevivir se predice por el genoma, por el estado (energía,
borde) o por nada. Tres salidas con consecuencias distintas: HEREDABLE →
el problema es intensidad de selección frente a carga (medir ventaja y tiempo
de fijación); ESTADO → la hambruna mata por dónde y con cuánto, no por qué
programa: ninguna cantidad de tiempo produce adaptación y hay que cambiar qué
mide el filtro o cómo el genoma fija el estado; NADA → muerte al azar.

**Resultado §18: NADA por la letra (denominador de 20 con 5–7 extinciones),
ESTADO con componente heredable por la evidencia.** Energía predice el
destino en la hambruna en 13/13 y 13/15 mundos utilizables; genoma en 7/13 y
9/15, repetible entre hambrunas (8/10, 14/15). Conclusión operativa del
programa, con toda la cadena de la noche: el sustrato tiene variación
heredable en lo que la hambruna mide, pero no la convierte en adaptación
(§17). Las dos hipótesis que quedan —canje supervivencia/fecundidad, o
genoma como proxy de posición— exigen registro por celda (linaje, posición,
energía, partos) y una medida de selección directa (covarianza de Price entre
genoma y descendencia). Eso, o cambiar qué mide el filtro, es una decisión de
programa.

## 19. Estado al cierre de la sesión 2026-09-27

- Regulación por el orden del entorno: 19 corridas pre-registradas, 0
  vestigios, 5 señuelos cazados por réplica o control.
- Cuarta jaula (clausura de operandos) hallada, medida y abierta (v16); la
  apertura no cambió el resultado.
- El sustrato NO EVOLUCIONA bajo esta ecología (§17, contra nulo congelado),
  aunque la oferta de variantes viables es suficiente (§16b) y hay componente
  heredable y repetible en la supervivencia a la hambruna (§18).
- Errores de método propios registrados: veredicto de un solo brazo, lectura
  de nivel confundida con demografía, sombra extinta como control, denominador
  con extinciones.

## 20. El bien común: ¿la difusión de energía neutraliza la selección? (2026-09-27)

Hipótesis que une §17 y §18: con difusión conservativa de energía (e_dif =
0.25) la reserva de cada celda es en buena parte la de su vecindario; un
programa que ingresa más reparte la ganancia y la hambruna mata según la
reserva local, no según el programa. Selección individual neutralizada por
un bien común. Prueba: §17 con e_dif = 0. Si EVOLUCIONA, el sustrato sí
evoluciona cuando la reserva es privada, y la línea vuelve a la regulación
con esa ecología; si NO, la difusión no era la causa y quedan el canje
supervivencia/fecundidad y la posición, que sí exigen registro por celda.

**Resultado §20: NO EVOLUCIONA** (abierto 0.54 vs congelado 0.82 en 9/16
pares, p 0.40). La difusión no era la causa principal. Dos hipótesis quedan y
las dos se prueban barato:
- §21 ¿La selección ve los genomas? Réplicas del mismo mundo CONGELADO (misma
  sopa) con distinto orden de actualización (`orden_seed`): si la abundancia
  final de los 16 genomas iniciales concuerda entre réplicas (Kendall W contra
  nulo por permutación), la selección es determinista sobre el programa; si
  no, lo que decide es la posición y el azar.
- §22 Tasa de mutación. El germinal escribe en cada parto: ≈1 mutación por
  generación con efectos fuertes sobre 16 loci, por encima del umbral de error
  (Eigen) para casi cualquier paisaje; la carga de §17 (el brazo abierto muere
  más) es la firma. `tasa_germinal=p`: la cría recibe la escritura germinal
  sólo si la fracción de |R_b| es < p (determinista desde la materia; mano
  declarada). §17 con p = 0.1 y 0.02.

## 21–22. Réplicas de selección y tasa de mutación (2026-09-27)

Implementados `orden_seed` y `tasa_germinal` (byte-idénticos apagados). §21
corre 10 sopas × 5 órdenes en mundos congelados y mide la concordancia de la
abundancia final de los 16 genomas iniciales (W de Kendall contra nulo por
permutación): SELECCIÓN si ≥ 8/10 sopas concuerdan, POSICIÓN si ≤ 3/10. §22
repite §17 con escritura germinal rara (p = 0.1, 0.02): si evoluciona con
p < 1 y no con p = 1, la tasa de mutación era el cuello (umbral de error).

**Resultado §21: SELECCIÓN 10/10.** El mismo genoma barre en las 5 réplicas
en 9/10 sopas (share 1.00). La selección sobre programas fijos es
determinista y fuerte. Con §17 (sin adaptación bajo herencia de cambios) la
inferencia es directa: la variación destruye lo que la selección construye.
Predicción para §22: con p = 0.1 o 0.02 el brazo abierto evoluciona.

**Resultado §22: NO EVOLUCIONA por la regla**; tendencia graduada (la carga
cae con la tasa: 0.73 → 0.69 → 0.49 contra 0.60 congelado; p=0.02 menor que
congelado en 12/18, p 0.12). La tasa explica la carga, no la ausencia de
adaptación en la vara de hambruna. Hipótesis restante y decisiva: la vara.
§21 muestra selección fuerte sobre programas fijos, y lo que barre es
seguramente el mejor colonizador. La adaptación, si existe, es en capacidad
competitiva. §23 la mide como la evolución experimental: competencia en
jardín común del genoma evolucionado contra su ancestro.

## 23. Jardín común (2026-09-27)

Evolucionado contra ancestro en mundo congelado, dos disposiciones, 20
semillas, regímenes p = 0.02 y p = 1. ADAPTA / DEGRADA / NEUTRAL escritos
antes de correr. Si ADAPTA en p = 0.02, el sustrato evoluciona en el rasgo
que la ecología selecciona y la línea vuelve a la regulación por el orden
con ese régimen; si NEUTRAL o DEGRADA, la variación no mejora la
competitividad en 120000 ticks y el paisaje alrededor del mejor programa fijo
es plano o descendente.

**Resultado §23: NEUTRAL**, y el patrón (1.00, 0.00) por disposición en casi
la mitad de las semillas muestra que la competencia la decide la posición.
Releído §21 a esa luz: sus réplicas no movían las posiciones. Hipótesis
principal ahora: en la línea con frontera abierta la reproducción es un
efecto fundador espacial (quien toca el vacío llena el espacio), no una
función del programa; por eso la selección no ve genomas y nada se adapta.
§24 lo prueba barajando posiciones; si se confirma, el cambio necesario es
estructural (cerrar la frontera para que la competencia sea interior, o
cambiar la topología), no ecológico.

## 24. Posición o programa (2026-09-27)

Réplicas congeladas con posiciones barajadas (mismo conjunto de genomas,
mismo orden), en frontera abierta y en frontera cerrada (n0 = max_n = 64).
PROGRAMA / POSICIÓN / MIXTO por ecología, escritos antes de correr. Es la
prueba directa de la hipótesis que sobrevivió a todo lo demás: en la línea
con frontera abierta la reproducción es efecto fundador espacial.

**Resultado §24: PROGRAMA en ambas** (abierta 9/9, cerrada 10/10). La
selección ve programas; la posición sólo desempata entre iguales (§23). Con
oferta mutacional suficiente y selección fuerte, la ausencia de adaptación
apunta a un techo de aptitud bajo y alcanzable al azar en la frontera abierta
(colonizar cada tick). En la ecología cerrada coexisten 5–11 genomas con
ranking reproducible: allí la competencia es interior y puede haber gradiente.
§25: §17 en la ecología cerrada (n0 = max_n = 64), brazos abierto p = 0.02,
cerrado, congelado; misma lectura primaria y regla.

**Resultado §25: SIN CONTACTO** (mortalidad per cápita en A 0.004–0.006: la
hambruna no mata en la ecología cerrada con L0 = 9). Hipótesis de fondo: la
sonda aplana el gradiente de ingreso (los programas legales tienen materia
pseudoaleatoria → mismo ingreso esperado). §26: (a) calibrar luz escasa en la
ecología cerrada hasta que la hambruna muerda; (b) control positivo del
gradiente: sembrar un programa anti-sol legal (v = vecino + 0.5) en mundos
congelados y ver si gana; (c) si gana, evolvabilidad con variación abierta en
esa ecología; si no gana, el gradiente no existe y hay que cambiar el filtro.

## 26. Control positivo del gradiente de ingreso (2026-09-27)

¿Un programa legal con más ingreso de luz gana cuando la luz escasea? ANTISOL
(materia a distancia 0.5 del sol de la hambruna) contra ESPEJO (misma forma,
ingreso al azar), 4 + 4 sembrados entre 56 al azar en la ecología cerrada,
congelada, con L0 = 1.75. GRADIENTE / SIN GRADIENTE / MIXTO escritos antes de
correr. Si hay gradiente, la ausencia de adaptación es de camino (la
variación no llega a programas así) o de vara, y lo siguiente es medir la
alcanzabilidad de ANTISOL desde la sopa con escritura total; si no lo hay,
la sonda aplana el ingreso o el ingreso no manda, y hay que cambiar el
filtro o la ecología.

**Resultado §26: GRADIENTE 17/20** (ANTISOL barre al 100% en 15/20 antes de
10000 ticks; ESPEJO 0.00). La sonda no aplana el ingreso; el gradiente existe
y la selección lo ve. Queda el CAMINO o la VARA. §27 mide directamente el
rasgo premiado —peso de luz medio de la materia durante la hambruna— en
poblaciones con variación abierta contra el congelado, en la ecología cerrada
con luz escasa: si sube, el sustrato evoluciona y la vara de mortalidad era
ciega; si no sube, la variación no alcanza el rasgo (camino) y lo siguiente es
medir la alcanzabilidad de la materia anti-hambruna desde programas legales.

## 27. ¿Sube el rasgo premiado? (2026-09-27)

Primera medida de evolución sobre un rasgo que la selección premia de forma
demostrada (§26). Peso de luz de la materia durante la hambruna, tardío /
temprano y nivel, pareado contra el congelado, cuatro brazos. ADAPTA / NO
escritos antes de correr. Si sube: el sustrato evoluciona y la vara de
mortalidad era ciega; la regulación por el orden se vuelve a medir aquí. Si
no: camino —la variación no alcanza la materia anti-hambruna—, y se mide la
alcanzabilidad desde programas legales.

**Resultado §27: NO EVOLUCIONA.** El rasgo premiado no se mueve (0.30–0.34,
razón 1.00, 59 hambrunas, cuatro brazos). Camino. §28 mide la alcanzabilidad
sin evolucionar: distribución de Δw̄ en el vecindario a una y dos escrituras
de programas legales del tejido evolucionado (fracción de vecinos viables
con Δw̄ ≥ +0.1 y ≥ +0.2; máximo alcanzable), comparando escritura total con
sólo opcode. Si no hay saltos grandes, el rasgo sólo se alcanza por pasos
pequeños que con N ≈ 14 son neutros: el paso constructivo es la población
efectiva (línea cerrada grande o el plano), no otra ecología. Si hay saltos
grandes y aun así no se fijan, hay que mirar la viabilidad en contexto de
esas variantes (mueren al nacer por otra razón).

## 28–29. Alcanzabilidad y población efectiva (2026-09-27)

§28 (sin evolucionar): en 20000 escrituras totales sobre programas legales
del tejido, ninguna mueve el rasgo premiado +0.2 y sólo el 0.19% lo mueve
+0.1; la mediana es 0. El paisaje es una meseta neutra con escalones raros y
pequeños. Con N ≈ 14, esos escalones son neutros. §29: §27 con la línea
cerrada de 512 lugares y L0 = 14 (misma luz por lugar), brazos abierto p = 1,
cerrado y congelado, 12 semillas, 120000 ticks; misma lectura y regla que
§27. Si el rasgo sube con N ×8, la evolución en el útero estaba limitada por
la deriva, y el camino a la regulación es población y tiempo; si tampoco,
queda el paisaje mismo (la meseta neutra) y hay que cambiar cómo la materia
sale del programa, no la ecología.

**Resultado §29: NO EVOLUCIONA en el rasgo** (w̄_A 0.37 en los tres brazos
con N ≈ 150); el congelado acumula más banda anti-hambruna (0.55) que los
brazos con herencia: la variación arrastra el rasgo de vuelta. Secundaria
inesperada: mortalidad per cápita en la hambruna 0.14 (abierto) contra 0.96
(congelado), con cerrado intermedio (0.29). Dos lecturas: carga mutacional
que baja la fecundidad y deja reserva (probable), o reproducción regulada
(vestigio). §30: N = 512 con tasa germinal 0.02 y 0.005 (contra congelado),
lectura primaria el rasgo; secundarias: partos per cápita por estación (B y
A) y mortalidad; si la mortalidad baja con MENOS mutación (no más), no era
carga.

**Resultado §30: NO en el rasgo; la mortalidad en la hambruna del brazo
p = 0.02 es menor que la del congelado en 12/12 mundos (0.15 contra 0.96) y
su caída entre hambrunas en 11/12 (p 0.003). La regla de carga no se cumple;
la de regulación sí, justo en el umbral (A/B 9/12).** Confusor no
pre-registrado: densidad (138 contra 176 vivas; con luz finita, menos vivas =
más reserva). §31: el control de densidad. Brazos: abierto p = 0.02;
congelado; congelado-sombra con muertes al azar fuera de A iguales en número
a las del brazo abierto de la misma semilla y ninguna impuesta durante A (la
misma densidad sin herencia). HEREDABLE si la mortalidad per cápita en A del
abierto es menor que la del congelado-sombra en ≥ 75% de los pares (p signo
< 0.05) con razón mediana ≤ 0.5; DENSIDAD si ≤ 50% de los pares. Si
HEREDABLE: primer candidato a vestigio de la línea (una población que, por
herencia, muere menos en la hambruna sin que el rasgo de luz cambie); el
paso siguiente sería identificar el mecanismo (partos, energía al entrar en
A, invasión) y replicar con otro sol.

**Resultado §31: DENSIDAD** (igualado 0.18 contra abierto 0.15, razón 0.79,
7/12; la densidad sola da 11/12 contra el congelado). La señal de §30 era
carga convertida en densidad. Sin vestigio. Cierre del diagnóstico: el único
cuello no descartado es el paisaje (§28). §32: alcanzabilidad con escrituras
INCREMENTALES (±1 en un solo campo) contra totales, con el arnés de §28; si
dan una escalera más densa de pasos pequeños positivos, se implementa el
operador incremental como flag y se corre la escalada (§33).

**Resultado §32: SIN ESCALERA** (incremental 0.27% contra total 0.22% para
Δw̄ ≥ +0.05; cero para +0.2). Quinta jaula: el mapa programa→materia no tiene
localidad. §33 (v17, `parametros`): desplazamiento heredable continuo θ sumado
a la materia, perturbado al nacer desde la materia de la madre; brazos θ +
programa abierto (p = 0.02), θ solo (programas congelados, θ heredable), y
congelado total (θ copiado exacto: el nulo). Lectura primaria: w̄_A con la
regla de §27, más la trayectoria de θ̄ en A. Si ADAPTA: primera evolución
real del útero; la regulación por el orden se vuelve a preguntar sobre ese
sustrato. Si no: ni con un mapa local, y el problema está más abajo.

**Resultado §33: NO EVOLUCIONA** (w̄_A 0.38–0.40 contra 0.385 del nulo).
Error de diseño: un desplazamiento no cambia la distancia media al sol de una
materia pseudoaleatoria; el rasgo premiado es la dispersión. v17b (`escala`):
materia visible = (θ + s·salida) mod 1 con s heredable; la sonda sigue viendo
la salida cruda. §34: mismo diseño que §33 con θ y s heredables contra el nulo
(θ y s fijos); lectura primaria w̄_A, secundarias s̄ y R_θ.

## 34–35. Primera evolución medida y su réplica (2026-09-27)

**§34: EVOLUCIONA en theta_s_solo** (10/12 y 10/12, p 0.019; w̄_A 0.434
contra 0.385; s̄ 0.71). La cadena de la noche encontró el cuello real y su
respuesta: la selección era fuerte y el gradiente real, pero la variación no
tenía escalera porque la materia de un programa legal es pseudoaleatoria y
un cambio de programa no la mueve de a poco. Dos perillas heredables
continuas sobre la EXPRESIÓN de la física —no sobre la física— bastan para
que la selección actúe. Es evolución, no inteligencia: dos números que se
ajustan a un gradiente fijo. §35 réplica (sol seed 1, sopas 12–23, misma
regla): si replica, §36 vuelve a la pregunta original sobre este sustrato:
¿un tejido que evoluciona desarrolla regulación según el ORDEN de las
estaciones (R2_A, anticipación) y no sólo según la estación presente? Para
eso θ y s tendrán que poder ser escritos por el programa (perillas de
comportamiento, no sólo de herencia), lo que se decide después de la réplica.

**§35: REPLICA (10/12, 10/12, p 0.019; 0.423 contra 0.363). Se cree.**

## 36. La pregunta del orden sobre un sustrato que evoluciona (2026-09-27)

Con θ y s sólo heredables, un linaje no puede cambiar su expresión en vida:
hay adaptación pero no comportamiento. §36 hace las perillas ESCRIBIBLES por
el programa (`perillas=True`): θ_eff = (θ + S1) mod 1 y s_eff = clip(s + S2)
con S1, S2 los registros lentos que la física empuja despacio (τ = 1/λ), y
da al tejido interior un sentido de la estación (`percepcion=True`: la
energía como registro). La herencia (θ, s) pone la línea de base; la física
puede moverla según lo que siente y recuerda. Pregunta pre-registrada (la de
§6b/§13, ahora sobre un sustrato evolucionable): ¿el tejido bajo el orden
regular muere en la hambruna menos que bajo el permutado (R2_A), y no por el
tipo de transición (ciclo2)? Brazos: clima, ciclo2, permutado (todos
theta_s_abierto + perillas + percepción) y nulo (clima, θ y s fijos,
programas congelados). Lectura primaria R2_A con la regla de v14; secundarias
w̄_A, s̄_A, partos A/B, uso de las perillas (varianza de S1, S2 en vida).
VESTIGIO si R2_A cumple en clima y ciclo2; si sólo en clima, tipos de
transición; NADA en otro caso. Si VESTIGIO: replicar con otro sol antes de
creerlo.

**Resultado §36: NADA** (R2_A 5/12 y 3/12; razones 1.38 y 1.65). El
sustrato evoluciona pero no regula por el orden; las perillas se usan igual
con y sin herencia. Moldear comportamiento exige evolución de programa, y ese
paisaje es plano.

## 37. Una perilla de historia propia (2026-09-27)

Lo que evoluciona en el útero son perillas continuas heredables sobre la
expresión (§34–§35). La regulación por el orden necesita una cuya entrada sea
la historia de la celda: `reflejo=ε_g`: θ_eff = θ + g·tanh((ē − e)/e0), con ē
una media lenta de la energía propia (τ = 200) y g una ganancia heredable
continua (nace en 0, ±ε_g desde la materia de la madre, recortada a [−2, 2]).
Cuando la energía cae respecto de su historia, la expresión se desplaza; el
signo y la magnitud del desplazamiento son heredables. Bajo el orden regular
(C precede a A) la caída anuncia la hambruna; bajo el permutado no. Diseño:
programas CONGELADOS (sin carga), θ, s y g heredables; brazos clima, ciclo2,
permutado, nulo (θ, s, g fijos). Primaria R2_A (regla de v14); secundarias
ḡ_A por brazo (¿se selecciona un signo bajo los órdenes regulares y no bajo
el permutado?), w̄_A, s̄_A. VESTIGIO si R2_A cumple en clima y ciclo2; réplica
con otro sol antes de creerlo.

## 38. El motor en GPU (2026-09-27)

Por indicación de Fran los experimentos pasan a la GPU (la CPU se comparte
con otras sesiones). `utero/gpu.py` corre todos los mundos de un experimento
en un lote; el VM es exactamente el de CPU (test), el orden es en damero
(declarado). Se valida reproduciendo §26 y §34 antes de usarlo. La corrida
de §37 en CPU se detuvo sin resultado y se repite en GPU con 24 semillas
(`exp_utero_reflejo_gpu.py`), mismo pre-registro. Si la validación falla, el
motor no se usa para preguntas nuevas hasta entender qué cambia el damero.

## 39. Trasplante recíproco (2026-09-27)

El campo medio de §37 (numpy, sin GPU) mostró que la ganancia g es un reflejo
sobre el estado presente: paga con cualquier orden y más bajo el permutado,
así que R2_A no puede distinguir regularidad con esa perilla; §37 no se
corre. Mostró también que el orden decide cuál g conviene. La pregunta
correcta es de adaptación local: ¿a una población le va mejor bajo el orden
en el que evolucionó que bajo el otro, con un calendario nuevo y las perillas
fijas? Es el test clásico (trasplante recíproco), y separa adaptación al
orden de benignidad del entorno porque exige ventaja de casa en los DOS
orígenes. Orden de ejecución pendiente, todo en GPU y reanudable: (1)
completar V2 de §38; (2) §39. Ambos esperan la indicación de Fran: la corrida
de V2 fue detenida por el sistema por memoria RAM crítica.

**§39b, modelo reducido (numpy): PREDICE NADA** para el trasplante con las
perillas θ, s, g (local < foráneo 12/24 y 15/24). Enmienda de §39 antes de
correrlo: criterio local contra foráneo en ambos destinos.

## 40. Una perilla de historia de vida (2026-09-27)

La señal que recibe una perilla de tendencia de energía es la misma en la
estación templada bajo cualquier orden; lo que el orden cambia es la acción
que conviene allí. Perilla: propensión al parto condicionada al nivel de
ingreso propio, tres valores heredables q_bajo, q_medio, q_alto ∈ [0, 1]
(nacen en 1; ±ε al nacer). Predicción: bajo clima (a la templada le sigue la
hambruna) la selección baja q_medio; bajo ciclo2 (le sigue la abundancia) no.
El trasplante recíproco lo detecta con el criterio local contra foráneo.
Primero en el modelo reducido (minutos, sin GPU); si el modelo predice
VESTIGIO, la perilla se implementa en el motor de GPU y se corre en el
sustrato real cuando haya memoria y Fran lo indique.
