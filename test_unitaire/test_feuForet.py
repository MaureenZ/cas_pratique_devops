import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
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


if __name__ == "__main__":
    unittest.main()
