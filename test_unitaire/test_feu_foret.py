import unittest
from cas_pratique import ForestFireSimulator
from enum import Enum

class TerrainType(Enum):
    """Type de terrain"""
    EMPTY = 0      # Terrain nu
    TREE = 1       # Arbre
    WATER = 2      # Plan d'eau
    BURNT = 3      # Terrain brûlé

class testInit(unittest.TestCase):
    def test_initialisation_defaut(self):
        simulateur = ForestFireSimulator()
        self.assertEqual(simulateur.width, 10)
        self.assertEqual(simulateur.height, 8)
        self.assertEqual(simulateur.map, [])
        self.assertEqual(simulateur.current_map, [])

    def test_initialisation_custom1(self):
        simulateur = ForestFireSimulator(width=5, height=7)
        self.assertEqual(simulateur.width, 5)
        self.assertEqual(simulateur.height, 7)
        self.assertEqual(simulateur.map, [])
        self.assertEqual(simulateur.current_map, [])

    def test_initialisation_custom2(self):
        simulateur = ForestFireSimulator(width=2, height=2)
        self.assertEqual(simulateur.width, 2)
        self.assertEqual(simulateur.height, 2)
        self.assertEqual(simulateur.map, [])
        self.assertEqual(simulateur.current_map, [])

    def test_initialisation_custom2(self):
        simulateur = ForestFireSimulator(width=18, height=3)
        self.assertEqual(simulateur.width, 18)
        self.assertEqual(simulateur.height, 3)
        self.assertEqual(simulateur.map, [])
        self.assertEqual(simulateur.current_map, [])
    
class TestMapGenerator(unittest.TestCase):
    def test_map_dimensions(self):
        width, height = 15, 12
        simulateur = ForestFireSimulator(width, height)
        simulateur.map_generator(tree_percentage=0.5, water_percentage=0.2)

        self.assertEqual(len(simulateur.map), height, "La hauteur de la map est incorrect")
        for row in simulateur.map:
            self.assertEqual(len(row), width, "La largeur d'une ligne de la carte est incorrecte")

    def test_arbre_eau_pourcent(self):
        width, height = 15, 8
        tree_pourcent = 0.5
        water_pourcent = 0.6
        simulateur = ForestFireSimulator(width, height)
        simulateur.map_generator(tree_percentage=tree_pourcent, water_percentage=water_pourcent)

        total_map = width * height
        nb_arbre = 0
        nb_eau = 0

        for row in simulateur.map:
            for cell in row:
                if cell.name == "TREE":
                    nb_arbre += 1
                elif cell.name == "WATER":
                    nb_eau += 1

        pourcent_arbre_reel = nb_arbre / total_map
        pourcent_eau_reel = nb_eau / total_map

        #ecart autorisé de 20%
        marge = 0.2
        self.assertAlmostEqual(tree_pourcent, pourcent_arbre_reel, delta=marge, msg=f"Pourcentage d'arbres demandés ~{tree_pourcent}, obtenu {pourcent_arbre_reel:.2f}")
        self.assertAlmostEqual(water_pourcent, pourcent_eau_reel, delta=marge, msg=f"Pourcentage d'eau demandés ~{water_pourcent}, obtenu {pourcent_eau_reel:.2f}")

    def test_map_type_terrain_valide(self):
        width, height = 15, 8
        simulateur = ForestFireSimulator(width, height)
        simulateur.map_generator(tree_percentage=0.4, water_percentage=0.5)

        for row in simulateur.map:
            for cell in row:
                self.assertIn(cell.name, ["EMPTY", "WATER", "TREE"])

    def test_map_generation_pourcent_vide(self):
        width, height = 15, 8
        simulateur = ForestFireSimulator(width, height)
        

        #cas 1 : arbre et eau à 0
        simulateur.map_generator(tree_percentage=0, water_percentage=0)

        for row in simulateur.map:
            for cell in row:
                self.assertEqual(cell.name, "EMPTY")

        #cas 2 : arbre à 0 et eau != 0
        simulateur.map_generator(tree_percentage=0, water_percentage=0.5)
        for row in simulateur.map:
            for cell in row:
                self.assertIn(cell.name, ["WATER", "EMPTY"])

        #cas 3 : arbre != 0 et eau = 0
        simulateur.map_generator(tree_percentage=0.3, water_percentage=0)
        for row in simulateur.map:
            for cell in row:
                self.assertIn(cell.name, ["EMPTY", "TREE"])

    def test_map_generation_full_arbre(self):
        width, height = 15, 8
        simulateur = ForestFireSimulator(width, height)
        simulateur.map_generator(tree_percentage=1.0, water_percentage=0.0)

        for row in simulateur.map:
            for cell in row:
                self.assertEqual(cell.name, "TREE", "la case n'est pas un arbre")


    def test_map_generation_full_eau(self):
        width, height = 15, 8
        simulateur = ForestFireSimulator(width, height)
        simulateur.map_generator(tree_percentage=0.0, water_percentage=1.0)

        for row in simulateur.map:
            for cell in row:
                self.assertEqual(cell.name, "WATER", "la case n'est pas de l'eau")


if __name__ == "__main__":
    unittest.main()
