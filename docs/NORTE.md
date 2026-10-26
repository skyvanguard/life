# El norte de zeta-life

*Una página. Escrita el 2026-10-25, después de revisar los 241 commits y los
cinco programas del repositorio. Se actualiza sólo cuando cambia la pregunta,
no cuando cambia el experimento.*

## La pregunta que no cambió

**¿Puede un sistema nacer vacío, aprender de su propia experiencia en vida y
sostener una identidad, sin entrenamiento previo?**

Es la pregunta del cuaderno manuscrito (2025) y del diseño del kernel
(2026-03-03: aprendizaje continuo, identidad persistente, auto-modelo). Todo
lo demás son encarnaciones. Cuando una encarnación choca una pared, se baja
un nivel; lo que faltaba era escribir que se sigue preguntando lo mismo.

## Qué respondió cada programa

| Programa | Encarnación de la pregunta | Respuesta | Estado |
|---|---|---|---|
| **Zeta / IPUESA / psyche** (2025-12 a 2026-03) | ¿los ceros de zeta dan estructura a una IA adaptativa? | No: zeta == uniforme fuera de los autómatas espaciales | archivado |
| **Conscious Kernel** (2026-03 a 2026-06) | ¿una unidad de inferencia activa integra su experiencia con identidad persistente? | Sí como harness: aprende en vida, resuelve CartPole/Pendulum/Reacher con Ψ vivo; Ψ es heurística, no medida de conciencia | maduro, no frontera |
| **El Norte** (2026-06 a 2026-07) | ¿Ψ puede vivir en las activaciones de un LLM real y el modelo aprender a leerla? | No: la introspección entrenada es lookup, no lectura general | cerrado, negativo honesto |
| **El Útero, novedad** (2026-07 a 2026-09) | ¿emerge estructura nueva de una física que se reescribe, sin nada preentrenado? | Sí, rara (~5 %), con cinco jaulas nombradas | cerrado con paper |
| **El Útero, sol y evolución** (2026-09-26/27) | ¿emerge regulación, anticipación o aprendizaje bajo un entorno con orden? | No en 19 corridas; sí evolución darwiniana (§34/§35), no inteligencia | cerrado |
| **El Útero, aprender en vida** (§43–§49, 2026-09-27 a 2026-10-26) | ¿puede una celda cambiar su regla por su propia señal, durante su vida, y generalizar? | §43 (discreto): NADA por falta de localidad. §45 (continuo): aprende en vida, sin generalizar. §49: NADA | cerrado |
| **Kernel acoplado a Yvyra** (Fase A/B, 2026-06 a 2026-10-26) | ¿la introspección de un LLM se ancla a la Ψ del kernel? | Inconclusa. Ψ no estaba rota: detecta sorpresa relativa y la memoria llena más los quiebres frecuentes la tapaban | cerrado como vehículo: el kernel es el agente |

## Lo que une al kernel con el útero

El útero aportó los tres principios: reglas-como-estado, lazo cerrado,
persistencia como único filtro. El kernel aportó el mecanismo: una regla
continua con localidad, una señal propia (error de predicción o ingreso),
memoria y auto-modelo. El §44 dijo qué necesita un ser para aprender en vida:
localidad, señal propia rápida, algo que sentir, consecuencias en vida. El
útero discreto no tenía ninguna; el kernel tiene las cuatro por construcción;
el §45 es una celda del útero con la regla del kernel. Ahí convergen.

## La regla de decisión vigente

1. Correr el §45 con la enmienda de herencia genotípica (2026-10-25). Si
   APRENDE EN VIDA y GENERALIZA, y lo replica otro sol: la frontera pasa a
   ser **la celda plástica como kernel mínimo**, y la pregunta siguiente es
   qué señal (ingreso o energía libre) y qué otro (otro ser en el mundo).
2. Si NADA o sólo aprende sin generalizar: el útero se cierra con su paper
   como negativo honesto y la frontera **vuelve al kernel**, que ya cumple los
   cuatro requisitos del §44. La pregunta siguiente ahí es la que quedó
   abierta en junio: des-saturar la experiencia para que Ψ discrimine.
3. No se abre una sexta encarnación del útero sin cerrar la quinta.
4. El kernel no se archiva: es el único sustrato del repo que ya responde la
   pregunta en su forma de ingeniería.

## Resultado del §45 y la decisión pendiente (2026-10-26)

§45 corrió con la enmienda, en dos soles, más §45b con estaciones 10×:
**APRENDE EN VIDA, SIN GENERALIZAR**, replicado. Por la regla 2 de arriba el
útero se cerraría y la frontera volvería al kernel. Antes de aplicarla, un
matiz que salió de los datos y que Fran tiene que juzgar: la celda no
generaliza porque no tiene dónde guardar nada que sobreviva a la estación
(su memoria h dura 10 ticks y no es plástica; su regla se re-escribe). No
falló la hipótesis "aprender en vida"; falló una celda sin memoria lenta.
La pieza que falta ya existe en el repo: la memoria complementaria del
kernel. Recomendación: un solo experimento más, pre-registrado, que le dé a
la celda plástica una memoria lenta legible por su regla y mida G. Si tampoco
generaliza, se aplica la regla 2 sin más matices. **Decisión: de Fran.**

## Aplicación de la regla (2026-10-26, 09:30)

El experimento se corrió (§49, dos soles): **NADA**. Con el sentido de su
propio ingreso la celda no generaliza, y el diagnóstico de edades dice por
qué: vive dos estaciones y no vuelve a ver la misma; aprender por recurrencia
exige seis. Se aplica la regla 2 tal como quedó escrita: **el útero se cierra
con su paper como negativo honesto; la frontera vuelve al kernel.** Lo que el
útero deja: tres principios, cinco jaulas nombradas, una adaptación
darwiniana medida (§34/§35), un aprendizaje en vida medido y mortal (§45) y
la distinción, medida en el mismo mundo, entre lo que fabrica la evolución
(un especialista) y lo que fabrica el aprendizaje (un generalista con
retraso). Pregunta abierta, anotada y no corrida: vidas largas. Abrirla es
una decisión nueva, no una continuación.

## El kernel es el agente (2026-10-26, tarde)

Fran: *"el kernel tiene que ser único, sin necesidad de mezclarse con otro
agente, porque el kernel en sí es el agente"*. Se abandona Yvyra como vehículo:
un LLM es preentrenamiento, y la pregunta dice sin entrenamiento previo. La
hipótesis que quedaba abierta se probó con el kernel solo
(`exp_psi_quiebres.py`). En un flujo predecible, Ψ ve los quiebres raros y
grandes (aciertos 1.00, falsas alarmas 0.03–0.07). Los quiebres frecuentes no
los ve (0.25–0.30), y el ruido entierra los medianos. Ψ es un detector de
sorpresa relativa con un umbral que mueve el bono de memoria episódica. En
120 flujos, ALTA nunca bajó de 0.74, y donde más se acercó Ψ no
discriminaba: la meta de "des-saturar" estaba mal puesta. Lo que sigue es una decisión nueva: el kernel viviendo en su propio
mundo, donde sus actos causan su experiencia.

## Lo que la estrella sigue siendo

La experiencia subjetiva verificable no es alcanzable con ninguna matemática
de hoy; el muro es de verificación, no de ingeniería. Queda como brújula, no
como destino (conversación fundacional, 2026-07-02). Ψ mide integración, no
experiencia. Los indicadores de Butlin no son conciencia.

## Disciplina (la que sí se mantuvo en los cinco programas)

Vara antes de mirar. Control adversarial antes de creer. Refutaciones en el
ledger con el mismo peso que los positivos. Y una regla nueva, aprendida en
octubre: **después de cada cierre, una línea en este documento antes de abrir
el siguiente.**
