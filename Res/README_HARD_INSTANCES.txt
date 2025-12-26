======================================================================
INSTANCES CNF DIFFICILES - SAT SOLVER BENCHMARK
======================================================================

📊 STATISTIQUES GÉNÉRALES:
   • Total d'instances: 30
   • Variables: 5 → 200 (progression linéaire)
   • Type: 3-SAT au seuil critique (ratio ≈ 4.26)
   • Format: DIMACS CNF

🎯 POURQUOI CES INSTANCES SONT DIFFICILES:
   • Ratio clauses/variables = 4.26 (seuil de transition de phase)
   • À ce ratio, 3-SAT est statistiquement le PLUS DUR
   • ~50% des instances sont SAT, ~50% UNSAT
   • Aucune structure exploitable → force brute nécessaire

📈 COMPLEXITÉ ATTENDUE:
   • < 50 vars   : NAIVE & MOMS peuvent résoudre
   • 50-100 vars : Seul CDCL réussit (quelques secondes)
   • 100-150 vars: CDCL peut prendre plusieurs minutes
   • > 150 vars  : Très difficile, risque de TIMEOUT

🔧 UTILISATION:
   ./SATSolverOptimised
   (Le programme teste automatiquement tous les fichiers)

📋 DÉTAILS DES INSTANCES:
----------------------------------------------------------------------
  1. generated_sat_001.cnf
      Vars:   5 | Clauses:   21 | Ratio: 4.26
  2. generated_sat_002.cnf
      Vars:  11 | Clauses:   46 | Ratio: 4.26
  3. generated_sat_003.cnf
      Vars:  18 | Clauses:   76 | Ratio: 4.26
  4. generated_sat_004.cnf
      Vars:  25 | Clauses:  106 | Ratio: 4.26
  5. generated_sat_005.cnf
      Vars:  31 | Clauses:  132 | Ratio: 4.26
  6. generated_sat_006.cnf
      Vars:  38 | Clauses:  161 | Ratio: 4.26
  7. generated_sat_007.cnf
      Vars:  45 | Clauses:  191 | Ratio: 4.26
  8. generated_sat_008.cnf
      Vars:  52 | Clauses:  221 | Ratio: 4.26
  9. generated_sat_009.cnf
      Vars:  58 | Clauses:  247 | Ratio: 4.26
 10. generated_sat_010.cnf
      Vars:  65 | Clauses:  276 | Ratio: 4.26
 11. generated_sat_011.cnf
      Vars:  72 | Clauses:  306 | Ratio: 4.26
 12. generated_sat_012.cnf
      Vars:  78 | Clauses:  332 | Ratio: 4.26
 13. generated_sat_013.cnf
      Vars:  85 | Clauses:  362 | Ratio: 4.26
 14. generated_sat_014.cnf
      Vars:  92 | Clauses:  391 | Ratio: 4.26
 15. generated_sat_015.cnf
      Vars:  99 | Clauses:  421 | Ratio: 4.26
 16. generated_sat_016.cnf
      Vars: 105 | Clauses:  447 | Ratio: 4.26
 17. generated_sat_017.cnf
      Vars: 112 | Clauses:  477 | Ratio: 4.26
 18. generated_sat_018.cnf
      Vars: 119 | Clauses:  506 | Ratio: 4.26
 19. generated_sat_019.cnf
      Vars: 126 | Clauses:  536 | Ratio: 4.26
 20. generated_sat_020.cnf
      Vars: 132 | Clauses:  562 | Ratio: 4.26
 21. generated_sat_021.cnf
      Vars: 139 | Clauses:  592 | Ratio: 4.26
 22. generated_sat_022.cnf
      Vars: 146 | Clauses:  621 | Ratio: 4.26
 23. generated_sat_023.cnf
      Vars: 152 | Clauses:  647 | Ratio: 4.26
 24. generated_sat_024.cnf
      Vars: 159 | Clauses:  677 | Ratio: 4.26
 25. generated_sat_025.cnf
      Vars: 166 | Clauses:  707 | Ratio: 4.26
 26. generated_sat_026.cnf
      Vars: 173 | Clauses:  736 | Ratio: 4.26
 27. generated_sat_027.cnf
      Vars: 179 | Clauses:  762 | Ratio: 4.26
 28. generated_sat_028.cnf
      Vars: 186 | Clauses:  792 | Ratio: 4.26
 29. generated_sat_029.cnf
      Vars: 193 | Clauses:  822 | Ratio: 4.26
 30. generated_sat_030.cnf
      Vars: 200 | Clauses:  852 | Ratio: 4.26

======================================================================
