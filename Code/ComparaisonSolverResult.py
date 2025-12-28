import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns

class SATSolverResultsAnalyzer:
    """
    Analyse les résultats du SAT Solver à partir du fichier texte de sortie
    Génère des graphiques de comparaison et un fichier CSV
    """
    
    def __init__(self, results_file):
        self.results_file = results_file
        self.results = []
        self.df = None
    
    def parse_results(self):
        """Parser le fichier texte de résultats"""
        print("🔍 Parsing du fichier de résultats...")
        
        with open(self.results_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern pour extraire les informations de chaque instance
        pattern = r'Fichier: (.+?\.cnf)\s*-+\s*Variables: (\d+) \| Clauses: (\d+)\s*\n\[1/3\] NAIVE\.\.\.\s*(.+?)\s*\n\[2/3\] MOMS\.\.\.\s*(.+?)\s*\n\[3/3\] CDCL\.\.\.\s*(.+?)(?=\n\n|$)'
        
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            filename = match.group(1).strip()
            num_vars = int(match.group(2))
            num_clauses = int(match.group(3))
            naive_result = match.group(4).strip()
            moms_result = match.group(5).strip()
            cdcl_result = match.group(6).strip()
            
            # Parser NAIVE
            naive_data = self._parse_solver_result(naive_result)
            
            # Parser MOMS
            moms_data = self._parse_solver_result(moms_result)
            
            # Parser CDCL
            cdcl_data = self._parse_solver_result(cdcl_result)
            
            # Créer l'entrée
            entry = {
                'filename': Path(filename).name,
                'variables': num_vars,
                'clauses': num_clauses,
                'ratio_clauses_vars': num_clauses / num_vars if num_vars > 0 else 0,
                
                # NAIVE
                'naive_result': naive_data['result'],
                'naive_time': naive_data['time'],
                'naive_nodes': naive_data['nodes'],
                
                # MOMS
                'moms_result': moms_data['result'],
                'moms_time': moms_data['time'],
                'moms_nodes': moms_data['nodes'],
                
                # CDCL
                'cdcl_result': cdcl_data['result'],
                'cdcl_time': cdcl_data['time'],
                'cdcl_nodes': cdcl_data['nodes']
            }
            
            self.results.append(entry)
        
        print(f"✓ {len(self.results)} instances analysées")
        return self.results
    
    def _parse_solver_result(self, result_str):
        """Parser un résultat individuel (SAT/UNSAT/TIMEOUT)"""
        data = {
            'result': 'UNKNOWN',
            'time': None,
            'nodes': None
        }
        
        if 'TIMEOUT' in result_str:
            data['result'] = 'TIMEOUT'
            # Extraire le timeout
            timeout_match = re.search(r'TIMEOUT \((\d+)s\)', result_str)
            if timeout_match:
                data['time'] = float(timeout_match.group(1))
        elif 'SAT' in result_str or 'UNSAT' in result_str:
            # Extraire SAT/UNSAT
            if 'UNSAT' in result_str:
                data['result'] = 'UNSAT'
            else:
                data['result'] = 'SAT'
            
            # Extraire le temps
            time_match = re.search(r'(\d+\.\d+)s', result_str)
            if time_match:
                data['time'] = float(time_match.group(1))
            
            # Extraire les nœuds
            nodes_match = re.search(r'Noeuds: (\d+)', result_str)
            if nodes_match:
                data['nodes'] = int(nodes_match.group(1))
        
        return data
    
    def create_dataframe(self):
        """Créer un DataFrame pandas"""
        self.df = pd.DataFrame(self.results)
        
        print("\n📊 Aperçu des données:")
        print(self.df.head(10))
        print(f"\nShape: {self.df.shape}")
        
        return self.df
    
    def save_to_csv(self, output_file='../Res/sat_solver_results.csv'):
        """Sauvegarder les résultats en CSV"""
        if self.df is None:
            self.create_dataframe()
        
        self.df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n✓ CSV sauvegardé: {output_file}")
        
        return output_file
    
    def generate_statistics(self):
        """Générer des statistiques globales"""
        if self.df is None:
            self.create_dataframe()
        
        print("\n" + "="*70)
        print("STATISTIQUES GLOBALES")
        print("="*70)
        
        print("\n📊 INSTANCES:")
        print(f"  Total: {len(self.df)}")
        print(f"  Variables: {self.df['variables'].min()} à {self.df['variables'].max()}")
        print(f"  Clauses: {self.df['clauses'].min()} à {self.df['clauses'].max()}")
        print(f"  Ratio moyen clauses/variables: {self.df['ratio_clauses_vars'].mean():.2f}")
        
        # NAIVE
        print("\n🐌 NAIVE:")
        naive_sat = (self.df['naive_result'] == 'SAT').sum()
        naive_unsat = (self.df['naive_result'] == 'UNSAT').sum()
        naive_timeout = (self.df['naive_result'] == 'TIMEOUT').sum()
        print(f"  SAT: {naive_sat} | UNSAT: {naive_unsat} | TIMEOUT: {naive_timeout}")
        if naive_sat + naive_unsat > 0:
            print(f"  Temps moyen: {self.df[self.df['naive_result'].isin(['SAT', 'UNSAT'])]['naive_time'].mean():.2f}s")
        
        # MOMS
        print("\n🧠 MOMS:")
        moms_sat = (self.df['moms_result'] == 'SAT').sum()
        moms_unsat = (self.df['moms_result'] == 'UNSAT').sum()
        moms_timeout = (self.df['moms_result'] == 'TIMEOUT').sum()
        print(f"  SAT: {moms_sat} | UNSAT: {moms_unsat} | TIMEOUT: {moms_timeout}")
        if moms_sat + moms_unsat > 0:
            print(f"  Temps moyen: {self.df[self.df['moms_result'].isin(['SAT', 'UNSAT'])]['moms_time'].mean():.2f}s")
        
        # CDCL
        print("\n🚀 CDCL:")
        cdcl_sat = (self.df['cdcl_result'] == 'SAT').sum()
        cdcl_unsat = (self.df['cdcl_result'] == 'UNSAT').sum()
        cdcl_timeout = (self.df['cdcl_result'] == 'TIMEOUT').sum()
        print(f"  SAT: {cdcl_sat} | UNSAT: {cdcl_unsat} | TIMEOUT: {cdcl_timeout}")
        print(f"  Temps moyen: {self.df[self.df['cdcl_result'].isin(['SAT', 'UNSAT'])]['cdcl_time'].mean():.2f}s")
        print(f"  Nœuds moyens: {self.df[self.df['cdcl_nodes'].notna()]['cdcl_nodes'].mean():.0f}")
        
        # Comparaison
        print("\n⚡ COMPARAISON:")
        cdcl_success = cdcl_sat + cdcl_unsat
        total = len(self.df)
        print(f"  Taux de succès CDCL: {100*cdcl_success/total:.1f}%")
        print(f"  CDCL résout {cdcl_success} instances (NAIVE: 0, MOMS: 0)")
        
        print("="*70)
    
    def plot_comprehensive_analysis(self):
        """Générer tous les graphiques d'analyse"""
        if self.df is None:
            self.create_dataframe()
        
        # Configuration du style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
        # Créer la figure avec 6 sous-graphiques
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        fig.suptitle('Analyse Complète - SAT Solver Performance', 
                     fontsize=18, fontweight='bold', y=0.995)
        
        # 1. Temps d'exécution CDCL vs Variables
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_cdcl_time_vs_vars(ax1)
        
        # 2. Nœuds explorés vs Variables
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_cdcl_nodes_vs_vars(ax2)
        
        # 3. Distribution SAT/UNSAT/TIMEOUT
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_result_distribution(ax3)
        
        # 4. Temps CDCL: SAT vs UNSAT
        ax4 = fig.add_subplot(gs[1, 0])
        self._plot_sat_vs_unsat_time(ax4)
        
        # 5. Complexité: Log-Log (Temps vs Taille)
        ax5 = fig.add_subplot(gs[1, 1])
        self._plot_complexity_analysis(ax5)
        
        # 6. Ratio Clauses/Variables vs Temps
        ax6 = fig.add_subplot(gs[1, 2])
        self._plot_ratio_vs_time(ax6)
        
        # 7. Performance par taille d'instance
        ax7 = fig.add_subplot(gs[2, 0])
        self._plot_performance_by_size(ax7)
        
        # 8. Nœuds: SAT vs UNSAT
        ax8 = fig.add_subplot(gs[2, 1])
        self._plot_nodes_comparison(ax8)
        
        # 9. Taux de succès par taille
        ax9 = fig.add_subplot(gs[2, 2])
        self._plot_success_rate(ax9)
        
        plt.tight_layout()
        
        # Sauvegarder
        output_file = '../Res/sat_solver_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Graphique complet sauvegardé: {output_file}")
        
        plt.show()
    
    def _plot_cdcl_time_vs_vars(self, ax):
        """Graphique: Temps CDCL vs Variables"""
        df_cdcl = self.df[self.df['cdcl_result'].isin(['SAT', 'UNSAT'])]
        
        sat_data = df_cdcl[df_cdcl['cdcl_result'] == 'SAT']
        unsat_data = df_cdcl[df_cdcl['cdcl_result'] == 'UNSAT']
        
        ax.scatter(sat_data['variables'], sat_data['cdcl_time'], 
                  c='green', s=100, alpha=0.6, label='SAT', edgecolors='black')
        ax.scatter(unsat_data['variables'], unsat_data['cdcl_time'], 
                  c='red', s=100, alpha=0.6, label='UNSAT', edgecolors='black')
        
        # Régression
        if len(df_cdcl) > 2:
            z = np.polyfit(df_cdcl['variables'], df_cdcl['cdcl_time'], 2)
            p = np.poly1d(z)
            x_line = np.linspace(df_cdcl['variables'].min(), df_cdcl['variables'].max(), 100)
            ax.plot(x_line, p(x_line), 'b--', linewidth=2, alpha=0.7, label='Régression')
        
        ax.set_xlabel('Nombre de Variables', fontsize=11, fontweight='bold')
        ax.set_ylabel('Temps (secondes)', fontsize=11, fontweight='bold')
        ax.set_title('CDCL: Temps vs Variables', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_cdcl_nodes_vs_vars(self, ax):
        """Graphique: Nœuds explorés vs Variables"""
        df_cdcl = self.df[self.df['cdcl_nodes'].notna()]
        
        sat_data = df_cdcl[df_cdcl['cdcl_result'] == 'SAT']
        unsat_data = df_cdcl[df_cdcl['cdcl_result'] == 'UNSAT']
        
        ax.scatter(sat_data['variables'], sat_data['cdcl_nodes'], 
                  c='green', s=100, alpha=0.6, label='SAT', edgecolors='black')
        ax.scatter(unsat_data['variables'], unsat_data['cdcl_nodes'], 
                  c='red', s=100, alpha=0.6, label='UNSAT', edgecolors='black')
        
        ax.set_xlabel('Nombre de Variables', fontsize=11, fontweight='bold')
        ax.set_ylabel('Nœuds Explorés', fontsize=11, fontweight='bold')
        ax.set_title('CDCL: Nœuds vs Variables', fontsize=12, fontweight='bold')
        ax.set_yscale('log')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_result_distribution(self, ax):
        """Graphique: Distribution des résultats"""
        cdcl_counts = self.df['cdcl_result'].value_counts()
        
        colors = {'SAT': '#2ecc71', 'UNSAT': '#e74c3c', 'TIMEOUT': '#95a5a6'}
        colors_list = [colors.get(x, 'gray') for x in cdcl_counts.index]
        
        ax.bar(cdcl_counts.index, cdcl_counts.values, color=colors_list, 
               alpha=0.8, edgecolor='black', linewidth=2)
        
        # Ajouter les pourcentages
        total = cdcl_counts.sum()
        for i, (label, count) in enumerate(cdcl_counts.items()):
            percentage = 100 * count / total
            ax.text(i, count + 0.5, f'{count}\n({percentage:.1f}%)', 
                   ha='center', fontsize=10, fontweight='bold')
        
        ax.set_ylabel('Nombre d\'Instances', fontsize=11, fontweight='bold')
        ax.set_title('CDCL: Distribution des Résultats', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_sat_vs_unsat_time(self, ax):
        """Graphique: Temps SAT vs UNSAT"""
        df_cdcl = self.df[self.df['cdcl_result'].isin(['SAT', 'UNSAT'])]
        
        sat_times = df_cdcl[df_cdcl['cdcl_result'] == 'SAT']['cdcl_time']
        unsat_times = df_cdcl[df_cdcl['cdcl_result'] == 'UNSAT']['cdcl_time']
        
        data_to_plot = [sat_times, unsat_times]
        labels = ['SAT', 'UNSAT']
        colors = ['#2ecc71', '#e74c3c']
        
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                       showmeans=True, meanline=True)
        
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        
        ax.set_ylabel('Temps (secondes)', fontsize=11, fontweight='bold')
        ax.set_title('CDCL: Temps SAT vs UNSAT', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_complexity_analysis(self, ax):
        """Graphique: Analyse de complexité (Log-Log)"""
        df_cdcl = self.df[self.df['cdcl_result'].isin(['SAT', 'UNSAT'])]
        
        total_size = df_cdcl['variables'] + df_cdcl['clauses']
        
        sat_data = df_cdcl[df_cdcl['cdcl_result'] == 'SAT']
        unsat_data = df_cdcl[df_cdcl['cdcl_result'] == 'UNSAT']
        
        sat_size = sat_data['variables'] + sat_data['clauses']
        unsat_size = unsat_data['variables'] + unsat_data['clauses']
        
        ax.scatter(sat_size, sat_data['cdcl_time'], 
                  c='green', s=100, alpha=0.6, label='SAT', edgecolors='black')
        ax.scatter(unsat_size, unsat_data['cdcl_time'], 
                  c='red', s=100, alpha=0.6, label='UNSAT', edgecolors='black')
        
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Taille Totale (Variables + Clauses)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Temps (secondes)', fontsize=11, fontweight='bold')
        ax.set_title('Complexité: Log-Log Scale', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, which='both')
    
    def _plot_ratio_vs_time(self, ax):
        """Graphique: Ratio Clauses/Vars vs Temps"""
        df_cdcl = self.df[self.df['cdcl_result'].isin(['SAT', 'UNSAT'])]
        
        sat_data = df_cdcl[df_cdcl['cdcl_result'] == 'SAT']
        unsat_data = df_cdcl[df_cdcl['cdcl_result'] == 'UNSAT']
        
        ax.scatter(sat_data['ratio_clauses_vars'], sat_data['cdcl_time'], 
                  c='green', s=100, alpha=0.6, label='SAT', edgecolors='black')
        ax.scatter(unsat_data['ratio_clauses_vars'], unsat_data['cdcl_time'], 
                  c='red', s=100, alpha=0.6, label='UNSAT', edgecolors='black')
        
        # Ligne verticale au seuil critique (4.26)
        ax.axvline(x=4.26, color='orange', linestyle='--', linewidth=2, 
                  label='Seuil critique 3-SAT', alpha=0.7)
        
        ax.set_xlabel('Ratio Clauses/Variables', fontsize=11, fontweight='bold')
        ax.set_ylabel('Temps (secondes)', fontsize=11, fontweight='bold')
        ax.set_title('Ratio vs Temps', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_performance_by_size(self, ax):
        """Graphique: Performance par catégorie de taille"""
        df_cdcl = self.df[self.df['cdcl_result'].isin(['SAT', 'UNSAT'])]
        
        # Catégoriser par taille
        bins = [0, 50, 100, 150, 200, 300]
        labels = ['<50', '50-100', '100-150', '150-200', '>200']
        df_cdcl['size_category'] = pd.cut(df_cdcl['variables'], bins=bins, labels=labels)
        
        # Temps moyen par catégorie
        avg_times = df_cdcl.groupby('size_category')['cdcl_time'].mean()
        
        ax.bar(range(len(avg_times)), avg_times.values, 
               color='steelblue', alpha=0.7, edgecolor='black', linewidth=2)
        ax.set_xticks(range(len(avg_times)))
        ax.set_xticklabels(avg_times.index)
        ax.set_xlabel('Catégorie de Taille (Variables)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Temps Moyen (secondes)', fontsize=11, fontweight='bold')
        ax.set_title('Performance par Taille', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_nodes_comparison(self, ax):
        """Graphique: Comparaison nœuds SAT vs UNSAT"""
        df_cdcl = self.df[self.df['cdcl_nodes'].notna()]
        
        sat_nodes = df_cdcl[df_cdcl['cdcl_result'] == 'SAT']['cdcl_nodes']
        unsat_nodes = df_cdcl[df_cdcl['cdcl_result'] == 'UNSAT']['cdcl_nodes']
        
        data_to_plot = [sat_nodes, unsat_nodes]
        labels = ['SAT', 'UNSAT']
        colors = ['#2ecc71', '#e74c3c']
        
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                       showmeans=True, meanline=True)
        
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        
        ax.set_ylabel('Nœuds Explorés', fontsize=11, fontweight='bold')
        ax.set_title('Nœuds: SAT vs UNSAT', fontsize=12, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_success_rate(self, ax):
        """Graphique: Taux de succès par taille"""
        # Catégoriser
        bins = [0, 50, 100, 150, 200, 300]
        labels = ['<50', '50-100', '100-150', '150-200', '>200']
        self.df['size_category'] = pd.cut(self.df['variables'], bins=bins, labels=labels)
        
        # Calculer taux de succès
        success_rate = []
        categories = []
        
        for cat in labels:
            cat_data = self.df[self.df['size_category'] == cat]
            if len(cat_data) > 0:
                success = ((cat_data['cdcl_result'] == 'SAT') | 
                          (cat_data['cdcl_result'] == 'UNSAT')).sum()
                rate = 100 * success / len(cat_data)
                success_rate.append(rate)
                categories.append(cat)
        
        colors_rate = ['#2ecc71' if r >= 80 else '#f39c12' if r >= 50 else '#e74c3c' 
                      for r in success_rate]
        
        bars = ax.bar(range(len(success_rate)), success_rate, 
                     color=colors_rate, alpha=0.7, edgecolor='black', linewidth=2)
        
        # Ajouter les pourcentages
        for i, rate in enumerate(success_rate):
            ax.text(i, rate + 2, f'{rate:.1f}%', ha='center', 
                   fontsize=10, fontweight='bold')
        
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories)
        ax.set_xlabel('Catégorie de Taille (Variables)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Taux de Succès (%)', fontsize=11, fontweight='bold')
        ax.set_title('Taux de Succès CDCL', fontsize=12, fontweight='bold')
        ax.set_ylim([0, 105])
        ax.axhline(y=100, color='green', linestyle='--', linewidth=1, alpha=0.5)
        ax.grid(True, alpha=0.3, axis='y')


def main():
    print("="*70)
    print("ANALYSEUR DE RÉSULTATS - SAT SOLVER")
    print("="*70)
    
    # Fichier d'entrée
    results_file = 'TerminalSolver.txt'
    
    # Créer l'analyseur
    analyzer = SATSolverResultsAnalyzer(results_file)
    
    # Parser les résultats
    analyzer.parse_results()
    
    # Créer le DataFrame
    analyzer.create_dataframe()
    
    # Sauvegarder en CSV
    analyzer.save_to_csv()
    
    # Générer les statistiques
    analyzer.generate_statistics()
    
    # Générer les graphiques
    analyzer.plot_comprehensive_analysis()
    
    print("\n✓ Analyse terminée avec succès!")
    print("="*70)


if __name__ == "__main__":
    main()