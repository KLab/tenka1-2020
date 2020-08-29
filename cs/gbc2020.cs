using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Threading.Tasks;

public class Program
{
    string GAME_SERVER;
    string TOKEN;
    static readonly Random random = new Random();

    async Task Solve()
    {
        GAME_SERVER = Environment.GetEnvironmentVariable("GAME_SERVER") ?? "https://contest.gbc-2020.tenka1.klab.jp";
        TOKEN = Environment.GetEnvironmentVariable("TOKEN") ?? "YOUR_TOKEN";

        while (true)
        {
            var game_resp = (await CallAPI("/api/game")).Split('\n');
            var game_id = int.Parse(game_resp[0]);
            var remaining_ms = int.Parse(game_resp[1]);

            if (game_id < 0)
            {
                break;
            }

            var stage_resp = (await CallAPI($"/api/stage/{game_id}")).Split('\n');
            Assert(stage_resp[0] == "20");
            var stage = stage_resp.Skip(1).Take(20).Select(x => x.Split(' ').Select(int.Parse).ToArray()).ToArray();

            while(true)
            {
                var areas_resp = (await CallAPI($"/api/areas/{TOKEN}/{game_id}")).Split('\n');
                if (areas_resp[0] == "too_many_request")
                {
                    await Task.Delay(500);
                    continue;
                }

                Assert(areas_resp[0] == "ok");
                var num_claim = areas_resp.Skip(1).Take(20).Select(x => x.Split(' ').Select(int.Parse).ToArray()).ToArray();
                var my_claim = areas_resp.Skip(21).Take(20).Select(x => x.Split(' ').Select(int.Parse).ToArray()).ToArray();

                var score = CalcScore(stage, num_claim, my_claim);
                Console.WriteLine($"game_id: {game_id}  score: {score}");

                var candidate = new List<(int, int)>();
                for (var i = 0; i < 20; i++)
                {
                    for (var j = 0; j < 20; j++)
                    {
                        if (my_claim[i][j] == 0)
                        {
                            candidate.Add((i, j));
                        }
                    }
                }

                Assert(candidate.Count > 0);

                var (r, c) = candidate[random.Next(candidate.Count)];

                var claim_resp = (await CallAPI($"/api/claim/{TOKEN}/{game_id}/{r}-{c}-1")).Split('\n')[0];
                if (claim_resp == "game_finished")
                {
                    break;
                }

                Assert(claim_resp == "ok");
            }

            while (int.Parse((await CallAPI("/api/game")).Split('\n')[0]) == game_id)
            {
                await Task.Delay(500);
            }
        }
    }

    void Assert(bool x)
    {
        if (!x)
        {
            throw new Exception();
        }
    }

    async Task<string> CallAPI(string x)
    {
        var client = WebRequest.Create($"{GAME_SERVER}{x}");
        using (var response = await client.GetResponseAsync())
        using (var reader = new StreamReader(response.GetResponseStream()))
        {
            return reader.ReadToEnd();
        }
    }

    double CalcScore(int[][] stage, int[][] num_claim, int[][] my_claim)
    {
        var visited = new bool[20, 20];

        (double, int) f(int r, int c)
        {
            if (r < 0 || r >= 20 || c < 0 || c >= 20 || my_claim[r][c] == 0 || visited[r, c])
            {
                return (1e+300, 0);
            }

            visited[r, c] = true;

            double r1 = (double)stage[r][c] / num_claim[r][c];
            int r2 = 1;
            foreach (var (r3, r4) in new (double, int)[] { f(r + 1, c), f(r - 1, c), f(r, c + 1), f(r, c - 1) })
            {
                r1 = Math.Min(r1, r3);
                r2 += r4;
            }

            return (r1, r2);
        }

        var score = 0.0;
        for (var i = 0; i < 20; i++)
        {
            for (var j = 0; j < 20; j++)
            {
                var (x, y) = f(i, j);
                score += x * y;
            }
        }

        return score;
    }

    public static void Main(string[] args)
    {
        new Program().Solve().Wait();
    }
}
