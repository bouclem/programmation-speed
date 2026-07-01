arr = list(range(100, 0, -1))
for i in range(99):
    for j in range(99 - i):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
print(arr[50])
