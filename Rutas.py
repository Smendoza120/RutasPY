import heapq
from typing import Dict, List, Optional, Set, Tuple

# Conocimiento inicial
class KnowledgeBase: 
  def __init__(self):
    self.estaciones_cerradas: Set[str] = set()
    self.lineas_inactivas: Set[str] = set()
    self.tiempo_transbordo: Dict[Tuple[str, str], float] = {}

  def reportar_estacion_cerrada(self, estacion: str) -> None:
    self.estaciones_cerradas.add(estacion)

  def reportar_linea_inactiva(self, linea: str) -> None:
    self.lineas_inactivas.add(linea)

  def es_transito_valido(self, origen: str, destino: str, linea: str) -> bool:
    if origen in self.estaciones_cerradas:
      return False
    if destino in self.estaciones_cerradas:
      return False
    if linea in self.lineas_inactivas:
      return False
    return True

# Red de transporte
class TransportNetwork:
  def __init__(self):
    self.adj: Dict[str, List[Tuple[str, float, str]]] = {}
    self.coordenadas: Dict[str, Tuple[float, float]] = {}

  def agregar_estacion(self, nombre: str, x: float, y: float) -> None:
    if nombre not in self.adj:
      self.adj[nombre] = []
      self.coordenadas[nombre] = (x, y)

  def agregar_conexion(self, origen: str, destino: str, tiempo: float, linea: str) -> None:
    self.adj[origen].append((destino, tiempo, linea))
    self.adj[destino].append((origen, tiempo, linea)) 

  def heuristica(self, estacion_a: str, estacion_b: str) -> float:
    x1, y1 = self.coordenadas[estacion_a]
    x2, y2 = self.coordenadas[estacion_b]
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

# Motor de busqueda inteligente
class RouterAgent:
  def __init__(self, network: TransportNetwork, knowledge: KnowledgeBase):
    self.network = network
    self.kb = knowledge

  def encontrar_mejor_ruta(self, origen: str, destino: str) -> Optional[Tuple[List[str], float]]:
    if origen not in self.network.adj or destino not in self.network.adj:
      return None

    pq: List[Tuple[float, float, str, Optional[str]]] = []
    heapq.heappush(pq, (0.0, 0.0, origen, None))

    g_score: Dict[str, float] = {origen: 0.0}
    came_from: Dict[str, Tuple[str, str]] = {}

    while pq:
      _, current_g, current_node, current_line = heapq.heappop(pq)

      if current_node == destino:
        return self._reconstruir_ruta(came_from, origen, destino), current_g

      if current_g > g_score.get(current_node, float('inf')):
        continue

      for neighbor, tiempo_tramo, linea in self.network.adj[current_node]:
        if not self.kb.es_transito_valido(current_node, neighbor, linea):
          continue

        costo_transbordo = 3.0 if (current_line and current_line != linea) else 0.0
        tentative_g = current_g + tiempo_tramo + costo_transbordo

        if tentative_g < g_score.get(neighbor, float('inf')):
          g_score[neighbor] = tentative_g
          f_score = tentative_g + self.network.heuristica(neighbor, destino)
          came_from[neighbor] = (current_node, linea)
          heapq.heappush(pq, (f_score, tentative_g, neighbor, linea))

    return None

  def _reconstruir_ruta(self, came_from: Dict[str, Tuple[str, str]], origen: str, destino: str) -> List[str]:
    curr = destino
    path = []

    while curr != origen:
      prev_node, linea = came_from[curr]
      path.append(f"{curr} (vía {linea})")
      curr = prev_node

    path.append(origen)
    path.reverse()
    return path

# Test del codigo
if __name__ == "__main__":
  red = TransportNetwork()

  estaciones = {
    "Portal Norte": (0, 10),
    "Calle 100": (0, 7),
    "Calle 72": (0, 4),
    "Marly": (0, 2),
    "Estación Central": (0, 0),
    "Suba": (-4, 8),
    "Suba Calle 100": (-2, 7)
  }

  for est, coords in estaciones.items():
    red.agregar_estacion(est, *coords)

  red.agregar_conexion("Portal Norte", "Calle 100", 6.0, "Línea Troncal A")
  red.agregar_conexion("Calle 100", "Calle 72", 5.0, "Línea Troncal A")
  red.agregar_conexion("Calle 72", "Marly", 4.0, "Línea Troncal A")
  red.agregar_conexion("Marly", "Estación Central", 3.0, "Línea Troncal A")
  
  red.agregar_conexion("Suba", "Suba Calle 100", 5.0, "Línea B")
  red.agregar_conexion("Suba Calle 100", "Calle 100", 4.0, "Línea B")
  red.agregar_conexion("Calle 100", "Estación Central", 10.0, "Línea Exprés C")

  kb = KnowledgeBase()
  agente = RouterAgent(red, kb)

  print("--- 1. BÚSQUEDA EN CONDICIONES NORMALES ---")
  resultado = agente.encontrar_mejor_ruta("Suba", "Estación Central")

  if resultado:
    ruta, tiempo = resultado
    print(f"Ruta óptima encontrada (Tiempo estimado: {tiempo:.1f} min):")
    print(" -> ".join(ruta))

  print("\n--- 2. INFERENCIA Y ACTUALIZACIÓN DE LA KB ---")
  print("Inyectando nuevo hecho en la BC: 'Calle 72 está CERRADA por mantenimiento'")
  kb.reportar_estacion_cerrada("Calle 72")

  print("\n--- 3. REVALORIZACIÓN DE RUTA BASADA EN REGLAS ---")
  resultado = agente.encontrar_mejor_ruta("Suba", "Estación Central")

  if resultado:
    ruta, tiempo = resultado
    print(f"Nueva ruta re-calculada (Tiempo estimado: {tiempo:.1f} min):")
    print(" -> ".join(ruta))
  else:
    print("No existe una ruta disponible que cumpla con los criterios lógicos.")