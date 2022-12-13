from random import shuffle
from collections import deque


def solve(n, m, grid, i_s, j_s, i_f, j_f, part):
    visited = [[False] * (m + 2) for _ in range(n + 2)]
    dist = [[-1] * (m + 2) for _ in range(n + 2)]
    stack = deque()
    stack.append((i_s, j_s))
    dist[i_s][j_s] = 0
    visited[i_s][j_s] = True
    parents = {}
    while stack:
        i, j = stack.popleft()

        if part == 2:
            if contents_pad[i][j] == "a":
                break
        else:
            if (i, j) == (i_f, j_f):
                break
        neighbs = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]

        for i_n, j_n in neighbs:
            if visited[i_n][j_n] or (ord(contents_pad[i_n][j_n]) - ord(contents_pad[i][j])) < -1:
                continue
            stack.append((i_n, j_n))
            visited[i_n][j_n] = True
            parents[(i_n, j_n)] = (i, j)
            dist[i_n][j_n] = dist[i][j] + 1
    path = []
    node = (i, j)
    while node != (i_s, j_s):
        path.append(parents[node])
        node = parents[node]

    return path


inputfile = "input.txt"

with open(inputfile) as myfile:
    contents = list(map(lambda x: x.strip(), myfile.readlines()))
n, m = len(contents), len(contents[0])
contents_pad = ['#' * (m + 2)]
for i in range(n):
    contents_pad.append('#' + contents[i] + '#')
contents_pad.append('#' * (m + 2))
for i in range(n + 2):
    for j in range(m + 2):
        if contents_pad[i][j] == "S":
            i_f, j_f = i, j
            contents_pad[i] = contents_pad[i].replace("S", "a")
        if contents_pad[i][j] == "E":
            i_s, j_s = i, j
            contents_pad[i] = contents_pad[i].replace("E", "z")

path1 = solve(n, m, contents_pad, i_s, j_s, i_f, j_f, 1)
path2 = solve(n, m, contents_pad, i_s, j_s, i_f, j_f, 2)
paths = [path1, path2]

with open("map.txt", "w") as inputmap:
    for i in range(1, len(contents_pad) - 1):
        inputmap.write(" ".join(list(map(lambda x: str(ord(x) - ord("a")), list(contents_pad[i])[1:-1]))) + "\n")
k = 1
for path in paths:
    with open(f"path{k}.txt", "w") as pathfile:
        for i, j in path[::-1]:
            pathfile.write(f"{i} {j}\n")
    k += 1