from Subject import Subject


class NCCD:
    def __init__(self, filename):
        self.dict = {}
        self.subjects = []
        self.parse_nccd_file(filename)

    def parse_nccd_file(self, filename):
        file = open(filename, 'r')
        lst = list(file.readlines())
        for line in lst[0: len(lst) - 1]:
            row = line.strip().split(" : ")
            id = 's' + row[0]
            subject = Subject(id)
            self.subjects.append(subject)
            self.dict[id] = ['s' + value for value in row[1].split(' -> ')[0].split()]
