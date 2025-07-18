#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <fstream>
#include <string>
#include <sstream>

using namespace std;

// ---------- RAG Deadlock Detection ----------
unordered_map<string, vector<string>> graph;
unordered_set<string> visited;
unordered_set<string> recursionStack;

bool isCyclic(string node) {
    if (recursionStack.count(node))
        return true;
    if (visited.count(node))
        return false;

    visited.insert(node);
    recursionStack.insert(node);

    for (const string& neighbor : graph[node]) {
        if (isCyclic(neighbor))
            return true;
    }

    recursionStack.erase(node);
    return false;
}

void run_rag() {
    int edge_count;
    ifstream infile("graph.txt");
    if (!infile) {
        cerr << "Error opening graph.txt\n";
        return;
    }

    infile >> edge_count;
    infile.ignore();

    for (int i = 0; i < edge_count; ++i) {
        string from, to;
        infile >> from >> to;
        graph[from].push_back(to);
    }

    for (const auto& pair : graph) {
        if (!visited.count(pair.first)) {
            if (isCyclic(pair.first)) {
                cout << "Deadlock Detected\n";
                return;
            }
        }
    }

    cout << "No Deadlock Detected\n";
}

// ---------- Banker's Algorithm ----------
void run_banker() {
    ifstream infile("banker_input.txt");
    if (!infile) {
        cerr << "Error opening banker_input.txt\n";
        return;
    }

    int n, m;
    infile >> n >> m;

    vector<vector<int>> alloc(n, vector<int>(m));
    vector<vector<int>> max(n, vector<int>(m));
    vector<int> avail(m);

    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            infile >> alloc[i][j];

    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            infile >> max[i][j];

    for (int i = 0; i < m; i++)
        infile >> avail[i];

    vector<vector<int>> need(n, vector<int>(m));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            need[i][j] = max[i][j] - alloc[i][j];

    vector<bool> finish(n, false);
    vector<int> safeSequence;

    int count = 0;
    while (count < n) {
        bool found = false;
        for (int i = 0; i < n; i++) {
            if (!finish[i]) {
                bool possible = true;
                for (int j = 0; j < m; j++) {
                    if (need[i][j] > avail[j]) {
                        possible = false;
                        break;
                    }
                }

                if (possible) {
                    for (int j = 0; j < m; j++)
                        avail[j] += alloc[i][j];
                    safeSequence.push_back(i);
                    finish[i] = true;
                    found = true;
                    count++;
                }
            }
        }

        if (!found) {
            cout << "System is in Deadlock\n";
            return;
        }
    }

    cout << "System is in Safe State\nSafe Sequence: ";
    for (int i : safeSequence)
        cout << "P" << i << " ";
    cout << "\n";
}

int main() {
    ifstream modeFile("mode.txt");
    if (!modeFile) {
        cerr << "Error: Could not open mode.txt\n";
        return 1;
    }

    string mode;
    getline(modeFile, mode);

    if (mode == "banker") {
        run_banker();
    } else if (mode == "rag") {
        run_rag();
    } else {
        cerr << "Unknown mode in mode.txt. Use 'banker' or 'rag'.\n";
        return 1;
    }

    return 0;
}
