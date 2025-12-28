"""
======================================================================
ANALYSEUR DE COMPLEXITÉ - RÉDUCTION SAT → 3-SAT
======================================================================
Analyse expérimentale de la croissance des variables et clauses
après réduction SAT vers 3-SAT.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


class ComplexityAnalyzerSAT3SAT:

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.df = None

    def load_data(self):
        if not self.filepath.exists():
            raise FileNotFoundError(f"Fichier introuvable : {self.filepath}")

        # 🔧 FIX MAJEUR : on impose les noms de colonnes
        self.df = pd.read_csv(
            self.filepath,
            header=None,
            names=[
                "OriginalVars",
                "OriginalClauses",
                "Vars3SAT",
                "Clauses3SAT",
                "AuxVars",
                "ClauseRatio",
                "VarGrowth",
                "Time"
            ]
        )

        print("✓ Données chargées avec succès")
        print("\nColonnes détectées :")
        print(self.df.columns.tolist())
        print("\nAperçu des données :")
        print(self.df.head())

    def analyze_complexity(self):
        print("\n======================================================================")
        print("ANALYSE DE COMPLEXITÉ - RÉDUCTION SAT → 3-SAT")
        print("======================================================================")

        print("\n📊 STATISTIQUES GÉNÉRALES:")
        print(f"  Instances analysées: {len(self.df)}")
        print(
            f"  Variables originales: "
            f"{self.df['OriginalVars'].min()} à {self.df['OriginalVars'].max()}"
        )
        print(
            f"  Clauses originales: "
            f"{self.df['OriginalClauses'].min()} à {self.df['OriginalClauses'].max()}"
        )

        print("\n📈 CROISSANCE OBSERVÉE:")
        print(
            f"  Variables après 3-SAT: "
            f"{self.df['Vars3SAT'].min()} à {self.df['Vars3SAT'].max()}"
        )
        print(
            f"  Clauses après 3-SAT: "
            f"{self.df['Clauses3SAT'].min()} à {self.df['Clauses3SAT'].max()}"
        )

        print("\n📐 RATIOS:")
        print(
            f"  Ratio clauses moyen: {self.df['ClauseRatio'].mean():.3f}"
        )
        print(
            f"  Facteur de croissance des variables moyen: "
            f"{self.df['VarGrowth'].mean():.3f}"
        )

        print("\n⏱️ TEMPS D'EXÉCUTION:")
        print(
            f"  Temps min: {self.df['Time'].min():.3f}s"
        )
        print(
            f"  Temps max: {self.df['Time'].max():.3f}s"
        )
        print(
            f"  Temps moyen: {self.df['Time'].mean():.3f}s"
        )

    def plot_growth(self):
        plt.figure()
        plt.scatter(self.df["OriginalVars"], self.df["Vars3SAT"])
        plt.xlabel("Variables originales")
        plt.ylabel("Variables après 3-SAT")
        plt.title("Croissance des variables (SAT → 3-SAT)")
        plt.grid(True)
        plt.show()

        plt.figure()
        plt.scatter(self.df["OriginalClauses"], self.df["Clauses3SAT"])
        plt.xlabel("Clauses originales")
        plt.ylabel("Clauses après 3-SAT")
        plt.title("Croissance des clauses (SAT → 3-SAT)")
        plt.grid(True)
        plt.show()


def main():
    print("=" * 70)
    print("ANALYSEUR DE COMPLEXITÉ - RÉDUCTION SAT → 3-SAT")
    print("=" * 70)

    filepath = "../CSV/reduction_stats.csv"  # adapte si besoin

    analyzer = ComplexityAnalyzerSAT3SAT(filepath)
    analyzer.load_data()
    analyzer.analyze_complexity()
    analyzer.plot_growth()


if __name__ == "__main__":
    main()
