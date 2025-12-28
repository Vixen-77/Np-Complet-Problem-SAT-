# SAT SOLVER – Implementation & Experimental Analysis

Ce projet implémente et analyse la résolution du problème **SAT** ainsi que sa **réduction vers 3-SAT**, en combinant des implémentations **C++** (performance, résolution) et **Python** (génération, analyse et visualisation).

Il s’inscrit dans un cadre académique (algorithmique / complexité) et s’appuie sur un **dataset CNF fourni par le professeur**.

---

## 📁 Structure générale du projet

.
├── Benjing/ # Dataset CNF fourni par le professeur
├── Code/ # Implémentations C++ et Python
├── CSV/ # Résultats expérimentaux (statistiques)
├── Python_plot/ # Graphiques générés automatiquement
├── Reductions/ # Résultats de réduction SAT → 3-SAT
├── Res/ # Instances CNF + solutions
├── ResSol/ # Résultats détaillés des solveurs
├── terminalOUTPUT_CPP/ # Sorties terminal des programmes C++
├── UNSAT/ # Instances reconnues comme UNSAT
├── README.md
└── .gitignore


---

## 📂 Benjing/
Contient le **dataset d’instances SAT au format `.cnf`**, fourni par le professeur via un lien dans le PDF du cours.  
Ces instances servent de base pour :
- la résolution SAT
- la réduction SAT → 3-SAT
- l’analyse expérimentale de la complexité

---

## 📂 Code/
Ce dossier contient **3 codes C++** et **3 codes Python**.

### 🔹 C++ (résolution et réduction)

Les programmes C++ sont utilisés pour leur **performance** et implémentent des solveurs SAT ainsi que la réduction SAT → 3-SAT.

- **`SATSOlverOPtimised2.cpp`**  
  Solveur SAT implémentant :
  - une approche **naïve (brute force)**
  - l’heuristique **MOMS**
  - l’algorithme **CDCL (Conflict-Driven Clause Learning)**  
  👉 CDCL est l’algorithme le plus performant et constitue le point central de l’analyse.

  Le solveur est testé sur :
  - 2 instances issues du dataset du professeur
  - 22 instances générées personnellement

  Il indique si l’instance est **SAT** ou **UNSAT**, ainsi que :
  - le temps d’exécution
  - le nombre de nœuds explorés

- **`SATVerificator.cpp`**  
  Vérificateur de solution SAT.  
  Il valide que la solution produite par le solveur C++ satisfait réellement toutes les clauses de l’instance CNF.

- **`reductionSAT_3SAT.cpp`**  
  Implémente la **réduction complète SAT → 3-SAT** sur l’ensemble du dataset *Benjing*.  
  Génère :
  - les nouvelles instances 3-SAT
  - des statistiques (variables, clauses, ratios)
  - un fichier CSV utilisé pour l’analyse de complexité

---

### 🔹 Python (génération, analyse, visualisation)

- **`instanceGenerator.py`**  
  Génère des instances SAT au format **DIMACS CNF**, en respectant strictement le format fourni par le professeur.

- **`ComparisonSolverResult.py`**  
  Compare les résultats obtenus par le solveur C++ (avec un accent particulier sur **CDCL**).  
  Génère des graphiques comparant :
  - temps d’exécution
  - efficacité relative des méthodes

- **`reductionAnalyser.py`**  
  Analyse les fichiers CSV générés par le réducteur C++.  
  Produit des graphiques illustrant :
  - la croissance du nombre de variables
  - la croissance du nombre de clauses  
  afin de valider expérimentalement la **complexité polynomiale** de la réduction SAT → 3-SAT.

---

## 📂 CSV/
Contient les résultats expérimentaux sous forme tabulaire.

- **`reduction_stats.csv`**  
  Statistiques issues de la réduction SAT → 3-SAT

- **`sat_solver_results.csv`**  
  Résultats du solveur SAT (temps, méthode, statut SAT/UNSAT)

---

## 📂 Python_plot/
Dossier de sortie automatique des graphiques générés par les scripts Python.

Exemples :
- `growth_variables_sat_3sat.png`
- `growth_clauses_sat_3sat.png`
- `sat_solver_analysis.png`

Ces figures sont directement exploitables dans un rapport ou une soutenance.

---

## 📂 Res/
Fichiers importants liés aux instances et solutions.

- **`.cnf`**  
  Fichiers d’instances SAT au format DIMACS.

- **`.cnf.sol`**  
  Solution produite par le solveur C++ lorsque l’instance est **SAT**.

---

## ⚠️ NOTE IMPORTANTE
Si le solveur C++ conclut qu’une instance est **UNSAT**,  
👉 **aucun fichier `.cnf.sol` n’est généré**.

Dans ce cas, seules les informations suivantes sont produites :
- temps d’exécution
- nombre de nœuds explorés

---

## 🎯 Objectifs du projet

- Implémenter et comparer différentes stratégies de résolution SAT
- Mettre en évidence l’efficacité de CDCL
- Vérifier expérimentalement la complexité de la réduction SAT → 3-SAT
- Relier théorie (NP-complétude) et pratique expérimentale

---

## 🧠 Remarque finale
Ce projet met l’accent sur la **rigueur algorithmique**, la **reproductibilité expérimentale** et l’**analyse de complexité**, conformément aux exigences académiques.
