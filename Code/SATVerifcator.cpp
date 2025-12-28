#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <algorithm>
#include <filesystem>

using namespace std;
using namespace std::chrono;
namespace fs = std::filesystem;

// =========================
// STRUCTURES
// =========================
struct Clause {
    vector<int> literals;  // Format: positif = vrai, négatif = faux
    
    bool isSatisfied(const vector<int8_t>& assignment) const {
        for (int lit : literals) {
            int var = abs(lit);
            bool sign = (lit > 0);
            
            // Vérifier si ce littéral est vrai
            if (var < assignment.size() && assignment[var] != -1) {
                bool varValue = (assignment[var] == 1);
                if (varValue == sign) {
                    return true;  // Au moins un littéral vrai → clause satisfaite
                }
            }
        }
        return false;  // Aucun littéral vrai → clause non satisfaite
    }
};

struct CNFInstance {
    int numVars;
    int numClauses;
    vector<Clause> clauses;
    
    CNFInstance() : numVars(0), numClauses(0) {}
};

struct Solution {
    vector<int8_t> assignment;  // -1: non assigné, 0: false, 1: true
    int numVars;
    
    Solution(int vars) : numVars(vars) {
        assignment.resize(vars + 1, -1);  // Index 0 non utilisé
    }
    
    void setLiteral(int lit) {
        int var = abs(lit);
        bool value = (lit > 0);
        
        if (var >= 0 && var < assignment.size()) {
            assignment[var] = value ? 1 : 0;
        }
    }
};

// =========================
// PARSERS
// =========================
class CNFParser {
public:
    static CNFInstance parse(const string& filename) {
        ifstream file(filename);
        if (!file.is_open()) {
            throw runtime_error("Impossible d'ouvrir le fichier CNF: " + filename);
        }
        
        CNFInstance instance;
        string line;
        
        while (getline(file, line)) {
            if (line.empty()) continue;
            
            // Ignorer les commentaires
            if (line[0] == 'c') continue;
            
            // Ligne d'en-tête: "p cnf <numVars> <numClauses>"
            if (line[0] == 'p') {
                istringstream iss(line);
                string p, cnf;
                iss >> p >> cnf >> instance.numVars >> instance.numClauses;
                continue;
            }
            
            // Lire une clause
            istringstream iss(line);
            Clause clause;
            int lit;
            
            while (iss >> lit) {
                if (lit == 0) break;  // Fin de clause
                clause.literals.push_back(lit);
            }
            
            if (!clause.literals.empty()) {
                instance.clauses.push_back(clause);
            }
        }
        
        file.close();
        return instance;
    }
};

class SolutionParser {
public:
    static Solution parse(const string& filename, int numVars) {
        ifstream file(filename);
        if (!file.is_open()) {
            throw runtime_error("Impossible d'ouvrir le fichier solution: " + filename);
        }
        
        Solution solution(numVars);
        string line;
        
        while (getline(file, line)) {
            if (line.empty()) continue;
            
            // Ignorer les commentaires
            if (line[0] == 'c') continue;
            
            // Lire la ligne de solution (commence par "v ")
            if (line[0] == 'v') {
                // Enlever le "v " au début
                line = line.substr(2);
                
                istringstream iss(line);
                int lit;
                
                while (iss >> lit) {
                    if (lit == 0) break;  // Fin de la solution
                    solution.setLiteral(lit);
                }
            }
        }
        
        file.close();
        return solution;
    }
};

// =========================
// VÉRIFICATEUR
// =========================
class SATVerifier {
public:
    static pair<bool, string> verify(const CNFInstance& instance, const Solution& solution) {
        if (instance.clauses.empty()) {
            return {true, "Instance vide (trivialement satisfaite)"};
        }
        
        int satisfiedClauses = 0;
        int unsatisfiedClauses = 0;
        vector<int> unsatisfiedIndices;
        
        // Vérifier chaque clause
        for (size_t i = 0; i < instance.clauses.size(); i++) {
            const Clause& clause = instance.clauses[i];
            
            if (clause.isSatisfied(solution.assignment)) {
                satisfiedClauses++;
            } else {
                unsatisfiedClauses++;
                unsatisfiedIndices.push_back(i);
                
                // Limiter l'affichage à 10 premières clauses non satisfaites
                if (unsatisfiedIndices.size() > 10) break;
            }
        }
        
        // Construire le message de résultat
        ostringstream msg;
        msg << "Clauses satisfaites: " << satisfiedClauses << "/" << instance.clauses.size();
        
        if (unsatisfiedClauses > 0) {
            msg << "\nClauses NON satisfaites: " << unsatisfiedClauses;
            msg << "\nExemples (max 10 premières):";
            
            for (int idx : unsatisfiedIndices) {
                msg << "\n  Clause " << (idx + 1) << ": ";
                const Clause& clause = instance.clauses[idx];
                
                for (size_t j = 0; j < clause.literals.size() && j < 10; j++) {
                    int lit = clause.literals[j];
                    msg << lit << " ";
                }
                if (clause.literals.size() > 10) {
                    msg << "...";
                }
            }
        }
        
        bool isSat = (unsatisfiedClauses == 0);
        return {isSat, msg.str()};
    }
    
    static void printStatistics(const CNFInstance& instance, const Solution& solution) {
        cout << "\n" << string(70, '=') << endl;
        cout << "STATISTIQUES" << endl;
        cout << string(70, '=') << endl;
        
        cout << "Variables déclarées: " << instance.numVars << endl;
        cout << "Clauses déclarées: " << instance.numClauses << endl;
        cout << "Clauses effectives: " << instance.clauses.size() << endl;
        
        // Compter les variables assignées
        int assignedVars = 0;
        int trueVars = 0;
        int falseVars = 0;
        
        for (int i = 1; i <= instance.numVars; i++) {
            if (i < solution.assignment.size() && solution.assignment[i] != -1) {
                assignedVars++;
                if (solution.assignment[i] == 1) trueVars++;
                else falseVars++;
            }
        }
        
        cout << "Variables assignées: " << assignedVars << "/" << instance.numVars << endl;
        cout << "  - TRUE: " << trueVars << endl;
        cout << "  - FALSE: " << falseVars << endl;
        
        // Taille moyenne des clauses
        if (!instance.clauses.empty()) {
            double avgClauseSize = 0;
            int minSize = INT_MAX;
            int maxSize = 0;
            
            for (const auto& clause : instance.clauses) {
                int size = clause.literals.size();
                avgClauseSize += size;
                minSize = min(minSize, size);
                maxSize = max(maxSize, size);
            }
            
            avgClauseSize /= instance.clauses.size();
            
            cout << "\nTaille des clauses:" << endl;
            cout << "  - Moyenne: " << fixed << setprecision(2) << avgClauseSize << endl;
            cout << "  - Min: " << minSize << endl;
            cout << "  - Max: " << maxSize << endl;
        }
        
        cout << string(70, '=') << endl;
    }
};

// =========================
// UTILITAIRES
// =========================
class FileUtils {
public:
    static vector<string> findCNFFiles(const string& directory) {
        vector<string> cnfFiles;
        
        try {
            for (const auto& entry : fs::directory_iterator(directory)) {
                if (entry.is_regular_file()) {
                    string filename = entry.path().filename().string();
                    
                    // Chercher les fichiers .cnf (mais pas .cnf.sol)
                    if (filename.size() > 4 && 
                        filename.substr(filename.size() - 4) == ".cnf" &&
                        filename.substr(filename.size() - 8) != ".cnf.sol") {
                        cnfFiles.push_back(entry.path().string());
                    }
                }
            }
        } catch (const exception& e) {
            cerr << "Erreur lors de la lecture du dossier: " << e.what() << endl;
        }
        
        // Trier par ordre alphabétique
        sort(cnfFiles.begin(), cnfFiles.end());
        
        return cnfFiles;
    }
    
    static bool fileExists(const string& filename) {
        ifstream file(filename);
        return file.good();
    }
};

// =========================
// MAIN
// =========================
int main(int argc, char* argv[]) {
    cout << string(70, '=') << endl;
    cout << "VÉRIFICATEUR DE SOLUTIONS SAT - Format DIMACS" << endl;
    cout << string(70, '=') << endl;
    
    string directory = "../Res/";
    
    // Si un argument est fourni, utiliser ce fichier spécifique
    if (argc >= 2) {
        string cnfFile = argv[1];
        string solFile = cnfFile + ".sol";
        
        cout << "\nMode fichier unique:" << endl;
        cout << "CNF: " << cnfFile << endl;
        cout << "SOL: " << solFile << endl;
        
        if (!FileUtils::fileExists(cnfFile)) {
            cerr << "Erreur: Fichier CNF introuvable: " << cnfFile << endl;
            return 1;
        }
        
        if (!FileUtils::fileExists(solFile)) {
            cerr << "Erreur: Fichier solution introuvable: " << solFile << endl;
            return 1;
        }
        
        try {
            auto startParse = high_resolution_clock::now();
            CNFInstance instance = CNFParser::parse(cnfFile);
            Solution solution = SolutionParser::parse(solFile, instance.numVars);
            auto endParse = high_resolution_clock::now();
            
            auto startVerify = high_resolution_clock::now();
            auto [isSat, details] = SATVerifier::verify(instance, solution);
            auto endVerify = high_resolution_clock::now();
            
            double parseTime = duration_cast<microseconds>(endParse - startParse).count() / 1000.0;
            double verifyTime = duration_cast<microseconds>(endVerify - startVerify).count() / 1000.0;
            
            cout << "\n" << string(70, '-') << endl;
            cout << "RÉSULTAT: " << (isSat ? "✓ SATISFIABLE" : "✗ UNSATISFIABLE") << endl;
            cout << string(70, '-') << endl;
            cout << details << endl;
            cout << "\nTemps de parsing: " << fixed << setprecision(3) << parseTime << " ms" << endl;
            cout << "Temps de vérification: " << verifyTime << " ms" << endl;
            cout << "Temps total: " << (parseTime + verifyTime) << " ms" << endl;
            
            SATVerifier::printStatistics(instance, solution);
            
            return isSat ? 0 : 1;
            
        } catch (const exception& e) {
            cerr << "Erreur: " << e.what() << endl;
            return 1;
        }
    }
    
    // Mode batch : vérifier tous les fichiers du dossier
    cout << "\nMode batch - Dossier: " << directory << endl;
    cout << "Recherche de fichiers .cnf avec solutions .sol..." << endl;
    
    vector<string> cnfFiles = FileUtils::findCNFFiles(directory);
    
    if (cnfFiles.empty()) {
        cout << "Aucun fichier .cnf trouvé dans " << directory << endl;
        return 0;
    }
    
    cout << "Trouvé " << cnfFiles.size() << " fichiers .cnf" << endl;
    cout << string(70, '=') << endl;
    
    int totalFiles = 0;
    int satisfiableCount = 0;
    int unsatisfiableCount = 0;
    int errorCount = 0;
    
    for (const string& cnfFile : cnfFiles) {
        string solFile = cnfFile + ".sol";
        
        // Extraire le nom de base du fichier
        string basename = fs::path(cnfFile).filename().string();
        
        cout << "\n[" << (totalFiles + 1) << "/" << cnfFiles.size() << "] " << basename;
        cout.flush();
        
        // Vérifier si la solution existe
        if (!FileUtils::fileExists(solFile)) {
            cout << " → ⚠ Pas de solution (.sol)" << endl;
            continue;
        }
        
        totalFiles++;
        
        try {
            auto start = high_resolution_clock::now();
            
            CNFInstance instance = CNFParser::parse(cnfFile);
            Solution solution = SolutionParser::parse(solFile, instance.numVars);
            auto [isSat, details] = SATVerifier::verify(instance, solution);
            
            auto end = high_resolution_clock::now();
            double totalTime = duration_cast<microseconds>(end - start).count() / 1000.0;
            
            if (isSat) {
                cout << " → ✓ SAT";
                satisfiableCount++;
            } else {
                cout << " → ✗ UNSAT";
                unsatisfiableCount++;
            }
            
            cout << " (" << fixed << setprecision(2) << totalTime << " ms)";
            cout << " | " << instance.numVars << " vars, " << instance.clauses.size() << " clauses";
            cout << endl;
            
            // Afficher détails si UNSAT
            if (!isSat) {
                cout << "   " << details << endl;
            }
            
        } catch (const exception& e) {
            cout << " →  ERREUR: " << e.what() << endl;
            errorCount++;
        }
    }
    
    // Résumé final
    cout << "\n" << string(70, '=') << endl;
    cout << "RÉSUMÉ FINAL" << endl;
    cout << string(70, '=') << endl;
    cout << "Fichiers vérifiés: " << totalFiles << endl;
    cout << "✓ SATISFIABLE: " << satisfiableCount << endl;
    cout << "✗ UNSATISFIABLE: " << unsatisfiableCount << endl;
    
    if (errorCount > 0) {
        cout << " ERREURS: " << errorCount << endl;
    }
    
    double successRate = totalFiles > 0 ? (100.0 * satisfiableCount / totalFiles) : 0;
    cout << "\nTaux de succès: " << fixed << setprecision(1) << successRate << "%" << endl;
    cout << string(70, '=') << endl;
    
    return 0;
}