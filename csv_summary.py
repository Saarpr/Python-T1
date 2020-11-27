import csv
import json

class Summary:
    c_file = None
    j_file = None
    group_by = None
    def __init__(self,  csv_file ,json_file ):
        self.c_file = csv_file
        self.j_file = json_file
        with open(json_file) as jsonfile:
            data = json.load(jsonfile)
            self.group_by = data["groupby"]

    def getGroups(self):
        """
        method which will return a list of all groups created.
        """
        groups_names = set()
        groups_list = list()
        with open(self.c_file,'r')as file:
            csv_dict = csv.DictReader(file)
            for row in csv_dict:
                groups_names.add(dict(row)[self.group_by])
            for i in groups_names:
                tmp_data =[]
                with open(self.c_file, 'r')as file:
                    csv_dict = csv.DictReader(file)
                    for row in csv_dict:
                        if(i==row[self.group_by]):
                            tmp_data.append(dict(row))
                    tmp_group = Group(i,tmp_data,self.getSpec())
                    groups_list.append(tmp_group)
                    tmp_group.print_sum()

        for i in groups_list:
            i.print_sum()


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
                if(list(feature.values())[0]["type"]=="categorical" or list(feature.values())[0]["type"]=="numerical"):
                    tmp_dict[list(feature.keys())[0]]=list(feature.values())[0]["aggregate"]
        return tmp_dict

class Group:
    name = None
    finalSummary = {}
    data = None
    agg = None

    def __str__(self):
        tmp = "{} - ".format(self.name)
        # print(self.name , self.finalSummary)
        # for k,v in self.finalSummary:
        #     tmp +="{}({}):{}, ".format(k,v,self.finalSummary[k])
        return tmp
    def __init__(self,name,data,aggList):
        self.name=name
        self.data=data
        self.agg=aggList
        for k,v in aggList.items():
            if(v=="mode"):
                self.finalSummary[k]=self.mode(k)
            elif (v=="union"):
                self.finalSummary[k]=self.union(k)
            elif (v=="unique"):
                self.finalSummary[k]=self.unique(k)
            elif (v=="count"):
                self.finalSummary[k]=self.count(k)
            elif (v=="min"):
                self.finalSummary[k]=self.min(k)
            elif (v=="max"):
                self.finalSummary[k]=self.max(k)
            elif (v=="median"):
                self.finalSummary[k]=self.median(k)
            elif (v=="mean"):
                self.finalSummary[k]=self.mean(k)
            elif (v=="sum"):
                self.finalSummary[k]=self.sum(k)



    def print_sum(self):
        print(self.name , self.finalSummary)
    def mode (self,feature):
        count = list()
        for line in self.data:
            count.append(line[feature])
        return max(set(count), key = count.count)

    def union (self,feature):
        union = set()
        for line in self.data:
            union.add(line[feature])
        return ";".join(union)


    def unique (self,feature):
        unique = set()
        for line in self.data:
            unique.add(line[feature])
        return len(unique)

    def count (self,feature):
        x = 0
        for line in self.data:
            if(line[feature]):
                x += 1
        return x

    def min (self,feature):
        mini = list()
        for line in self.data:
            mini.append(int(line[feature]))
        return min(mini)

    def max (self,feature):
        maxi = list()
        for line in self.data:
            maxi.append(int(line[feature]))
        return max(maxi)

    def median (self,feature):
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

    def mean (self,feature):
        n_num = []
        for line in self.data:
            n_num.append(int(line[feature]))
        n = len(n_num)
        get_sum = sum(n_num)
        mean = get_sum / n

        return str(format(mean,".2f"))

    def sum (self,feature):
        x = 0
        for line in self.data:
            if(line[feature]):
                x += int(line[feature])
        return x
if __name__ == "__main__":
    js = "features.json"
    cs = "Example.csv"
    S = Summary(cs,js)
    S.getGroups()
    print("test!")
    # for i in S.getGroups():
    #     print (str(i))

