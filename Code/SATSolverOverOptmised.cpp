#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <map>
#include <unordered_map>
#include <queue>
#include <sstream>
#include <iomanip>

using namespace std;
using namespace std::chrono;

// =========================
// CONFIGURATION
// =========================
const int TIMEOUT_NAIVE = 30;
const int TIMEOUT_MOMS = 30;
const int TIMEOUT_CDCL = 1800;

// =========================
// STRUCTURES
// =========================
struct Lit {
    int var;
    bool sign;
    
    Lit(int v = 0, bool s = true) : var(v), sign(s) {}
    int toInt() const { return sign ? var : -var; }
    Lit operator~() const { return Lit(var, !sign); }
    bool operator==(const Lit& other) const { return var == other.var && sign == other.sign; }
};

struct Clause {
    vector<Lit> literals;
    int id;
    
    Clause(const vector<Lit>& lits = {}, int i = -1) : literals(lits), id(i) {}
};

struct Assignment {
    vector<int8_t> values;
    vector<int> trail;
    
    Assignment(int maxVars = 0) { 
        values.resize(maxVars + 1, -1);
    }
    
    bool contains(int var) const { 
        return var > 0 && var < values.size() && values[var] != -1; 
    }
    
    bool getValue(int var) const { return values[var] == 1; }
    
    void assign(int var, bool value) {
        if (var <= 0 || var >= values.size()) return;
        values[var] = value ? 1 : 0;
        trail.push_back(var);
    }
    
    void unassign(int var) {
        if (var <= 0 || var >= values.size()) return;
        values[var] = -1;
    }
    
    void backtrackTo(int position) {
        while (trail.size() > position) {
            unassign(trail.back());
            trail.pop_back();
        }
    }
    
    size_t size() const { return trail.size(); }
};

// =========================
// TIMEOUT MANAGER
// =========================
class TimeoutManager {
    high_resolution_clock::time_point startTime;
    int timeoutSeconds;
    int checkCounter;
    
public:
    TimeoutManager(int seconds) : timeoutSeconds(seconds), checkCounter(0) {
        startTime = high_resolution_clock::now();
    }
    
    void check() {
        if (++checkCounter % 10000 == 0) {
            auto elapsed = duration_cast<seconds>(high_resolution_clock::now() - startTime).count();
            if (elapsed > timeoutSeconds) throw runtime_error("TIMEOUT");
        }
    }
};

// =========================
// CNF PARSER
// =========================
class CNFParser {
public:
    static pair<vector<Clause>, int> parse(const string& filename) {
        ifstream file(filename);
        if (!file.is_open()) throw runtime_error("Impossible d'ouvrir: " + filename);
        
        vector<Clause> clauses;
        int numVars = 0, clauseId = 0;
        string line;
        
        while (getline(file, line)) {
            if (line.empty() || line[0] == 'c') continue;
            
            if (line[0] == 'p') {
                istringstream iss(line);
                string p, cnf;
                int numClauses;
                iss >> p >> cnf >> numVars >> numClauses;
                continue;
            }
            
            istringstream iss(line);
            vector<Lit> literals;
            int lit;
            
            while (iss >> lit && lit != 0) {
                literals.push_back(Lit(abs(lit), lit > 0));
            }
            
            if (!literals.empty()) {
                clauses.push_back(Clause(literals, clauseId++));
            }
        }
        
        return {clauses, numVars};
    }
};

// =========================
// AFFICHAGE ET SAUVEGARDE
// =========================
void saveSolutionToFile(const Assignment& assignment, int numVars, 
                       const string& inputFile, double time, long long nodes) {
    ofstream out(inputFile + ".sol");
    if (!out.is_open()) return;
    
    out << "c Solution pour " << inputFile << endl;
    out << "c Temps: " << fixed << setprecision(3) << time << "s" << endl;
    out << "c Noeuds: " << nodes << endl;
    out << "v ";
    
    for (int i = 1; i <= numVars; i++) {
        if (assignment.contains(i)) {
            out << (assignment.getValue(i) ? i : -i) << " ";
        }
    }
    out << "0" << endl;
    out.close();
}

// =========================
// NAIVE SOLVER
// =========================
class NaiveSolver {
    static long long nodesExplored;
    
    static bool isSatisfied(const vector<Clause>& clauses, const Assignment& assignment) {
        for (const auto& clause : clauses) {
            bool satisfied = false;
            for (const auto& lit : clause.literals) {
                if (assignment.contains(lit.var) && assignment.getValue(lit.var) == lit.sign) {
                    satisfied = true;
                    break;
                }
            }
            if (!satisfied) return false;
        }
        return true;
    }
    
    static bool dpll(const vector<Clause>& clauses, Assignment& assignment, 
                     int numVars, TimeoutManager* tm) {
        nodesExplored++;
        if (tm) tm->check();
        
        if (isSatisfied(clauses, assignment)) return true;
        
        int var = -1;
        for (int i = 1; i <= numVars; i++) {
            if (!assignment.contains(i)) {
                var = i;
                break;
            }
        }
        
        if (var == -1) return false;
        
        assignment.assign(var, true);
        if (dpll(clauses, assignment, numVars, tm)) return true;
        assignment.unassign(var);
        
        assignment.assign(var, false);
        if (dpll(clauses, assignment, numVars, tm)) return true;
        assignment.unassign(var);
        
        return false;
    }
    
public:
    static pair<bool, Assignment> solve(const vector<Clause>& clauses, int numVars, TimeoutManager* tm) {
        nodesExplored = 0;
        Assignment assignment(numVars);
        bool result = dpll(clauses, assignment, numVars, tm);
        return {result, assignment};
    }
    
    static long long getNodesExplored() { return nodesExplored; }
};

long long NaiveSolver::nodesExplored = 0;

// =========================
// MOMS SOLVER
// =========================
class MOMSSolver {
    static long long nodesExplored;
    
    static int selectVariableMOMS(const vector<Clause>& clauses, const Assignment& assignment) {
        unordered_map<int, int> litCount;
        
        for (const auto& clause : clauses) {
            bool satisfied = false;
            for (const auto& lit : clause.literals) {
                if (assignment.contains(lit.var) && assignment.getValue(lit.var) == lit.sign) {
                    satisfied = true;
                    break;
                }
            }
            
            if (!satisfied) {
                for (const auto& lit : clause.literals) {
                    if (!assignment.contains(lit.var)) {
                        litCount[lit.toInt()]++;
                    }
                }
            }
        }
        
        if (litCount.empty()) return -1;
        
        int bestLit = litCount.begin()->first;
        int maxCount = litCount.begin()->second;
        
        for (const auto& [lit, count] : litCount) {
            if (count > maxCount) {
                maxCount = count;
                bestLit = lit;
            }
        }
        
        return abs(bestLit);
    }
    
    static bool isSatisfied(const vector<Clause>& clauses, const Assignment& assignment) {
        for (const auto& clause : clauses) {
            bool satisfied = false;
            for (const auto& lit : clause.literals) {
                if (assignment.contains(lit.var) && assignment.getValue(lit.var) == lit.sign) {
                    satisfied = true;
                    break;
                }
            }
            if (!satisfied) return false;
        }
        return true;
    }
    
    static bool dpll(const vector<Clause>& clauses, Assignment& assignment, 
                     int numVars, TimeoutManager* tm) {
        nodesExplored++;
        if (tm) tm->check();
        
        if (isSatisfied(clauses, assignment)) return true;
        
        int var = selectVariableMOMS(clauses, assignment);
        if (var == -1) return false;
        
        assignment.assign(var, true);
        if (dpll(clauses, assignment, numVars, tm)) return true;
        assignment.unassign(var);
        
        assignment.assign(var, false);
        if (dpll(clauses, assignment, numVars, tm)) return true;
        assignment.unassign(var);
        
        return false;
    }
    
public:
    static pair<bool, Assignment> solve(const vector<Clause>& clauses, int numVars, TimeoutManager* tm) {
        nodesExplored = 0;
        Assignment assignment(numVars);
        bool result = dpll(clauses, assignment, numVars, tm);
        return {result, assignment};
    }
    
    static long long getNodesExplored() { return nodesExplored; }
};

long long MOMSSolver::nodesExplored = 0;

// =========================
// CDCL OPTIMISÉ AVEC WATCHED LITERALS
// =========================
class FastCDCLSolver {
    static long long nodesExplored;
    vector<Clause> clauses;
    int numVars;
    Assignment assignment;
    
    // Watched literals: watches[lit] = liste des indices de clauses qui watchent ce littéral
    vector<vector<int>> watches;
    
    // VSIDS
    vector<double> activity;
    double varInc, varDecay;
    
    void initWatches() {
        watches.resize(2 * numVars + 2);
        
        for (int i = 0; i < clauses.size(); i++) {
            auto& c = clauses[i];
            if (c.literals.size() >= 1) {
                int lit = c.literals[0].toInt();
                int idx = litToIdx(lit);
                watches[idx].push_back(i);
            }
            if (c.literals.size() >= 2) {
                int lit = c.literals[1].toInt();
                int idx = litToIdx(lit);
                watches[idx].push_back(i);
            }
        }
    }
    
    int litToIdx(int lit) const {
        return lit > 0 ? (2 * lit) : (2 * (-lit) + 1);
    }
    
    bool propagate(TimeoutManager* tm) {
        queue<int> propQueue;
        
        // Ajouter le dernier assignement
        if (!assignment.trail.empty()) {
            int var = assignment.trail.back();
            bool val = assignment.getValue(var);
            int falseLit = val ? -var : var;
            propQueue.push(falseLit);
        }
        
        while (!propQueue.empty()) {
            if (tm) tm->check();
            
            int falseLit = propQueue.front();
            propQueue.pop();
            
            int watchIdx = litToIdx(falseLit);
            auto& watchList = watches[watchIdx];
            
            // Parcourir les clauses qui watchent ce littéral FAUX
            for (size_t i = 0; i < watchList.size(); ) {
                int clauseIdx = watchList[i];
                auto& clause = clauses[clauseIdx];
                
                // Vérifier si clause satisfaite ou unitaire
                bool satisfied = false;
                Lit unassignedLit;
                int unassignedCount = 0;
                
                for (const auto& lit : clause.literals) {
                    if (assignment.contains(lit.var)) {
                        if (assignment.getValue(lit.var) == lit.sign) {
                            satisfied = true;
                            break;
                        }
                    } else {
                        unassignedLit = lit;
                        unassignedCount++;
                    }
                }
                
                if (satisfied) {
                    i++;
                    continue;
                }
                
                if (unassignedCount == 0) {
                    // CONFLIT
                    return false;
                }
                
                if (unassignedCount == 1) {
                    // Propagation unitaire
                    assignment.assign(unassignedLit.var, unassignedLit.sign);
                    bumpActivity(unassignedLit.var);
                    
                    int newFalseLit = unassignedLit.sign ? -unassignedLit.var : unassignedLit.var;
                    propQueue.push(newFalseLit);
                }
                
                i++;
            }
        }
        
        return true;
    }
    
    void bumpActivity(int var) {
        if (var <= 0 || var >= activity.size()) return;
        activity[var] += varInc;
        if (activity[var] > 1e100) {
            for (auto& a : activity) a *= 1e-100;
            varInc *= 1e-100;
        }
    }
    
    void decayActivities() {
        varInc /= varDecay;
    }
    
    int selectVariable() {
        int bestVar = -1;
        double bestScore = -1;
        
        for (int i = 1; i <= numVars; i++) {
            if (!assignment.contains(i) && activity[i] > bestScore) {
                bestScore = activity[i];
                bestVar = i;
            }
        }
        
        return bestVar;
    }
    
public:
    FastCDCLSolver(const vector<Clause>& cls, int nv) 
        : clauses(cls), numVars(nv), assignment(nv), varInc(1.0), varDecay(0.95) {
        activity.resize(nv + 1, 0.0);
        initWatches();
    }
    
    pair<bool, Assignment> solve(TimeoutManager* tm) {
        nodesExplored = 0;
        int conflicts = 0;
        int decisions = 0;
        
        while (decisions < 1000000) {
            nodesExplored++;
            decisions++;
            
            if (tm) tm->check();
            
            // Propagation
            if (!propagate(tm)) {
                conflicts++;
                
                // Backtrack
                if (assignment.trail.size() <= 1) {
                    return {false, assignment}; // UNSAT
                }
                
                int backtrackPos = assignment.trail.size() / 2;
                assignment.backtrackTo(backtrackPos);
                
                // Decay VSIDS
                if (conflicts % 50 == 0) {
                    decayActivities();
                }
                
                // Restart
                if (conflicts > 100) {
                    assignment.backtrackTo(0);
                    conflicts = 0;
                }
                
                continue;
            }
            
            // Vérifier si satisfait
            if (assignment.size() == numVars) {
                bool allSat = true;
                for (const auto& clause : clauses) {
                    bool clauseSat = false;
                    for (const auto& lit : clause.literals) {
                        if (assignment.contains(lit.var) && 
                            assignment.getValue(lit.var) == lit.sign) {
                            clauseSat = true;
                            break;
                        }
                    }
                    if (!clauseSat) {
                        allSat = false;
                        break;
                    }
                }
                
                if (allSat) return {true, assignment};
            }
            
            // Décision
            int var = selectVariable();
            if (var == -1) {
                for (int i = 1; i <= numVars; i++) {
                    if (!assignment.contains(i)) {
                        var = i;
                        break;
                    }
                }
            }
            
            if (var == -1) return {assignment.size() == numVars, assignment};
            
            bool polarity = (decisions % 3 == 0) ? false : true;
            assignment.assign(var, polarity);
        }
        
        return {false, assignment};
    }
    
    static long long getNodesExplored() { return nodesExplored; }
};

long long FastCDCLSolver::nodesExplored = 0;

// =========================
// MAIN
// =========================
int main() {
    cout << string(80, '=') << endl;
    cout << "SAT SOLVER - CDCL OPTIMISE" << endl;
    cout << string(80, '=') << endl;
    cout << "\nTimeouts: NAIVE=30s | MOMS=30s | CDCL=30min\n" << endl;
    
    vector<string> testFiles = {
        "../Res/2bitcomp_5.cnf",
        "../Res/2bitmax_6.cnf",
        "../Res/generated_sat_001.cnf",
        "../Res/generated_sat_002.cnf",
        "../Res/generated_sat_003.cnf",
        "../Res/generated_sat_004.cnf",
        "../Res/generated_sat_005.cnf",
        "../Res/generated_sat_006.cnf",
        "../Res/generated_sat_007.cnf",
        "../Res/generated_sat_008.cnf",
        "../Res/generated_sat_009.cnf",
        "../Res/generated_sat_010.cnf",
        "../Res/generated_sat_011.cnf",
        "../Res/generated_sat_012.cnf",
        "../Res/generated_sat_013.cnf",
        "../Res/generated_sat_014.cnf",
        "../Res/generated_sat_015.cnf",
        "../Res/generated_sat_016.cnf",
        "../Res/generated_sat_017.cnf",
        "../Res/generated_sat_018.cnf",
        "../Res/generated_sat_019.cnf",
        "../Res/generated_sat_020.cnf",
        "../Res/generated_sat_021.cnf",
        "../Res/generated_sat_022.cnf",
        "../Res/generated_sat_023.cnf",
        "../Res/generated_sat_024.cnf",
        "../Res/generated_sat_025.cnf",
        "../Res/generated_sat_026.cnf",
        "../Res/generated_sat_027.cnf",
        "../Res/generated_sat_028.cnf",
        "../Res/generated_sat_029.cnf",
        "../Res/generated_sat_030.cnf"
    };
    
    for (const auto& filename : testFiles) {
        cout << "\n" << string(80, '-') << endl;
        cout << "Fichier: " << filename << endl;
        cout << string(80, '-') << endl;
        
        try {
            auto [clauses, numVars] = CNFParser::parse(filename);
            cout << "Variables: " << numVars << " | Clauses: " << clauses.size() << endl;
            
            // NAIVE
            cout << "\n[1/3] NAIVE...";
            cout.flush();
            try {
                TimeoutManager tm(TIMEOUT_NAIVE);
                auto start = high_resolution_clock::now();
                auto [sat, sol] = NaiveSolver::solve(clauses, numVars, &tm);
                auto duration = duration_cast<milliseconds>(high_resolution_clock::now() - start).count() / 1000.0;
                
                cout << " " << (sat ? "SAT" : "UNSAT") 
                     << " | " << fixed << setprecision(2) << duration << "s"
                     << " | Noeuds: " << NaiveSolver::getNodesExplored() << endl;
            } catch (const runtime_error&) {
                cout << " TIMEOUT (30s)" << endl;
            }
            
            // MOMS
            cout << "[2/3] MOMS...";
            cout.flush();
            try {
                TimeoutManager tm(TIMEOUT_MOMS);
                auto start = high_resolution_clock::now();
                auto [sat, sol] = MOMSSolver::solve(clauses, numVars, &tm);
                auto duration = duration_cast<milliseconds>(high_resolution_clock::now() - start).count() / 1000.0;
                
                cout << " " << (sat ? "SAT" : "UNSAT") 
                     << " | " << fixed << setprecision(2) << duration << "s"
                     << " | Noeuds: " << MOMSSolver::getNodesExplored() << endl;
            } catch (const runtime_error&) {
                cout << " TIMEOUT (30s)" << endl;
            }
            
            // CDCL
            cout << "[3/3] CDCL...";
            cout.flush();
            try {
                TimeoutManager tm(TIMEOUT_CDCL);
                FastCDCLSolver solver(clauses, numVars);
                auto start = high_resolution_clock::now();
                auto [sat, sol] = solver.solve(&tm);
                auto duration = duration_cast<milliseconds>(high_resolution_clock::now() - start).count() / 1000.0;
                
                cout << " " << (sat ? "SAT" : "UNSAT") 
                     << " | " << fixed << setprecision(2) << duration << "s"
                     << " | Noeuds: " << FastCDCLSolver::getNodesExplored() << endl;
                
                if (sat) {
                    saveSolutionToFile(sol, numVars, filename, duration, FastCDCLSolver::getNodesExplored());
                    cout << "   Solution sauvegardee: " << filename << ".sol" << endl;
                }
                
            } catch (const runtime_error&) {
                cout << " TIMEOUT (1800s)" << endl;
            }
            
        } catch (const exception& e) {
            cout << "Erreur: " << e.what() << endl;
        }
    }
    
    cout << "\n" << string(80, '=') << endl;
    cout << "Tests termines!" << endl;
    cout << string(80, '=') << endl;
    
    return 0;
}