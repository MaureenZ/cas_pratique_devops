import random
import copy
from enum import Enum

class TerrainType(Enum):
    """Types de terrain possibles"""
    EMPTY = 0      # Terrain nu
    TREE = 1       # Arbre
    WATER = 2      # Plan d'eau
    BURNT = 3      # Terrain brûlé

class ForestFireSimulator:
    """Simulateur de feux de forêt"""
    
    def __init__(self, width: int = 10, height: int = 8):
        """
        Initialise le simulateur
        
        Args:
            width: Largeur de la carte
            height: Hauteur de la carte
        """
        self.width = width
        self.height = height
        self.original_map = []
        self.current_map = []
        
    def generate_random_map(self, tree_percentage: float = 0.6, water_percentage: float = 0.1):
        """
        Génère une carte aléatoire
        
        Args:
            tree_percentage: Pourcentage d'arbres (0.0 à 1.0)
            water_percentage: Pourcentage d'eau (0.0 à 1.0)
        """
        self.original_map = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                rand = random.random()
                if rand < water_percentage:
                    terrain = TerrainType.WATER
                elif rand < water_percentage + tree_percentage:
                    terrain = TerrainType.TREE
                else:
                    terrain = TerrainType.EMPTY
                row.append(terrain)
            self.original_map.append(row)
        
        # Copie pour les simulations
        self.current_map = copy.deepcopy(self.original_map)
    
    def reset_map(self):
        """Remet la carte dans son état initial"""
        self.current_map = copy.deepcopy(self.original_map)
        
    def get_neighbors(self, x: int, y: int):
        """
        Retourne les coordonnées des voisins (incluant diagonales)
        
        Args:
            x, y: Coordonnées de la case
            
        Returns:
            Liste des coordonnées des voisins valides
        """
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors
    
    def simulate_fire(self, start_x: int, start_y: int):
        """
        Simule un incendie à partir d'une position donnée
        
        Args:
            start_x, start_y: Position de départ du feu
            
        Returns:
            Nombre de cases brûlées
        """
        if not (0 <= start_x < self.width and 0 <= start_y < self.height):
            raise ValueError("Position de départ invalide")
        
        if self.current_map[start_y][start_x] != TerrainType.TREE:
            print(f"Pas d'arbre à brûler à la position ({start_x}, {start_y})")
            return 0
        
        # File d'attente pour la propagation du feu (BFS)
        fire_queue = [(start_x, start_y)]
        burnt_count = 0
        
        print(f"Début de l'incendie à la position ({start_x}, {start_y})")
        
        while fire_queue:
            x, y = fire_queue.pop(0)
            
            # Si cette case n'est pas un arbre, on passe
            if self.current_map[y][x] != TerrainType.TREE:
                continue
            
            # Brûler la case
            self.current_map[y][x] = TerrainType.BURNT
            burnt_count += 1
            print(f"Case brûlée: ({x}, {y}) - Total: {burnt_count}")
            
            # Propager aux voisins
            for nx, ny in self.get_neighbors(x, y):
                if self.current_map[ny][nx] == TerrainType.TREE:
                    # Vérifier que ce voisin n'est pas déjà dans la queue
                    if (nx, ny) not in fire_queue:
                        fire_queue.append((nx, ny))
        
        print(f"Incendie terminé - Total de cases brûlées: {burnt_count}")
        return burnt_count
    
    def export_html(self, filename: str = "forest_fire_simulation.html", title: str = "Simulation d'Incendie de Forêt", use_original_map: bool = False):
        """
        Exporte la simulation en HTML pour visualisation
        
        Args:
            filename: Nom du fichier HTML à créer
            title: Titre de la page
            use_original_map: Si True, utilise la carte originale, sinon la carte actuelle
        """
        # Choisir quelle carte utiliser
        map_to_export = self.original_map if use_original_map else self.current_map
        
        # Couleurs pour chaque type de terrain
        colors = {
            TerrainType.EMPTY: '#D2B48C',    # Beige pour terrain nu
            TerrainType.TREE: '#228B22',     # Vert pour les arbres
            TerrainType.WATER: '#4169E1',    # Bleu pour l'eau
            TerrainType.BURNT: '#8B0000'     # Rouge foncé pour terrain brûlé
        }
        
        # Symboles pour la légende
        symbols = {
            TerrainType.EMPTY: 'Terrain nu',
            TerrainType.TREE: 'Arbre',
            TerrainType.WATER: 'Eau',
            TerrainType.BURNT: 'Terrain brûlé'
        }
        
        # Calculer les statistiques
        total_cells = self.width * self.height
        stats = {}
        for terrain_type in TerrainType:
            count = sum(row.count(terrain_type) for row in map_to_export)
            stats[terrain_type] = {
                'count': count,
                'percentage': (count / total_cells) * 100
            }
        
        # Générer le HTML
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }}
        .map-container {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }}
        .map {{
            display: grid;
            grid-template-columns: repeat({self.width}, 30px);
            grid-template-rows: repeat({self.height}, 30px);
            gap: 1px;
            border: 2px solid #333;
            background-color: #333;
        }}
        .cell {{
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border: 1px solid #333;
        }}
        .stats {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .stats h3 {{
            margin-top: 0;
            color: #333;
        }}
        .stat-item {{
            margin: 5px 0;
            padding: 5px;
            background-color: white;
            border-radius: 3px;
        }}
        .coordinates {{
            font-size: 10px;
            color: #666;
            text-align: center;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <div class="map-container">
            <div class="map">"""
        
        # Générer les cellules de la carte
        for y in range(self.height):
            for x in range(self.width):
                terrain = map_to_export[y][x]
                color = colors[terrain]
                html_content += f"""
                <div class="cell" style="background-color: {color};" title="({x},{y}) - {symbols[terrain]}"></div>"""
        
        html_content += f"""
            </div>
        </div>
        
        <div class="coordinates">
            Coordonnées : survolez les cases pour voir la position et le type de terrain
        </div>
        
        <div class="legend">"""
        
        # Générer la légende
        for terrain_type in TerrainType:
            if stats[terrain_type]['count'] > 0:  # Afficher seulement les types présents
                color = colors[terrain_type]
                name = symbols[terrain_type]
                html_content += f"""
            <div class="legend-item">
                <div class="legend-color" style="background-color: {color};"></div>
                <span>{name}</span>
            </div>"""
        
        html_content += f"""
        </div>
        
        <div class="stats">
            <h3>Statistiques de la simulation</h3>
            <div class="stat-item"><strong>Taille de la carte:</strong> {self.width} × {self.height} ({total_cells} cases)</div>"""
        
        # Ajouter les statistiques détaillées
        for terrain_type in TerrainType:
            if stats[terrain_type]['count'] > 0:
                name = symbols[terrain_type]
                count = stats[terrain_type]['count']
                percentage = stats[terrain_type]['percentage']
                html_content += f"""
            <div class="stat-item"><strong>{name}:</strong> {count} cases ({percentage:.1f}%)</div>"""
        
        html_content += """
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
            Généré par le Simulateur de Feux de Forêt
        </div>
    </div>
</body>
</html>"""
        
        # Écrire le fichier
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Export HTML créé : {filename}")
        return filename
    
    def display_map(self, show_burnt=True):
        """Affiche la carte en console pour les tests"""
        symbols = {
            TerrainType.EMPTY: '.',
            TerrainType.TREE: 'T',
            TerrainType.WATER: 'W',
            TerrainType.BURNT: 'X'
        }
        
        # Choisir quelle carte afficher
        map_to_show = self.current_map if show_burnt else self.original_map
        
        print("=" * (self.width + 2))
        for row in map_to_show:
            line = "|"
            for cell in row:
                line += symbols[cell]
            line += "|"
            print(line)
        print("=" * (self.width + 2))
        
        # Statistiques
        total_cells = self.width * self.height
        tree_count = sum(row.count(TerrainType.TREE) for row in map_to_show)
        water_count = sum(row.count(TerrainType.WATER) for row in map_to_show)
        empty_count = sum(row.count(TerrainType.EMPTY) for row in map_to_show)
        burnt_count = sum(row.count(TerrainType.BURNT) for row in map_to_show)
        
        print(f"Statistiques:")
        print(f"- Arbres: {tree_count}/{total_cells} ({tree_count/total_cells*100:.1f}%)")
        print(f"- Eau: {water_count}/{total_cells} ({water_count/total_cells*100:.1f}%)")
        print(f"- Terrain nu: {empty_count}/{total_cells} ({empty_count/total_cells*100:.1f}%)")
        if burnt_count > 0:
            print(f"- Terrain brûlé: {burnt_count}/{total_cells} ({burnt_count/total_cells*100:.1f}%)")


    def apply_smart_preventive_cut(self, fire_x: int, fire_y: int):
        """
        Applique une stratégie intelligente de coupe d'un seul arbre pour limiter la propagation du feu.
        
        Args:
            fire_x: Coordonnée x de départ du feu
            fire_y: Coordonnée y de départ du feu
            
        Returns:
            Tuple (meilleur_x, meilleur_y, nb_brule_initial, nb_brule_apres) de la meilleure coupe
        """
        # Carte initiale sans modification
        self.reset_map()
        nb_brule_initial = self.simulate_fire(fire_x, fire_y)
        
        # Liste des positions d'arbres
        tree_positions = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.original_map[y][x] == TerrainType.TREE
        ]

        best_cut = None
        min_burnt = nb_brule_initial

        for (x, y) in tree_positions:
            # empecher de couper le départ du feu
            if (x, y) == (fire_x, fire_y):
                continue

            # Créer une copie temporaire de la carte
            temp_map = copy.deepcopy(self.original_map)
            temp_map[y][x] = TerrainType.EMPTY  # Couper l'arbre

            # Simuler le feu avec cette carte
            self.current_map = copy.deepcopy(temp_map)
            burnt = self.simulate_fire(fire_x, fire_y)

            if burnt < min_burnt:
                min_burnt = burnt
                best_cut = (x, y)
        
        # Réappliquer la meilleure coupe sur la vraie carte
        if best_cut:
            self.original_map[best_cut[1]][best_cut[0]] = TerrainType.EMPTY
            self.reset_map()
            self.simulate_fire(fire_x, fire_y)
            print(f"Meilleure coupe: {best_cut}, Feu initial: {nb_brule_initial}, Feu après coupe: {min_burnt}")
            return best_cut + (nb_brule_initial, min_burnt)
        else:
            print("Aucune coupe n'améliore la situation.")
            return None


# Test du simulateur
if __name__ == "__main__":
    # Créer un simulateur
    simulator = ForestFireSimulator(10, 8)
    
    # Générer une carte avec 60% d'arbres et 10% d'eau
    simulator.generate_random_map(tree_percentage=0.6, water_percentage=0.1)
    
    # Afficher la carte initiale
    print("Carte initiale:")
    simulator.display_map(show_burnt=False)
    
    # Export HTML de la carte initiale
    print(f"\n" + "="*30)
    print("EXPORT HTML - CARTE INITIALE")
    print("="*30 + "\n")
    
    html_initial = simulator.export_html("carte_initiale.html", "Carte Initiale - Avant Incendie", use_original_map=True)
    print(f"Carte initiale exportée : {html_initial}")
    
    print("\n" + "="*50)
    print("SIMULATION D'INCENDIE")
    print("="*50 + "\n")
    
    # Lancer un incendie au centre de la carte
    fire_x, fire_y = simulator.width // 2, simulator.height // 2
    burnt_cells = simulator.simulate_fire(fire_x, fire_y)
    
    print(f"\n" + "="*50)
    print("RÉSULTAT APRÈS INCENDIE")
    print("="*50 + "\n")
    
    # Afficher la carte après l'incendie
    print("Carte après incendie:")
    simulator.display_map(show_burnt=True)



    
    # Export HTML
    print(f"\n" + "="*30)
    print("EXPORT HTML - APRÈS INCENDIE")
    print("="*30 + "\n")
    
    html_file = simulator.export_html("simulation_incendie.html", "Résultat de la Simulation d'Incendie")
    print(f"Simulation exportée : {html_file}")
    
    print(f"\n🔥 Résumé des exports HTML créés :")
    print(f"  📄 {html_initial} - Carte avant incendie")
    print(f"  📄 {html_file} - Carte après incendie")
    print("Ouvrez ces fichiers dans votre navigateur pour voir les visualisations !")
    
    print(f"\nLégende:")
    print(f"- '.' = Terrain nu")
    print(f"- 'T' = Arbre")
    print(f"- 'W' = Eau")
    print(f"- 'X' = Terrain brûlé")

    # Test avec coupe
    simulator.apply_smart_preventive_cut(fire_x, fire_y)
    # Afficher la carte après la coupe intelligente
    print("Carte après coupe:")
    simulator.display_map(show_burnt=True)
    simulator.export_html("resultat_smart_cut.html")

    # Test avec remise à zéro
    print(f"\n" + "="*50)
    print("TEST DE REMISE À ZÉRO")
    print("="*50 + "\n")
    
    simulator.reset_map()
    print("Carte remise à zéro:")
    simulator.display_map(show_burnt=False)