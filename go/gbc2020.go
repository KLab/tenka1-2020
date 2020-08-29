package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

var GameServer string
var TOKEN string

func assert(x bool) {
	if !x {
		panic("assert")
	}
}

func callApi(x string) string {
	resp, err := http.Get(GameServer + x)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()
	data, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatal(err)
	}
	return string(data)
}

func atoi(s string) int {
	r, err := strconv.Atoi(s)
	if err != nil {
		log.Fatal(err)
	}
	return r
}

func convert(a []string) [][]int {
	r := make([][]int, 0, 20)
	for _, s := range a {
		rr := make([]int, 0, 20)
		for _, ss := range strings.Split(s, " ") {
			rr = append(rr, atoi(ss))
		}
		r = append(r, rr)
	}
	return r
}

type CalcScore struct {
	Stage    [][]int
	NumClaim [][]int
	MyClaim  [][]int
	Visited  [][]bool
}

type CalcScoreResult struct {
	R1 float64
	R2 int
}

func (s *CalcScore) f(r, c int) *CalcScoreResult {
	if r < 0 || r >= 20 || c < 0 || c >= 20 || s.MyClaim[r][c] == 0 || s.Visited[r][c] {
		return &CalcScoreResult{1e+300, 0}
	}

	s.Visited[r][c] = true

	r1 := float64(s.Stage[r][c]) / float64(s.NumClaim[r][c])
	r2 := 1
	for _, x := range []*CalcScoreResult{s.f(r+1, c), s.f(r-1, c), s.f(r, c+1), s.f(r, c-1)} {
		r1 = math.Min(r1, x.R1)
		r2 += x.R2
	}
	return &CalcScoreResult{r1, r2}
}

func calcScore(stage [][]int, numClaim [][]int, myClaim [][]int) float64 {
	visited := make([][]bool, 20)
	for i := 0; i < 20; i++ {
		visited[i] = make([]bool, 20)
	}
	c := &CalcScore{Stage: stage, NumClaim: numClaim, MyClaim: myClaim, Visited: visited}
	score := 0.0
	for i := 0; i < 20; i++ {
		for j := 0; j < 20; j++ {
			x := c.f(i, j)
			score += x.R1 * float64(x.R2)
		}
	}
	return score
}

func main() {
	GameServer = os.Getenv("GAME_SERVER")
	TOKEN = os.Getenv("TOKEN")
	if GameServer == "" {
		GameServer = "https://contest.gbc-2020.tenka1.klab.jp"
	}
	if TOKEN == "" {
		TOKEN = "YOUR_TOKEN"
	}

	for {
		gameResp := strings.Split(callApi("/api/game"), "\n")
		gameId := atoi(gameResp[0])

		if gameId < 0 {
			break
		}

		stageResp := strings.Split(callApi(fmt.Sprintf("/api/stage/%d", gameId)), "\n")
		assert(stageResp[0] == "20")
		stage := convert(stageResp[1:21])

		for {
			areasResp := strings.Split(callApi(fmt.Sprintf("/api/areas/%s/%d", TOKEN, gameId)), "\n")
			if areasResp[0] == "too_many_request" {
				time.Sleep(500 * time.Millisecond)
				continue
			}
			assert(areasResp[0] == "ok")
			numClaim := convert(areasResp[1:21])
			myClaim := convert(areasResp[21:41])

			score := calcScore(stage, numClaim, myClaim)
			fmt.Printf("game_id: %d  score: %f\n", gameId, score)

			candidate := make([]string, 0)
			for i := 0; i < 20; i++ {
				for j := 0; j < 20; j++ {
					if myClaim[i][j] == 0 {
						candidate = append(candidate, fmt.Sprintf("%d-%d", i, j))
					}
				}
			}

			assert(len(candidate) > 0)
			rc := candidate[rand.Intn(len(candidate))]

			var claimResp = strings.Split(callApi(fmt.Sprintf("/api/claim/%s/%d/%s-1", TOKEN, gameId, rc)), "\n")[0]
			if claimResp == "game_finished" {
				break
			}
			assert(claimResp == "ok")
		}

		for atoi(strings.Split(callApi("/api/game"), "\n")[0]) == gameId {
			time.Sleep(500 * time.Millisecond)
		}
	}
}
