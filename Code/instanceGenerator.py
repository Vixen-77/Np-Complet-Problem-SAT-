import random
import os
from pathlib import Path

class HardCNFGenerator:
    """
    Générateur d'instances CNF DIFFICILES 
    Range: 5 à 200 variables (30 instances)
    """
    
    def __init__(self):
        self.instances = []
    
    def generate_hard_3sat(self, num_vars, ratio=4.26):
        """
        Génère une instance 3-SAT DIFFICILE au seuil critique
        
        Args:
            num_vars: Nombre de variables (5-200)
            ratio: Ratio clauses/variables (4.26 = seuil critique pour 3-SAT)
        """
        num_clauses = int(num_vars * ratio)
        
        lines = []
        lines.append("c Hard 3-SAT instance at phase transition threshold")
        lines.append(f"c Variables: {num_vars}")
        lines.append(f"c Clauses: {num_clauses}")
        lines.append(f"c Ratio: {ratio:.2f} (critical threshold)")
        lines.append(f"p cnf {num_vars} {num_clauses}")
        
        # Utiliser un set pour éviter les clauses dupliquées
        clauses_set = set()
        attempts = 0
        max_attempts = num_clauses * 10
        
        while len(clauses_set) < num_clauses and attempts < max_attempts:
            attempts += 1
            
            # Choisir 3 variables DISTINCTES aléatoirement
            k = min(3, num_vars)  # Si moins de 3 vars, prendre toutes
            vars_in_clause = random.sample(range(1, num_vars + 1), k)
            
            # Assigner polarités aléatoires (50/50)
            clause = tuple(
                v if random.random() < 0.5 else -v 
                for v in vars_in_clause
            )
            
            # Éviter les clauses triviales (x ∨ ¬x ∨ y)
            if not self._is_trivial_clause(clause):
                clauses_set.add(clause)
        
        # Convertir en liste et mélanger
        clauses_list = list(clauses_set)
        random.shuffle(clauses_list)
        
        # Écrire les clauses
        for clause in clauses_list:
            lines.append(" ".join(map(str, clause)) + " 0")
        
        return "\n".join(lines)
    
    def _is_trivial_clause(self, clause):
        """Vérifie si une clause contient x et ¬x (toujours vraie)"""
        vars_set = set(abs(lit) for lit in clause)
        return len(vars_set) < len(clause)
    
    def generate_progressive_instances(self, count=30, min_vars=5, max_vars=200):
        """
        Génère 30 instances de difficulté PROGRESSIVE
        De 5 à 200 variables
        """
        print("\n" + "="*70)
        print(f"GÉNÉRATION DE {count} INSTANCES DIFFICILES (3-SAT CRITIQUE)")
        print(f"Variables: {min_vars} → {max_vars}")
        print("="*70)
        
        instances = []
        
        # Créer une progression linéaire de 5 à 200 variables
        var_counts = []
        step = (max_vars - min_vars) / (count - 1)
        
        for i in range(count):
            num_vars = int(min_vars + i * step)
            var_counts.append(num_vars)
        
        # Générer les instances
        for i, num_vars in enumerate(var_counts):
            # Ratio critique : 4.26 pour 3-SAT (seuil de transition de phase)
            ratio = 4.26
            num_clauses = int(num_vars * ratio)
            
            instance = self.generate_hard_3sat(num_vars, ratio)
            
            instances.append({
                'content': instance,
                'vars': num_vars,
                'clauses': num_clauses,
                'ratio': ratio,
                'type': 'hard_sat'
            })
            
            # Affichage avec barre de progression
            progress = "█" * ((i + 1) * 50 // count)
            remaining = "░" * (50 - len(progress))
            
            print(f"[{progress}{remaining}] Instance {i+1:02d}/{count}: "
                  f"{num_vars:3d} vars, {num_clauses:4d} clauses (ratio: {ratio:.2f})")
        
        self.instances = instances
        return instances
    
    def save_instances(self, directory="../Res"):
        """
        Sauvegarde toutes les instances au format .cnf
        """
        Path(directory).mkdir(exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"SAUVEGARDE DES INSTANCES DANS '{directory}/'")
        print(f"{'='*70}")
        
        for i, instance in enumerate(self.instances):
            # Nom de fichier : generated_sat_XXX.cnf
            filename = f"{directory}/generated_sat_{i+1:03d}.cnf"
            
            # Sauvegarder le fichier .cnf
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(instance['content'])
            
            vars_count = instance['vars']
            clauses_count = instance['clauses']
            ratio = instance['ratio']
            
            # Estimation de difficulté
            if vars_count < 50:
                difficulty = "Facile"
                color = "🟢"
            elif vars_count < 100:
                difficulty = "Moyen"
                color = "🟡"
            elif vars_count < 150:
                difficulty = "Difficile"
                color = "🟠"
            else:
                difficulty = "Très Difficile"
                color = "🔴"
            
            print(f"{color} {filename}")
            print(f"   └─ {vars_count:3d} vars | {clauses_count:4d} clauses | "
                  f"ratio: {ratio:.2f} | {difficulty}")
        
        # Créer un README détaillé
        self._create_readme(directory)
        
        print(f"\n{'='*70}")
        print(f"✅ TOTAL: {len(self.instances)} fichiers .cnf générés")
        print(f"{'='*70}")
    
    def _create_readme(self, directory):
        """Crée un fichier README détaillé"""
        readme_path = f"{directory}/README_HARD_INSTANCES.txt"
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("INSTANCES CNF DIFFICILES - SAT SOLVER BENCHMARK\n")
            f.write("="*70 + "\n\n")
            
            f.write("📊 STATISTIQUES GÉNÉRALES:\n")
            f.write(f"   • Total d'instances: {len(self.instances)}\n")
            f.write(f"   • Variables: 5 → 200 (progression linéaire)\n")
            f.write(f"   • Type: 3-SAT au seuil critique (ratio ≈ 4.26)\n")
            f.write(f"   • Format: DIMACS CNF\n\n")
            
            f.write("🎯 POURQUOI CES INSTANCES SONT DIFFICILES:\n")
            f.write("   • Ratio clauses/variables = 4.26 (seuil de transition de phase)\n")
            f.write("   • À ce ratio, 3-SAT est statistiquement le PLUS DUR\n")
            f.write("   • ~50% des instances sont SAT, ~50% UNSAT\n")
            f.write("   • Aucune structure exploitable → force brute nécessaire\n\n")
            
            f.write("📈 COMPLEXITÉ ATTENDUE:\n")
            f.write("   • < 50 vars   : NAIVE & MOMS peuvent résoudre\n")
            f.write("   • 50-100 vars : Seul CDCL réussit (quelques secondes)\n")
            f.write("   • 100-150 vars: CDCL peut prendre plusieurs minutes\n")
            f.write("   • > 150 vars  : Très difficile, risque de TIMEOUT\n\n")
            
            f.write("🔧 UTILISATION:\n")
            f.write("   ./SATSolverOptimised\n")
            f.write("   (Le programme teste automatiquement tous les fichiers)\n\n")
            
            f.write("📋 DÉTAILS DES INSTANCES:\n")
            f.write("-"*70 + "\n")
            
            for i, inst in enumerate(self.instances):
                f.write(f"{i+1:3d}. generated_sat_{i+1:03d}.cnf\n")
                f.write(f"      Vars: {inst['vars']:3d} | Clauses: {inst['clauses']:4d} | ")
                f.write(f"Ratio: {inst['ratio']:.2f}\n")
            
            f.write("\n" + "="*70 + "\n")
        
        print(f"📄 README créé: {readme_path}")


def main():
    """
    Menu principal simplifié
    """
    print("\n" + "="*70)
    print("GÉNÉRATEUR D'INSTANCES CNF DIFFICILES - SAT BENCHMARK")
    print("="*70)
    
    generator = HardCNFGenerator()
    
    print("\n🎯 Configuration:")
    print("   • Nombre d'instances: 30")
    print("   • Variables: 5 → 200 (progression linéaire)")
    print("   • Type: 3-SAT au seuil critique (ratio 4.26)")
    print("   • Difficulté: MAXIMALE (transition de phase)")
    
    choice = input("\n➤ Générer les 30 instances? (o/n): ").strip().lower()
    
    if choice == 'o' or choice == 'y':
        # Générer les instances
        generator.generate_progressive_instances(count=30, min_vars=5, max_vars=200)
        
        # Sauvegarder automatiquement
        generator.save_instances(directory="../Res")
        
        print("\n✅ Génération terminée avec succès!")
        print("📁 Fichiers disponibles dans: ../Res/")
        print("\n💡 Conseil: Commence par tester les petites instances (<50 vars)")
        print("   puis augmente progressivement pour mesurer les limites de CDCL.")
    else:
        print("\n❌ Génération annulée.")


if __name__ == "__main__":
    main()