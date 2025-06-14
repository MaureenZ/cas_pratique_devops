
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

    def test_get_neighbors_center(self):
        # Point au centre (1,1) dans une grille 4x4
        neighbors = self.sim.get_neighbors(1, 1)
        expected = [
            (0, 0), (1, 0), (2, 0),
            (0, 1),         (2, 1),
            (0, 2), (1, 2), (2, 2),
        ]
        self.assertCountEqual(neighbors, expected)

    def test_get_neighbors_corner(self):
        # Point en coin (0,0) dans une grille 4x4
        neighbors = self.sim.get_neighbors(0, 0)
        expected = [
            (1, 0), (0, 1), (1, 1)
        ]
        self.assertCountEqual(neighbors, expected)

    def test_get_neighbors_edge(self):
        # Point sur bord (0,1) dans une grille 4x4
        neighbors = self.sim.get_neighbors(0, 1)
        expected = [
            (0, 0), (1, 0),
            (1, 1),
            (0, 2), (1, 2),
        ]
        self.assertCountEqual(neighbors, expected)

    def test_get_neighbors_bottom_right_corner(self):
        # Point en coin bas droit (3,3)
        neighbors = self.sim.get_neighbors(3, 3)
        expected = [
            (2, 2), (3, 2), (2, 3)
        ]
        self.assertCountEqual(neighbors, expected)

    def test_reset_map_resets_current_map(self):
        # Modifier current_map pour simuler un état modifié (ex: tout brûlé)
        for i in range(self.sim.height):
            for j in range(self.sim.width):
                self.sim.current_map[i][j] = TerrainType.BURNT

        # Vérifier que current_map est modifiée et différente de map
        different = False
        for i in range(self.sim.height):
            for j in range(self.sim.width):
                if self.sim.current_map[i][j] != self.sim.map[i][j]:
                    different = True
                    break
        self.assertTrue(different, "current_map doit être différente de map avant reset")

        # Appeler reset_map
        self.sim.reset_map()

        # Vérifier que current_map est redevenue identique à map
        for i in range(self.sim.height):
            for j in range(self.sim.width):
                self.assertEqual(self.sim.current_map[i][j], self.sim.map[i][j],
                                f"Cellule ({i},{j}) doit être identique après reset")


    def test_simulate_fire_valid_and_propagation(self):
        # Test normal : départ feu sur arbre en (1,1)
        burnt = self.sim.simulate_fire(1, 1)
        self.assertEqual(burnt, 3)
        # Vérifier que ces cases sont bien marquées brûlées
        self.assertEqual(self.sim.current_map[1][0], TerrainType.BURNT)
        self.assertEqual(self.sim.current_map[0][1], TerrainType.BURNT)
        self.assertEqual(self.sim.current_map[1][1], TerrainType.BURNT)
        # Arbre isolé en (1,3) non brûlé
        self.assertEqual(self.sim.current_map[3][1], TerrainType.TREE)

    def test_simulate_fire_invalid_position(self):
        with self.assertRaises(ValueError):
            self.sim.simulate_fire(-1, 0)
        with self.assertRaises(ValueError):
            self.sim.simulate_fire(4, 0)
        with self.assertRaises(ValueError):
            self.sim.simulate_fire(0, 4)

    def test_simulate_fire_no_tree_at_start(self):
        # Case vide en (0,0) => pas d'arbre à brûler
        result = self.sim.simulate_fire(0, 0)
        self.assertEqual(result, 0)


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

    def test_export_html_creates_file_with_content(self):
        # Préparer une carte simple
        self.sim.map = [
            [TerrainType.TREE, TerrainType.EMPTY],
            [TerrainType.WATER, TerrainType.BURNT],
        ]
        self.sim.current_map = self.sim.map
        self.sim.width = 2
        self.sim.height = 2

        # Nom de fichier de test
        test_filename = "test_export.html"

        # Appeler la méthode
        result_file = self.sim.export_html(filename=test_filename, title="Test HTML Export")

        # Vérifier que le fichier a bien été créé
        self.assertTrue(os.path.exists(test_filename), "Le fichier HTML n'a pas été créé")

        # Vérifier que le contenu du fichier contient des éléments attendus
        with open(test_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("<title>Test HTML Export</title>", content)
            self.assertIn("🌳", content)
            self.assertIn("💧", content)
            self.assertIn("🔥", content)
            self.assertIn("🍂", content)
            self.assertIn("Statistiques de la simulation", content)
            self.assertIn("Taille de la carte", content)

        # Nettoyage : supprimer le fichier généré
        os.remove(test_filename)

    def test_export_html_uses_original_map(self):
        # Préparer une map d'origine différente de la map actuelle
        self.sim.map = [
            [TerrainType.TREE, TerrainType.EMPTY],
            [TerrainType.WATER, TerrainType.BURNT],
        ]
        self.sim.current_map = [
            [TerrainType.BURNT, TerrainType.BURNT],
            [TerrainType.BURNT, TerrainType.BURNT],
        ]
        self.sim.width = 2
        self.sim.height = 2

        # Nom de fichier pour le test
        test_filename = "test_export_original_map.html"

        # Appel avec use_map=True
        self.sim.export_html(filename=test_filename, title="Test Map Originale", use_map=True)

        # Lire le contenu généré
        with open(test_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            # Vérifie que les symboles correspondant à self.map (et non current_map) sont bien présents
            self.assertIn("🌳", content)  # TREE
            self.assertIn("💧", content)  # WATER
            self.assertIn("🍂", content)  # EMPTY
            self.assertIn("🔥", content)  # BURNT

        # Nettoyage
        os.remove(test_filename)


if __name__ == "__main__":
    unittest.main()
