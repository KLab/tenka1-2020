#include <iostream>
#include <fstream>
#include <vector>
using namespace std;

const int di[] = {+1,-1, 0, 0};
const int dj[] = { 0, 0,+1,-1};

struct CalcScore {
	const int N;
	vector<vector<double>> b;
	CalcScore(int N, const vector<vector<double>>& b) : N(N), b(b) {}

	pair<int, double> f(int i, int j) {
		if (b[i][j] <= 0) return {0, 1e+300};
		int n = 1;
		double m = b[i][j];
		b[i][j] = 0;
		for (int k = 0; k < 4; ++ k) {
			int ii = i + di[k];
			int jj = j + dj[k];
			if (0 <= ii && ii < N && 0 <= jj && jj < N) {
				auto r = f(ii, jj);
				n += r.first;
				m = min(m, r.second);
			}
		}
		return {n, m};
	}

	double calc() {
		double score = 0;
		for (int i = 0; i < N; ++ i) for (int j = 0; j < N; ++ j) if (b[i][j] > 0) {
			auto r = f(i, j);
			score += r.first * r.second;
		}
		return score;
	}
};

int main(int argc, char** argv) {
	int N;
	ifstream fin(argv[1]);
	fin >> N;
	vector<vector<double>> A(N, vector<double>(N));
	for (int i = 0; i < N; ++ i) for (int j = 0; j < N; ++ j) fin >> A[i][j];

	int n;
	while (cin >> n) {
		vector<vector<double>> b(N, vector<double>(N));
		for (int k = 0; k < n; ++ k) {
			int idx;
			double cnt;
			cin >> idx >> cnt;
			int i = idx / N, j = idx % N;
			b[i][j] = A[i][j] / cnt;
		}
		printf("%.15f\n", CalcScore(N, b).calc());
		fflush(stdout);
	}
}
