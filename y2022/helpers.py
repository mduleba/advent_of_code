def load_file(file_name: str = 'input.txt'):
    lines = []
    with open(file_name) as file:
        for line in file.readlines():
            clean_line = line.rstrip('\n')
            lines.append(clean_line)
    return lines