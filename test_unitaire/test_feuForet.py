import io
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from contextlib import redirect_stdout
from cas_pratique import ForestFireSimulator
from cas_pratique import TerrainType
import copy

class TestFireSimulation(unittest.TestCase):
    def setUp(self):
        # Carte 4x4 avec 5 arbres
        self.map = [
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 1, 0, 0],
        ]

        # Conversion carte en TerrainType
        self.map_enum = [[TerrainType(cell) for cell in row] for row in self.map]

        # Initialiser le simulateur avec cette carte
        self.sim = ForestFireSimulator(4, 4)
        self.sim.map = copy.deepcopy(self.map_enum)
        self.sim.current_map = copy.deepcopy(self.map_enum)

    def test_apply_smart_preventive_cut_improves_fire(self):
        result = self.sim.apply_smart_preventive_cut(0, 1)  # feu départ sur un arbre en (0,1)
        self.assertIsNotNone(result)
        x, y, feu_avant, feu_apres = result
        self.assertLess(feu_apres, feu_avant)  # Après coupe, le feu doit brûler moins

    def test_apply_smart_n_preventive_cut_limits_coupes(self):
        results = self.sim.apply_smart_n_preventive_cut(0, 1, 2)
        self.assertTrue(len(results) <= 2)
        for x, y, feu_avant, feu_apres in results:
            self.assertLess(feu_apres, feu_avant)

    def test_apply_smart_preventive_cut_no_improvement(self):
        # Carte sans arbres = pas d'amélioration possible
        sim2 = ForestFireSimulator(2, 2)
        sim2.map = [
            [TerrainType.EMPTY, TerrainType.EMPTY],
            [TerrainType.EMPTY, TerrainType.EMPTY]
        ]
        sim2.current_map = copy.deepcopy(sim2.map)
        result = sim2.apply_smart_preventive_cut(0, 0)
        self.assertIsNone(result)
    
    def test_display_map_output(self):
        self.sim.map = [
            [TerrainType.EMPTY, TerrainType.TREE],
            [TerrainType.WATER, TerrainType.BURNT],
        ]
        self.sim.current_map = self.sim.map
        self.sim.width = 2
        self.sim.height = 2

        f = io.StringIO()
        with redirect_stdout(f):
            self.sim.display_map()

        output = f.getvalue()

        # Vérifier que les symboles apparaissent dans l'affichage
        self.assertIn("⬜", output)   # EMPTY
        self.assertIn("🌳", output)  # TREE
        self.assertIn("💧", output)  # WATER
        self.assertIn("🔥", output)  # BURNT

        # Vérifier qu’il y a bien une ligne de statistiques
        self.assertIn("Statistique:", output)
        self.assertIn("- Arbres:", output)
        self.assertIn("- Eau:", output)
        self.assertIn("- Terrain nu:", output)
        self.assertIn("- Terrain brûlé:", output)
    
    def test_display_map_no_burnt(self):
        # Carte avec une cellule brûlée, qu'on ne veut pas afficher
        self.sim.map = [
            [TerrainType.EMPTY, TerrainType.TREE],
            [TerrainType.WATER, TerrainType.TREE],
        ]
        self.sim.current_map = [
            [TerrainType.EMPTY, TerrainType.TREE],
            [TerrainType.WATER, TerrainType.BURNT],  # simulé brûlé
        ]
        self.sim.width = 2
        self.sim.height = 2

        f = io.StringIO()
        with redirect_stdout(f):
            self.sim.display_map(show_burnt=False)  # on veut voir self.map

        output = f.getvalue()

        # On vérifie que le symbole 🔥 (brûlé) n'apparaît pas dans l'affichage
        self.assertNotIn("🔥", output)




if __name__ == "__main__":
    unittest.main()
