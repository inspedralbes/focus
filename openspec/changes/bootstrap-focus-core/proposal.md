# Canvi: bootstrap-focus-core

## Problema
FOCUS encara no té implementació. Cal establir un nucli local petit, extensible i verificable abans d'afegir restriccions reals als ordinadors. Sense contractes explícits, les transicions, els plugins i la recuperació d'errors podrien tenir comportaments inconsistents.

## Objectiu
Construir la primera versió funcional del nucli FOCUS en Python, guiada per especificacions i tests automatitzats.

## Inclòs
- Daemon local que carrega l'estat inicial i executa el plugin corresponent.
- Contracte de plugins: `on_enter()`, `on_tick()` i `on_exit()`.
- Plugins demostratius `classe`, `test` i `practica`.
- Polling periòdic de `state.json`.
- CLI per sol·licitar canvis d'estat.
- Escriptura atòmica del fitxer d'estat.
- Transicions ordenades i gestió d'errors/recuperació.
- Logging i tests automatitzats.

## Fora d'abast
- Kiosk real, bloqueig o tancament forçat d'aplicacions.
- Filtratge de xarxa/firewall.
- Integració específica amb Veyon.
- Servei systemd i journald.
- Paquet Debian.
- Servidor central, API o gestió centralitzada d'aula.

## Criteris d'acceptació
1. El daemon s'executa des del repositori en Python compatible.
2. En arrencar, llegeix un estat vàlid i crida `on_enter()` del plugin.
3. Les transicions executen `on_exit()` abans de `on_enter()`.
4. Detecta canvis de `state.json` dins l'interval configurat.
5. La CLI valida l'estat i actualitza el fitxer atòmicament.
6. Els errors de plugin es gestionen sense finalitzar innecessàriament el daemon.
7. Els canvis i errors queden registrats.
8. Els tests cobreixen els escenaris de les especificacions.
9. Cap plugin demostratiu modifica el sistema operatiu.

## Enfocament
Implementar primer contracte i nucli amb dependències substituïbles als tests; després CLI i plugins demostratius. Les operacions reals del sistema operatiu es desenvoluparan en canvis OpenSpec posteriors.

## Riscos
- Un hook pot modificar parcialment el sistema abans de fallar.
- El fitxer pot ser llegit durant una actualització; la CLI ha d'emprar substitució atòmica.
- Un hook síncron pot bloquejar el bucle; no hi haurà execució concurrent en aquesta fase.
