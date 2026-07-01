let arr = [];
for (let i = 0; i < 100; i++) {
    arr[i] = 100 - i;
}
for (let i = 0; i < 99; i++) {
    for (let j = 0; j < 99 - i; j++) {
        if (arr[j] > arr[j + 1]) {
            let tmp = arr[j];
            arr[j] = arr[j + 1];
            arr[j + 1] = tmp;
        }
    }
}
console.log(arr[50]);
