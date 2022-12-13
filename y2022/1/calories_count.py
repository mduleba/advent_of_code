

with open('input.txt') as file:
    top_3 = [0, 0, 0]
    current_backpack = 0
    for line in file.readlines():
        if line == '\n':
            if current_backpack > min(top_3):
                top_3.sort(reverse=True)
                top_3.pop()
                top_3.append(current_backpack)
            current_backpack = 0
        else:
            current_backpack += int(line)

        print(sum(top_3))
