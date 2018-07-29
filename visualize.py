import matplotlib.pyplot as plt
import csv

traffic = list()
date = list()
with open("traffics.csv", "r") as f:
    for x in csv.reader(f, delimiter=','):
        traffic.append(float(x[2]))
        date.append(x[-1])

plt.plot(date, traffic)
plt.xlabel("date")
plt.ylabel("traffic [GB]")
plt.show()
