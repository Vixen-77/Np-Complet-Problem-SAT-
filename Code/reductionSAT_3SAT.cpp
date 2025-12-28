#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <algorithm>
#include <filesystem>
#include <map>

using namespace std;
using namespace std::chrono;
namespace fs = std::filesystem;

// =========================
// STRUCTURES
// =========================
struct Clause {
    vector<int> literals;  // Format: positif = vrai, négatif = faux
    
    int size() const { return literals.size(); }
    
    bool is3SAT() const { return literals.size() == 3; }
};

struct CNFFormula {
    int numVars;
    int numClauses;
    vector<Clause> clauses;
    
    CNFFormula() : numVars(0), numClauses(0) {}
    
    // Statistiques sur les tailles de clauses
    map<int, int> getClauseSizeDistribution() const {
        map<int, int> dist;
        for (const auto& clause : clauses) {
            dist[clause.size()]++;
        }
        return dist;
    }
};

// =========================
// STATISTIQUES DE RÉDUCTION
// =========================
struct ReductionStats {
    // Avant réduction
    int originalVars;
    int originalClauses;
    map<int, int> originalSizeDist;
    
    // Après réduction
    int reducedVars;
    int reducedClauses;
    int auxVarsAdded;
    
    // Temps
    double reductionTimeMs;
    
    // Complexité pratique
    double variableGrowthRatio;
    double clauseGrowthRatio;
    int totalLiteralsOriginal;
    int totalLiteralsReduced;
    
    void print() const {
        cout << "\n" << string(70, '=') << endl;
        cout << "STATISTIQUES DE RÉDUCTION SAT → 3-SAT" << endl;
        cout << string(70, '=') << endl;
        
        cout << "\n AVANT RÉDUCTION:" << endl;
        cout << "  Variables: " << originalVars << endl;
        cout << "  Clauses: " << originalClauses << endl;
        cout << "  Littéraux totaux: " << totalLiteralsOriginal << endl;
        cout << "\n  Distribution des tailles de clauses:" << endl;
        for (const auto& [size, count] : originalSizeDist) {
            double percent = 100.0 * count / originalClauses;
            cout << "    Taille " << size << ": " << count 
                 << " (" << fixed << setprecision(1) << percent << "%)" << endl;
        }
        
        cout << "\n APRÈS RÉDUCTION:" << endl;
        cout << "  Variables: " << reducedVars 
             << " (+" << auxVarsAdded << " auxiliaires)" << endl;
        cout << "  Clauses: " << reducedClauses << endl;
        cout << "  Littéraux totaux: " << totalLiteralsReduced << endl;
        cout << "  Toutes les clauses sont de taille 3 ✓" << endl;
        
        cout << "\nCOMPLEXITÉ PRATIQUE:" << endl;
        cout << "  Ratio variables: " << fixed << setprecision(3) 
             << variableGrowthRatio << "x" << endl;
        cout << "  Ratio clauses: " << clauseGrowthRatio << "x" << endl;
        cout << "  Ratio littéraux: " 
             << (double)totalLiteralsReduced / totalLiteralsOriginal << "x" << endl;
        cout << "  Temps de réduction: " << setprecision(2) 
             << reductionTimeMs << " ms" << endl;
        
        cout << "\nANALYSE:" << endl;
        if (variableGrowthRatio < 1.5) {
            cout << "  ✓ Croissance linéaire des variables (excellente)" << endl;
        } else if (variableGrowthRatio < 2.0) {
            cout << "  ✓ Croissance modérée des variables (bonne)" << endl;
        } else {
            cout << "  ⚠ Croissance importante des variables" << endl;
        }
        
        if (clauseGrowthRatio < 2.0) {
            cout << "  ✓ Croissance linéaire des clauses (excellente)" << endl;
        } else if (clauseGrowthRatio < 3.0) {
            cout << "  ✓ Croissance modérée des clauses (bonne)" << endl;
        } else {
            cout << "  ⚠ Croissance importante des clauses" << endl;
        }
        
        cout << string(70, '=') << endl;
    }
    
    void saveToCSV(const string& filename) const {
        ofstream csv(filename, ios::app);
        if (!csv.is_open()) {
            // Créer le fichier avec en-tête
            csv.open(filename);
            csv << "OriginalVars,OriginalClauses,ReducedVars,ReducedClauses,"
                << "AuxVars,VarRatio,ClauseRatio,TimeMs\n";
        }
        
        csv << originalVars << "," << originalClauses << ","
            << reducedVars << "," << reducedClauses << ","
            << auxVarsAdded << "," << fixed << setprecision(3)
            << variableGrowthRatio << "," << clauseGrowthRatio << ","
            << setprecision(2) << reductionTimeMs << "\n";
        
        csv.close();
    }
};

// =========================
// PARSER CNF
// =========================
class CNFParser {
public:
    static CNFFormula parse(const string& filename) {
        ifstream file(filename);
        if (!file.is_open()) {
            throw runtime_error("Impossible d'ouvrir: " + filename);
        }
        
        CNFFormula formula;
        string line;
        
        while (getline(file, line)) {
            if (line.empty() || line[0] == 'c') continue;
            
            if (line[0] == 'p') {
                istringstream iss(line);
                string p, cnf;
                iss >> p >> cnf >> formula.numVars >> formula.numClauses;
                continue;
            }
            
            // Lire clause
            istringstream iss(line);
            Clause clause;
            int lit;
            
            while (iss >> lit && lit != 0) {
                clause.literals.push_back(lit);
            }
            
            if (!clause.literals.empty()) {
                formula.clauses.push_back(clause);
            }
        }
        
        file.close();
        return formula;
    }
};

// =========================
// RÉDUCTEUR SAT → 3-SAT
// =========================
class SATto3SATReducer {
private:
    int nextAuxVar;
    
    // Réduire une clause de taille 1 : (x) → 4 clauses 3-SAT
    vector<Clause> reduceSize1(int lit) {
        vector<Clause> result;
        int y = nextAuxVar++;
        int z = nextAuxVar++;
        
        // (x ∨ y ∨ z) ∧ (x ∨ y ∨ ¬z) ∧ (x ∨ ¬y ∨ z) ∧ (x ∨ ¬y ∨ ¬z)
        result.push_back({{lit, y, z}});
        result.push_back({{lit, y, -z}});
        result.push_back({{lit, -y, z}});
        result.push_back({{lit, -y, -z}});
        
        return result;
    }
    
    // Réduire une clause de taille 2 : (x₁ ∨ x₂) → 2 clauses 3-SAT
    vector<Clause> reduceSize2(int lit1, int lit2) {
        vector<Clause> result;
        int y = nextAuxVar++;
        
        // (x₁ ∨ x₂ ∨ y) ∧ (x₁ ∨ x₂ ∨ ¬y)
        result.push_back({{lit1, lit2, y}});
        result.push_back({{lit1, lit2, -y}});
        
        return result;
    }
    
    // Réduire une clause de taille k ≥ 4 : (x₁ ∨ ... ∨ xₖ) → chaîne de clauses
    vector<Clause> reduceSizeK(const vector<int>& lits) {
        vector<Clause> result;
        int k = lits.size();
        
        if (k < 4) return result;  // Ne devrait pas arriver
        
        // Créer k-3 variables auxiliaires
        vector<int> auxVars;
        for (int i = 0; i < k - 3; i++) {
            auxVars.push_back(nextAuxVar++);
        }
        
        // Première clause : (x₁ ∨ x₂ ∨ y₁)
        result.push_back({{lits[0], lits[1], auxVars[0]}});
        
        // Clauses intermédiaires : (¬yᵢ ∨ xᵢ₊₂ ∨ yᵢ₊₁)
        for (int i = 0; i < k - 4; i++) {
            result.push_back({{-auxVars[i], lits[i + 2], auxVars[i + 1]}});
        }
        
        // Dernière clause : (¬yₖ₋₃ ∨ xₖ₋₁ ∨ xₖ)
        result.push_back({{-auxVars[k - 4], lits[k - 2], lits[k - 1]}});
        
        return result;
    }
    
public:
    pair<CNFFormula, ReductionStats> reduce(const CNFFormula& original) {
        auto startTime = high_resolution_clock::now();
        
        CNFFormula reduced;
        ReductionStats stats;
        
        // Initialiser les variables auxiliaires après les originales
        nextAuxVar = original.numVars + 1;
        
        // Statistiques originales
        stats.originalVars = original.numVars;
        stats.originalClauses = original.clauses.size();
        stats.originalSizeDist = original.getClauseSizeDistribution();
        stats.totalLiteralsOriginal = 0;
        
        for (const auto& clause : original.clauses) {
            stats.totalLiteralsOriginal += clause.size();
        }
        
        // Réduction clause par clause
        for (const auto& clause : original.clauses) {
            int size = clause.size();
            
            if (size == 0) {
                // Clause vide → formule insatisfaisable
                continue;
            } else if (size == 1) {
                // Taille 1 → 4 clauses
                auto newClauses = reduceSize1(clause.literals[0]);
                reduced.clauses.insert(reduced.clauses.end(), 
                                      newClauses.begin(), newClauses.end());
            } else if (size == 2) {
                // Taille 2 → 2 clauses
                auto newClauses = reduceSize2(clause.literals[0], clause.literals[1]);
                reduced.clauses.insert(reduced.clauses.end(), 
                                      newClauses.begin(), newClauses.end());
            } else if (size == 3) {
                // Taille 3 → inchangée
                reduced.clauses.push_back(clause);
            } else {
                // Taille ≥ 4 → chaîne de clauses
                auto newClauses = reduceSizeK(clause.literals);
                reduced.clauses.insert(reduced.clauses.end(), 
                                      newClauses.begin(), newClauses.end());
            }
        }
        
        // Finaliser la formule réduite
        reduced.numVars = nextAuxVar - 1;
        reduced.numClauses = reduced.clauses.size();
        
        // Calculer les statistiques
        stats.reducedVars = reduced.numVars;
        stats.reducedClauses = reduced.numClauses;
        stats.auxVarsAdded = reduced.numVars - original.numVars;
        
        stats.variableGrowthRatio = (double)stats.reducedVars / stats.originalVars;
        stats.clauseGrowthRatio = (double)stats.reducedClauses / stats.originalClauses;
        
        stats.totalLiteralsReduced = 0;
        for (const auto& clause : reduced.clauses) {
            stats.totalLiteralsReduced += clause.size();
        }
        
        auto endTime = high_resolution_clock::now();
        stats.reductionTimeMs = duration_cast<microseconds>(endTime - startTime).count() / 1000.0;
        
        return {reduced, stats};
    }
};

// =========================
// WRITER CNF
// =========================
class CNFWriter {
public:
    static void write(const CNFFormula& formula, const string& filename) {
        ofstream file(filename);
        if (!file.is_open()) {
            throw runtime_error("Impossible de créer: " + filename);
        }
        
        // En-tête
        file << "c Formule 3-SAT générée par réduction" << endl;
        file << "c Variables originales: " << formula.numVars - formula.clauses.size() << endl;
        file << "c Variables totales (avec auxiliaires): " << formula.numVars << endl;
        file << "p cnf " << formula.numVars << " " << formula.numClauses << endl;
        
        // Clauses
        for (const auto& clause : formula.clauses) {
            for (int lit : clause.literals) {
                file << lit << " ";
            }
            file << "0" << endl;
        }
        
        file.close();
    }
};

// =========================
// CONVERTISSEUR DE SOLUTIONS
// =========================
class SolutionConverter {
public:
    // Extraire uniquement les variables originales d'une solution 3-SAT
    static void convertSolution(const string& solution3SAT, 
                                const string& solutionSAT,
                                int originalVars) {
        ifstream in(solution3SAT);
        ofstream out(solutionSAT);
        
        if (!in.is_open() || !out.is_open()) {
            cerr << "Erreur: Impossible de convertir la solution" << endl;
            return;
        }
        
        string line;
        while (getline(in, line)) {
            if (line.empty() || line[0] == 'c') {
                out << line << endl;
                continue;
            }
            
            if (line[0] == 'v') {
                out << "v ";
                istringstream iss(line.substr(2));
                int lit;
                
                while (iss >> lit && lit != 0) {
                    int var = abs(lit);
                    // Garder seulement les variables originales
                    if (var <= originalVars) {
                        out << lit << " ";
                    }
                }
                out << "0" << endl;
            }
        }
        
        in.close();
        out.close();
        
        cout << "✓ Solution convertie: " << solutionSAT << endl;
    }
};

// =========================
// MAIN
// =========================
int main() {
    cout << string(70, '=') << endl;
    cout << "RÉDUCTEUR SAT → 3-SAT + ANALYSE DE COMPLEXITÉ" << endl;
    cout << string(70, '=') << endl;
    
    string inputDir = "../Bejing/";
    string outputDir = "../Reductions/";
    
    // Créer le dossier de sortie
    fs::create_directories(outputDir);
    
    // Trouver tous les fichiers .cnf
    vector<string> cnfFiles;
    for (const auto& entry : fs::directory_iterator(inputDir)) {
        if (entry.is_regular_file()) {
            string filename = entry.path().filename().string();
            if (filename.size() > 4 && 
                filename.substr(filename.size() - 4) == ".cnf" &&
                filename.find(".3sat.cnf") == string::npos) {
                cnfFiles.push_back(entry.path().string());
            }
        }
    }
    
    sort(cnfFiles.begin(), cnfFiles.end());
    
    cout << "\nTrouvé " << cnfFiles.size() << " fichiers .cnf" << endl;
    cout << "Dossier de sortie: " << outputDir << endl;
    cout << string(70, '=') << endl;
    
    // Fichier CSV pour les statistiques globales
    string csvFile = outputDir + "reduction_stats.csv";
    if (fs::exists(csvFile)) {
        fs::remove(csvFile);  // Réinitialiser
    }
    
    SATto3SATReducer reducer;
    int successCount = 0;
    
    for (size_t i = 0; i < cnfFiles.size(); i++) {
        const string& inputFile = cnfFiles[i];
        string basename = fs::path(inputFile).filename().string();
        string outputFile = outputDir + basename.substr(0, basename.size() - 4) + ".3sat.cnf";
        
        cout << "\n[" << (i + 1) << "/" << cnfFiles.size() << "] " << basename << endl;
        cout << string(70, '-') << endl;
        
        try {
            // Parser l'original
            CNFFormula original = CNFParser::parse(inputFile);
            
            cout << "Original: " << original.numVars << " vars, " 
                 << original.clauses.size() << " clauses" << endl;
            
            // Réduire
            auto [reduced, stats] = reducer.reduce(original);
            
            cout << "Réduit: " << reduced.numVars << " vars (+" 
                 << stats.auxVarsAdded << " aux), " 
                 << reduced.numClauses << " clauses" << endl;
            
            // Sauvegarder
            CNFWriter::write(reduced, outputFile);
            
            cout << "✓ Sauvegardé: " << outputFile << endl;
            cout << "  Ratio variables: " << fixed << setprecision(2) 
                 << stats.variableGrowthRatio << "x" << endl;
            cout << "  Ratio clauses: " << stats.clauseGrowthRatio << "x" << endl;
            cout << "  Temps: " << stats.reductionTimeMs << " ms" << endl;
            
            // Sauvegarder les stats
            stats.saveToCSV(csvFile);
            
            successCount++;
            
        } catch (const exception& e) {
            cout << "❌ Erreur: " << e.what() << endl;
        }
    }
    
    cout << "\n" << string(70, '=') << endl;
    cout << "RÉSUMÉ FINAL" << endl;
    cout << string(70, '=') << endl;
    cout << "Fichiers traités: " << successCount << "/" << cnfFiles.size() << endl;
    cout << "Statistiques sauvegardées: " << csvFile << endl;
    cout << string(70, '=') << endl;
    
    return 0;
}