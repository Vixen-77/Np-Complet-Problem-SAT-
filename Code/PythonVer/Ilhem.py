import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import random
import time


###############################################
#          analyseur           
##############################################

class AnalyseurResultats:
    def __init__(self):
        self.resultats = []
    
    def ajouter_test(self, n_vars, n_clauses, temps, satisfiable, source="random"):
        """Enregistre un résultat de test"""
        ratio = n_clauses / n_vars if n_vars > 0 else 0
        
        self.resultats.append({
            'source': source,
            'n_vars': n_vars,
            'n_clauses': n_clauses,
            'ratio': ratio,
            'temps': temps,
            'satisfiable': satisfiable
        })
    
    def generer_dataframe(self):
        """Convertit les résultats en DataFrame pandas"""
        return pd.DataFrame(self.resultats)
    
    def statistiques_par_taille(self):
        """Calcule statistiques groupées par nombre de variables"""
        df = self.generer_dataframe()
        
        stats = df.groupby('n_vars').agg({
            'temps': ['mean', 'std', 'min', 'max', 'count'],
            'satisfiable': lambda x: (x == True).sum() / len(x) * 100  # % SAT
        }).round(4)
        
        stats.columns = ['temps_moyen', 'temps_std', 'temps_min', 'temps_max', 'nb_tests', 'pct_sat']
        
        return stats
    
    def statistiques_par_ratio(self):
        """Calcule statistiques groupées par ratio clauses/vars"""
        df = self.generer_dataframe()
        
        # Créer des bins de ratio
        df['ratio_bin'] = pd.cut(df['ratio'], bins=[0, 2, 3, 4, 5, 10], 
                                labels=['<2', '2-3', '3-4', '4-5', '>5'])
        
        stats = df.groupby('ratio_bin').agg({
            'temps': ['mean', 'std'],
            'satisfiable': lambda x: (x == True).sum() / len(x) * 100
        }).round(4)
        
        return stats
    
    def detecter_anomalies(self, seuil_std=3):
        """Détecte les temps d'exécution anormalement longs"""
        df = self.generer_dataframe()
        
        anomalies = []
        
        for n_vars in df['n_vars'].unique():
            subset = df[df['n_vars'] == n_vars]
            
            mean_temps = subset['temps'].mean()
            std_temps = subset['temps'].std()
            
            for idx, row in subset.iterrows():
                z_score = (row['temps'] - mean_temps) / std_temps if std_temps > 0 else 0
                
                if abs(z_score) > seuil_std:
                    anomalies.append({
                        'n_vars': row['n_vars'],
                        'n_clauses': row['n_clauses'],
                        'temps': row['temps'],
                        'z_score': z_score,
                        'satisfiable': row['satisfiable']
                    })
        
        return pd.DataFrame(anomalies)
    
    def tracer_graphes(self, save_path='analyse_sat.png'):
        """Génère tous les graphes d'analyse"""
        df = self.generer_dataframe()
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Analyse Complète SAT Solver', fontsize=16, fontweight='bold')
        
        # ===== Graphe 1: Temps vs Nombre de Variables =====
        stats = df.groupby('n_vars')['temps'].agg(['mean', 'std'])
        axes[0, 0].errorbar(stats.index, stats['mean'], yerr=stats['std'], 
                        marker='o', capsize=5, capthick=2, color='blue')
        axes[0, 0].set_xlabel('Nombre de variables', fontsize=12)
        axes[0, 0].set_ylabel('Temps (s)', fontsize=12)
        axes[0, 0].set_title('Temps moyen ± écart-type')
        axes[0, 0].set_yscale('log')
        axes[0, 0].grid(True, alpha=0.3)
        
        # ===== Graphe 2: Temps SAT vs UNSAT =====
        sat_data = df[df['satisfiable'] == True]
        unsat_data = df[df['satisfiable'] == False]
        
        axes[0, 1].scatter(sat_data['n_vars'], sat_data['temps'], 
                        alpha=0.6, label='SAT', color='green', s=50)
        axes[0, 1].scatter(unsat_data['n_vars'], unsat_data['temps'], 
                        alpha=0.6, label='UNSAT', color='red', s=50)
        axes[0, 1].set_xlabel('Nombre de variables', fontsize=12)
        axes[0, 1].set_ylabel('Temps (s)', fontsize=12)
        axes[0, 1].set_title('Comparaison SAT vs UNSAT')
        axes[0, 1].set_yscale('log')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # ===== Graphe 3: Distribution des Temps =====
        axes[0, 2].hist(df['temps'], bins=30, color='purple', alpha=0.7, edgecolor='black')
        axes[0, 2].set_xlabel('Temps (s)', fontsize=12)
        axes[0, 2].set_ylabel('Fréquence', fontsize=12)
        axes[0, 2].set_title('Distribution des Temps d\'Exécution')
        axes[0, 2].set_xscale('log')
        axes[0, 2].grid(True, alpha=0.3)
        
        # ===== Graphe 4: Ratio Clauses/Variables vs Temps =====
        axes[1, 0].scatter(df['ratio'], df['temps'], alpha=0.5, color='orange')
        axes[1, 0].axvline(x=4.27, color='red', linestyle='--', 
                        label='Ratio critique (4.27)', linewidth=2)
        axes[1, 0].set_xlabel('Ratio clauses/variables', fontsize=12)
        axes[1, 0].set_ylabel('Temps (s)', fontsize=12)
        axes[1, 0].set_title('Impact du Ratio sur le Temps')
        axes[1, 0].set_yscale('log')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # ===== Graphe 5: Pourcentage SAT par Taille =====
        pct_sat = df.groupby('n_vars')['satisfiable'].apply(
            lambda x: (x == True).sum() / len(x) * 100
        )
        axes[1, 1].bar(pct_sat.index, pct_sat.values, color='teal', alpha=0.7)
        axes[1, 1].set_xlabel('Nombre de variables', fontsize=12)
        axes[1, 1].set_ylabel('% SAT', fontsize=12)
        axes[1, 1].set_title('Pourcentage d\'Instances Satisfaisables')
        axes[1, 1].set_ylim([0, 105])
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        # ===== Graphe 6: Boxplot Temps par Taille =====
        df.boxplot(column='temps', by='n_vars', ax=axes[1, 2])
        axes[1, 2].set_xlabel('Nombre de variables', fontsize=12)
        axes[1, 2].set_ylabel('Temps (s)', fontsize=12)
        axes[1, 2].set_title('Variabilité des Temps par Taille')
        axes[1, 2].set_yscale('log')
        axes[1, 2].get_figure().suptitle('')  # Supprimer titre auto
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n✅ Graphes sauvegardés: {save_path}")
        plt.show()
    
    def generer_rapport_texte(self):
        """Génère un rapport textuel complet"""
        df = self.generer_dataframe()
        
        rapport = []
        rapport.append("=" * 70)
        rapport.append("RAPPORT D'ANALYSE SAT SOLVER")
        rapport.append("=" * 70)
        
        # Statistiques globales
        rapport.append("\n📊 STATISTIQUES GLOBALES")
        rapport.append("-" * 70)
        rapport.append(f"Nombre total de tests: {len(df)}")
        rapport.append(f"Temps moyen: {df['temps'].mean():.4f}s")
        rapport.append(f"Temps médian: {df['temps'].median():.4f}s")
        rapport.append(f"Temps min: {df['temps'].min():.4f}s")
        rapport.append(f"Temps max: {df['temps'].max():.4f}s")
        rapport.append(f"Pourcentage SAT: {(df['satisfiable']==True).sum()/len(df)*100:.1f}%")
        rapport.append(f"Pourcentage UNSAT: {(df['satisfiable']==False).sum()/len(df)*100:.1f}%")
        
        # Statistiques par taille
        rapport.append("\n📈 STATISTIQUES PAR NOMBRE DE VARIABLES")
        rapport.append("-" * 70)
        stats_taille = self.statistiques_par_taille()
        rapport.append(str(stats_taille))
        
        # Anomalies
        rapport.append("\n⚠️  ANOMALIES DÉTECTÉES (z-score > 3)")
        rapport.append("-" * 70)
        anomalies = self.detecter_anomalies()
        if len(anomalies) > 0:
            rapport.append(str(anomalies))
        else:
            rapport.append("Aucune anomalie détectée")
        
        # Recommandations
        rapport.append("\n💡 RECOMMANDATIONS")
        rapport.append("-" * 70)
        
        temps_max = df['temps'].max()
        n_vars_max = df.loc[df['temps'].idxmax(), 'n_vars']
        
        if temps_max > 1.0:
            rapport.append(f"⚠️  Temps maximum élevé: {temps_max:.2f}s (n={n_vars_max})")
            rapport.append("   → Considérer DPLL ou heuristiques")
        
        std_global = df.groupby('n_vars')['temps'].std().mean()
        if std_global > df['temps'].mean():
            rapport.append("⚠️  Forte variabilité des temps")
            rapport.append("   → Augmenter nombre de tests par taille")
        
        rapport.append("\n" + "=" * 70)
        
        return "\n".join(rapport)
###############################################################
#           verificateur naive
###############################################################

def verifier_solution_SAT(clauses, solution):
    """
    Vérifie si une solution satisfait toutes les clauses
    
    Args:
        clauses: Liste de clauses (liste de listes d'entiers)
        solution: Dictionnaire {variable: True/False}
    
    Returns:
        (bool, str): (True si valide, message explicatif)
    """
    if solution is None:
        return False, "Solution est None (UNSAT)"
    
    for i, clause in enumerate(clauses):
        clause_satisfaite = False
        
        for literal in clause:
            variable = abs(literal)
            
            # Vérifier que la variable est assignée
            if variable not in solution:
                return False, f"Variable {variable} non assignée dans la solution"
            
            valeur = solution[variable]
            
            # Literal positif et variable vraie OU literal négatif et variable fausse
            if (literal > 0 and valeur) or (literal < 0 and not valeur):
                clause_satisfaite = True
                break
        
        if not clause_satisfaite:
            return False, f"Clause {i+1} non satisfaite: {clause}"
    
    return True, f"Solution valide ! Toutes les {len(clauses)} clauses satisfaites"


def verifier_UNSAT(clauses, solution):
    """
    Vérifie qu'une instance est bien UNSAT
    (Pour test exhaustif - seulement petites instances)
    """
    if solution is not None:
        return False, "Solution trouvée, donc pas UNSAT"
    
    return True, "Aucune solution trouvée (UNSAT vérifié)"

def generer_formule_SAT_controlee(n_vars, ratio_clauses=4.0):
    """Génère formule avec ratio contrôlé"""
    n_clauses = int(n_vars * ratio_clauses)
    formule = []
    
    for _ in range(n_clauses):
        taille_clause = random.randint(1, 5)
        variables_choisies = random.sample(range(1, n_vars + 1), 
                                        min(taille_clause, n_vars))
        clause = [v if random.random() < 0.5 else -v for v in variables_choisies]
        formule.append(clause)
    
    return formule

def evaluate(assignment, clause):
    undecided = False
    for lit in clause:
        var = abs(lit)
        if var not in assignment:
            undecided = True
            continue
        val = assignment[var]
        if lit < 0:
            val = not val
        if val:
            return True
    if undecided:
        return None
    return False

def unasigned_var(clauses, assignment):
    for clause in clauses:              
        for lit in clause:              
            var = abs(lit)              
            if var not in assignment:   
                return var              
    return None                        

def SAT(clauses, assignment):
    # Check all clauses
    all_satisfied = True
    for clause in clauses:
        val = evaluate(assignment, clause)
        if val is False:       # clause violated
            return None        # backtrack
        if val is None:        # clause undecided
            all_satisfied = False

    if all_satisfied:
        return assignment

    # Pick one unassigned variable globally
    x = unasigned_var(clauses, assignment)
    if x is None:
        return None

    # Branch True
    assignment[x] = True
    result = SAT(clauses, assignment)
    if result:
        return result

    # Branch False
    assignment[x] = False
    result = SAT(clauses, assignment)
    if result:
        return result

    # Backtrack
    assignment.pop(x)
    return None

# ========================================
# TESTS AUTOMATISÉS
# ========================================

print("🚀 Démarrage des tests automatisés...\n")

analyseur = AnalyseurResultats()

# Test avec tailles croissantes
tailles = [5, 10, 15, 20, 25, 30, 35, 40]
nb_tests_par_taille = 10

for n_vars in tailles:
    print(f"Testing n={n_vars} variables...")
    
    for essai in range(nb_tests_par_taille):
        # Générer instance
        formule = generer_formule_SAT_controlee(n_vars, ratio_clauses=4.0)
        
        # Mesurer temps
        start = time.time()
        solution = SAT(formule, {})
        temps = time.time() - start
        
        # Vérifier solution
        if solution is not None:
            valide, msg = verifier_solution_SAT(formule, solution)
            if not valide:
                print(f"❌ ERREUR: {msg}")
                continue
        
        # Enregistrer
        analyseur.ajouter_test(
            n_vars=n_vars,
            n_clauses=len(formule),
            temps=temps,
            satisfiable=(solution is not None),
            source="random"
        )
        
        print(f"  Essai {essai+1}: {temps:.4f}s - {'SAT' if solution else 'UNSAT'}")

# ========================================
# GÉNÉRATION DU RAPPORT
# ========================================

print("\n" + "="*70)
print("GÉNÉRATION DU RAPPORT D'ANALYSE")
print("="*70)

# Rapport texte
rapport = analyseur.generer_rapport_texte()
print(rapport)

# Sauvegarder rapport
with open('rapport_sat_analyse.txt', 'w', encoding='utf-8') as f:
    f.write(rapport)
print("\n✅ Rapport texte sauvegardé: rapport_sat_analyse.txt")

# Graphes
analyseur.tracer_graphes(save_path='analyse_sat_graphes.png')

# DataFrame complet
df = analyseur.generer_dataframe()
df.to_csv('resultats_sat_complets.csv', index=False)
print("✅ Résultats CSV sauvegardés: resultats_sat_complets.csv")

print("\n🎉 Analyse terminée avec succès!")
