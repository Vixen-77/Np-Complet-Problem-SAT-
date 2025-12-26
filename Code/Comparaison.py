#!/usr/bin/env python3
"""
Script d'analyse de complexité expérimentale pour un solveur SAT.
Analyse les résultats d'exécution et génère des visualisations de performance.

Usage: python analyse_solver.py
"""

import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Configuration de style pour les graphiques
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def parse_solver_output(filepath):
    """
    Parse le fichier de sortie du solveur SAT et extrait les métriques.
    
    Args:
        filepath: Chemin vers le fichier texte de sortie
        
    Returns:
        Liste de dictionnaires contenant les métriques par fichier
    """
    data = []
    current_file = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Erreur: Le fichier '{filepath}' n'a pas été trouvé.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {e}")
        sys.exit(1)
    
    for line in lines:
        line = line.strip()
        
        # Détection du nom de fichier
        if line.startswith("Fichier:"):
            # Si on a déjà des données pour un fichier précédent, on les sauvegarde
            if current_file and 'filename' in current_file:
                data.append(current_file)
            
            # Extraction du nom de fichier
            filename_match = re.search(r'Fichier: (.+)', line)
            if filename_match:
                current_file = {'filename': filename_match.group(1)}
        
        # Extraction du nombre de variables et clauses
        elif "Variables:" in line and "Clauses:" in line:
            vars_match = re.search(r'Variables: (\d+)', line)
            clauses_match = re.search(r'Clauses: (\d+)', line)
            if vars_match and clauses_match:
                current_file['variables'] = int(vars_match.group(1))
                current_file['clauses'] = int(clauses_match.group(1))
                # Taille de l'instance (approximation)
                current_file['instance_size'] = current_file['variables'] + current_file['clauses']
        
        # Extraction des résultats NAIVE
        elif line.startswith("[1/3] NAIVE..."):
            if "TIMEOUT" in line:
                current_file['naive_status'] = 'TIMEOUT'
                current_file['naive_time'] = None
                current_file['naive_nodes'] = None
            else:
                # Format: [1/3] NAIVE... SAT | 0.00s | Noeuds: 40
                result_match = re.search(r'(SAT|UNSAT) \| ([\d.]+)s \| Noeuds: (\d+)', line)
                if result_match:
                    current_file['naive_status'] = result_match.group(1)
                    current_file['naive_time'] = float(result_match.group(2))
                    current_file['naive_nodes'] = int(result_match.group(3))
        
        # Extraction des résultats MOMS
        elif line.startswith("[2/3] MOMS..."):
            if "TIMEOUT" in line:
                current_file['moms_status'] = 'TIMEOUT'
                current_file['moms_time'] = None
                current_file['moms_nodes'] = None
            else:
                result_match = re.search(r'(SAT|UNSAT) \| ([\d.]+)s \| Noeuds: (\d+)', line)
                if result_match:
                    current_file['moms_status'] = result_match.group(1)
                    current_file['moms_time'] = float(result_match.group(2))
                    current_file['moms_nodes'] = int(result_match.group(3))
        
        # Extraction des résultats CDCL
        elif line.startswith("[3/3] CDCL..."):
            if "TIMEOUT" in line:
                current_file['cdcl_status'] = 'TIMEOUT'
                current_file['cdcl_time'] = None
                current_file['cdcl_nodes'] = None
            else:
                result_match = re.search(r'(SAT|UNSAT) \| ([\d.]+)s \| Noeuds: (\d+)', line)
                if result_match:
                    current_file['cdcl_status'] = result_match.group(1)
                    current_file['cdcl_time'] = float(result_match.group(2))
                    current_file['cdcl_nodes'] = int(result_match.group(3))
    
    # Sauvegarder le dernier fichier
    if current_file and 'filename' in current_file:
        data.append(current_file)
    
    return data

def create_dataframe(data):
    """
    Crée un DataFrame pandas à partir des données parsées.
    
    Args:
        data: Liste de dictionnaires des métriques
        
    Returns:
        DataFrame pandas
    """
    if not data:
        print("⚠️  Attention: Aucune donnée n'a été extraite du fichier.")
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    
    # Extraction du numéro de fichier pour tri
    df['file_number'] = df['filename'].str.extract(r'(\d+)\.cnf$').astype(float)
    df = df.sort_values('file_number').reset_index(drop=True)
    
    print(f"✓ {len(df)} instances chargées avec succès")
    return df

def save_to_csv(df, output_path='resultats_solver.csv'):
    """
    Sauvegarde le DataFrame dans un fichier CSV.
    
    Args:
        df: DataFrame à sauvegarder
        output_path: Chemin du fichier CSV de sortie
    """
    try:
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"✓ Données sauvegardées dans '{output_path}'")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du CSV: {e}")

def plot_time_vs_variables(df, output_dir='plots'):
    """
    Graphique: Temps d'exécution en fonction du nombre de variables.
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Filtrer les données valides (non-timeout)
    for solver, color, marker in [
        ('naive', '#e74c3c', 'o'),
        ('moms', '#3498db', 's'),
        ('cdcl', '#2ecc71', '^')
    ]:
        valid_data = df[df[f'{solver}_time'].notna()]
        if not valid_data.empty:
            ax.scatter(valid_data['variables'], valid_data[f'{solver}_time'],
                      label=solver.upper(), alpha=0.7, s=100, 
                      color=color, marker=marker, edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel('Nombre de Variables', fontsize=12, fontweight='bold')
    ax.set_ylabel('Temps d\'exécution (secondes)', fontsize=12, fontweight='bold')
    ax.set_title('Temps d\'exécution vs Nombre de Variables', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'temps_vs_variables.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Graphique sauvegardé: {output_path}")
    plt.close()

def plot_time_vs_instance_size(df, output_dir='plots'):
    """
    Graphique: Temps d'exécution en fonction de la taille de l'instance.
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    for solver, color, marker in [
        ('naive', '#e74c3c', 'o'),
        ('moms', '#3498db', 's'),
        ('cdcl', '#2ecc71', '^')
    ]:
        valid_data = df[df[f'{solver}_time'].notna()]
        if not valid_data.empty:
            ax.scatter(valid_data['instance_size'], valid_data[f'{solver}_time'],
                      label=solver.upper(), alpha=0.7, s=100,
                      color=color, marker=marker, edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel('Taille de l\'instance (Variables + Clauses)', 
                  fontsize=12, fontweight='bold')
    ax.set_ylabel('Temps d\'exécution (secondes)', fontsize=12, fontweight='bold')
    ax.set_title('Temps d\'exécution vs Taille de l\'instance', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'temps_vs_taille_instance.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Graphique sauvegardé: {output_path}")
    plt.close()

def plot_nodes_vs_variables(df, output_dir='plots'):
    """
    Graphique: Nombre de nœuds explorés en fonction du nombre de variables.
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    for solver, color, marker in [
        ('naive', '#e74c3c', 'o'),
        ('moms', '#3498db', 's'),
        ('cdcl', '#2ecc71', '^')
    ]:
        valid_data = df[df[f'{solver}_nodes'].notna()]
        if not valid_data.empty:
            ax.scatter(valid_data['variables'], valid_data[f'{solver}_nodes'],
                      label=solver.upper(), alpha=0.7, s=100,
                      color=color, marker=marker, edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel('Nombre de Variables', fontsize=12, fontweight='bold')
    ax.set_ylabel('Nœuds explorés', fontsize=12, fontweight='bold')
    ax.set_title('Nœuds explorés vs Nombre de Variables', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    ax.set_xscale('log')
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'noeuds_vs_variables.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Graphique sauvegardé: {output_path}")
    plt.close()

def plot_solver_comparison_boxplot(df, output_dir='plots'):
    """
    Graphique: Comparaison des temps d'exécution par solveur (boxplot).
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    # Préparer les données pour le boxplot
    plot_data = []
    for solver in ['naive', 'moms', 'cdcl']:
        valid_times = df[df[f'{solver}_time'].notna()][f'{solver}_time']
        for time in valid_times:
            plot_data.append({'Solveur': solver.upper(), 'Temps (s)': time})
    
    if not plot_data:
        print("⚠️  Pas assez de données pour le boxplot de comparaison")
        return
    
    plot_df = pd.DataFrame(plot_data)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.boxplot(data=plot_df, x='Solveur', y='Temps (s)', 
                palette=['#e74c3c', '#3498db', '#2ecc71'], ax=ax)
    
    ax.set_ylabel('Temps d\'exécution (secondes)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Solveur', fontsize=12, fontweight='bold')
    ax.set_title('Distribution des temps d\'exécution par solveur', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'comparaison_solveurs_boxplot.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Graphique sauvegardé: {output_path}")
    plt.close()

def plot_success_rate(df, output_dir='plots'):
    """
    Graphique: Taux de succès (non-timeout) par solveur.
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    success_rates = {}
    for solver in ['naive', 'moms', 'cdcl']:
        total = len(df)
        successes = len(df[df[f'{solver}_status'] != 'TIMEOUT'])
        success_rates[solver.upper()] = (successes / total) * 100
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(success_rates.keys(), success_rates.values(), 
                   color=['#e74c3c', '#3498db', '#2ecc71'], 
                   edgecolor='black', linewidth=1.5, alpha=0.8)
    
    # Ajouter les pourcentages sur les barres
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', 
                fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Taux de succès (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Solveur', fontsize=12, fontweight='bold')
    ax.set_title('Taux de succès (instances résolues sans timeout)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 110)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_path = Path(output_dir) / 'taux_succes.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Graphique sauvegardé: {output_path}")
    plt.close()

def print_statistics(df):
    """
    Affiche des statistiques descriptives sur les résultats.
    """
    print("\n" + "="*70)
    print("STATISTIQUES DESCRIPTIVES")
    print("="*70)
    
    for solver in ['naive', 'moms', 'cdcl']:
        print(f"\n{solver.upper()}:")
        print("-" * 40)
        
        # Taux de succès
        total = len(df)
        timeouts = len(df[df[f'{solver}_status'] == 'TIMEOUT'])
        success = total - timeouts
        print(f"  Instances résolues: {success}/{total} ({success/total*100:.1f}%)")
        print(f"  Timeouts: {timeouts}/{total} ({timeouts/total*100:.1f}%)")
        
        # Temps d'exécution
        valid_times = df[df[f'{solver}_time'].notna()][f'{solver}_time']
        if not valid_times.empty:
            print(f"  Temps moyen: {valid_times.mean():.3f}s")
            print(f"  Temps médian: {valid_times.median():.3f}s")
            print(f"  Temps min/max: {valid_times.min():.3f}s / {valid_times.max():.3f}s")
        
        # Nœuds explorés
        valid_nodes = df[df[f'{solver}_nodes'].notna()][f'{solver}_nodes']
        if not valid_nodes.empty:
            print(f"  Nœuds moyens: {valid_nodes.mean():.0f}")
            print(f"  Nœuds médians: {valid_nodes.median():.0f}")

def main():
    """
    Fonction principale du script d'analyse.
    """
    print("\n" + "="*70)
    print("ANALYSE DE COMPLEXITÉ DU SOLVEUR SAT")
    print("="*70 + "\n")
    
    # Déterminer le répertoire du script
    script_dir = Path(__file__).parent
    
    # 1. Parser le fichier de sortie
    input_file = script_dir / 'resultats_solver.txt'
    print(f"📂 Lecture du fichier: {input_file}")
    data = parse_solver_output(input_file)
    
    # 2. Créer le DataFrame
    df = create_dataframe(data)
    if df.empty:
        print("\n❌ Aucune donnée à analyser. Vérifiez le format du fichier.")
        return
    
    # 3. Sauvegarder en CSV
    print("\n💾 Sauvegarde des données...")
    csv_path = script_dir / 'resultats_solver.csv'
    save_to_csv(df, csv_path)
    
    # 4. Afficher les statistiques
    print_statistics(df)
    
    # 5. Générer les graphiques
    print("\n📊 Génération des graphiques...")
    plots_dir = script_dir / 'plots'
    plot_time_vs_variables(df, plots_dir)
    plot_time_vs_instance_size(df, plots_dir)
    plot_nodes_vs_variables(df, plots_dir)
    plot_solver_comparison_boxplot(df, plots_dir)
    plot_success_rate(df, plots_dir)
    
    print("\n" + "="*70)
    print("✅ ANALYSE TERMINÉE AVEC SUCCÈS")
    print("="*70)
    print("\n📁 Fichiers générés:")
    print("  - resultats_solver.csv (données brutes)")
    print("  - plots/temps_vs_variables.png")
    print("  - plots/temps_vs_taille_instance.png")
    print("  - plots/noeuds_vs_variables.png")
    print("  - plots/comparaison_solveurs_boxplot.png")
    print("  - plots/taux_succes.png")
    print()

if __name__ == "__main__":
    main()