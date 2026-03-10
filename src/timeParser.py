def loadFile (filePath: str) -> dict[str, int]:
    categoryHours = {}
    with open(filePath, 'r') as file:
        for line in file:
            input = line.strip()
            if not input:
                continue

            category, hours = input.split()
            hours = int(hours)
            
            categoryHours[category] = categoryHours.get(category, 0) + hours

    return categoryHours
