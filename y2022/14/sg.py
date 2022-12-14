class Material:
    AIR = 0
    ROCK = 1
    SAND = 2


with open("input.txt") as file:
    points = {}
    lowest_rock = 0
    for line in file:
        end_points = [tuple(map(int, point.split(","))) for point in line.split("->")]
        for i in range(len(end_points) - 1):
            x1, y1, x2, y2 = *end_points[i], *end_points[i + 1]
            lowest_rock = max(y1, y2, lowest_rock)
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    points[x, y] = Material.ROCK

amount = 0
part1 = 0
floor = lowest_rock + 2
sand = None
while sand != (500, 0):
    sand = 500, 0
    while True:
        y = sand[1] + 1
        for dx in 0, -1, 1:
            x = sand[0] + dx
            if y < floor and points.get((x, y), Material.AIR) == Material.AIR:
                sand = x, y
                break
        else:
            if not part1 and sand[1] > lowest_rock:
                part1 = amount
            points[sand] = Material.SAND
            break
    amount += 1

print(part1)
print(amount)