import csv
import json


class Summary:
    c_file = None
    j_file = None
    group_by = None
    groups_list = None

    def __init__(self, csv_file, json_file):
        self.c_file = csv_file
        self.j_file = json_file
        self.groups_list = list()
        with open(json_file) as jsonfile:
            data = json.load(jsonfile)
            self.group_by = data["groupby"]
        self.getGroups()

    def __iter__(self):
        return iter(self.groups_list)

    def __getitem__(self, item):
        for i in self.groups_list:
            if (i.name == item):
                return i
    def __str__(self):
        tmp = ""
        for i in self.groups_list:
            tmp += str(i) + '\n'
        return tmp


    def getGroups(self):
        """
        method which will return a list of all groups created.
        """
        groups_names = set()
        with open(self.c_file, 'r')as file:
            csv_dict = csv.DictReader(file)
            for row in csv_dict:
                groups_names.add(dict(row)[self.group_by])
            groups_names = sorted(groups_names)
            for i in groups_names:
                tmp_data = []
                with open(self.c_file, 'r')as file:
                    csv_dict = csv.DictReader(file)
                    for row in csv_dict:
                        if (i == row[self.group_by]):
                            tmp_data.append(dict(row))
                    self.groups_list.append(Group(i, tmp_data, self.getSpec()))
                    # print(self.getSpec())
            # for i in self.groups_list:
            #     print(i)

    def getSpec(self):
        '''
        :return:a dictionary with the following format:
        {feature1:aggregate1, feature2:aggregate2, …, featureN:aggregateN}
        '''
        tmp_dict = dict()
        with open(self.j_file) as jsonfile:
            data = json.load(jsonfile)
            # print(data["features"])
            for feature in data["features"]:
                if (list(feature.values())[0]["type"] == "categorical" or list(feature.values())[0][
                    "type"] == "numerical"):
                    tmp_dict[list(feature.keys())[0]] = list(feature.values())[0]["aggregate"]
        return tmp_dict

    def saveSummary(self, filename, deli=','):
        featureStr = self.group_by + "(groupby)"
        firstLine = list()
        firstLine.append(featureStr)
        for k, v in self.getSpec().items():
            tmp = "{}({})".format(k, v)
            firstLine.append(tmp)
        allValues = list()
        allValues.append(firstLine)
        for i in self.groups_list:
            groupValues = [i.name]
            for key, val in i:
                groupValues.append(val)
            allValues.append(groupValues)
        # for ls in allValues:
        #     for v in ls:
        #         print(v , end = ",")
        #     print("\n")
        # print(firstLine)
        if ('a' <= deli <= 'z') or ('A' <= deli <= 'Z') or ('0' <= deli <= '9') or deli == "'" or deli == '"':
            deli = ','
        csvFilename = filename + ".csv"
        file = open(csvFilename, 'w', newline='')
        with file:
            write = csv.writer(file, delimiter=deli)
            write.writerows(allValues)


class Group:
    name = None
    finalSummary = None
    data = None
    agg = None

    def __str__(self):
        tmp = "{} - ".format(self.name)
        for k, v in self.finalSummary.items():
            tmp += "{}({}):{}, ".format(k, self.agg[k], self.finalSummary[k])
        tmp = tmp[:-2]
        return tmp

    def __init__(self, name, data, aggList):
        self.name = name
        self.data = data
        self.agg = aggList
        self.finalSummary = {}
        for k, v in aggList.items():
            if (v == "mode"):
                self.finalSummary[k] = self.mode(k)
            elif (v == "union"):
                self.finalSummary[k] = self.union(k)
            elif (v == "unique"):
                self.finalSummary[k] = self.unique(k)
            elif (v == "count"):
                self.finalSummary[k] = self.count(k)
            elif (v == "min"):
                self.finalSummary[k] = self.min(k)
            elif (v == "max"):
                self.finalSummary[k] = self.max(k)
            elif (v == "median"):
                self.finalSummary[k] = self.median(k)
            elif (v == "mean"):
                self.finalSummary[k] = self.mean(k)
            elif (v == "sum"):
                self.finalSummary[k] = self.sum(k)

    def __iter__(self):
        return iter(self.finalSummary.items())

    def __getitem__(self, item):
        ls = list(self.finalSummary)
        ls.sort()
        for k, v in self.finalSummary.items():
            if (type(item) == str and k == item):
                return v
            elif (type(item) == int):
                return ls[item]

    def print_sum(self):
        print(self.name, self.finalSummary)

    def mode(self, feature):
        count = list()
        for line in self.data:
            count.append(line[feature])
        return max(set(count), key=count.count)

    def union(self, feature):
        union = set()
        for line in self.data:
            union.add(line[feature])
        return ";".join(union)

    def unique(self, feature):
        unique = set()
        for line in self.data:
            unique.add(line[feature])
        return len(unique)

    def count(self, feature):
        x = 0
        for line in self.data:
            if (line[feature]):
                x += 1
        return x

    def min(self, feature):
        mini = list()
        for line in self.data:
            mini.append(int(line[feature]))
        return min(mini)

    def max(self, feature):
        maxi = list()
        for line in self.data:
            maxi.append(int(line[feature]))
        return max(maxi)

    def median(self, feature):
        n_num = []
        for line in self.data:
            n_num.append(int(line[feature]))
        n = len(n_num)
        n_num.sort()

        if n % 2 == 0:
            median1 = n_num[n // 2]
            median2 = n_num[n // 2 - 1]
            median = (median1 + median2) / 2
        else:
            median = n_num[n // 2]
        return (str(median))

    def mean(self, feature):
        n_num = []
        for line in self.data:
            n_num.append(int(line[feature]))
        n = len(n_num)
        get_sum = sum(n_num)
        mean = get_sum / n
        return str(format(mean, ".2f"))

    def sum(self, feature):
        x = 0
        for line in self.data:
            if (line[feature]):
                x += int(line[feature])
        return x


if __name__ == "__main__":
    js = "features.json"
    cs = "Example.csv"
    S = Summary(cs, js)
    print(S)
    # S.getGroups()
    # print(S.group_by)
    # print(S.getSpec())
    # S.saveSummary()
    # for i in S.groups_list:
    #     print(i)
    # S.saveSummary("s", '6')
    # iterator = iter(S["Blue"])
    # print(iterator)
    # print(next(iterator))
    # print(next(iterator))
    # print(next(iterator))
    # print(S["Blue"]["Model"])
    # print(S["Blue"])
    # for i in S.getGroups():
    #     print (str(i))
