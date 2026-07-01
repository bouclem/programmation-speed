#include <stdio.h>

int main() {
    int arr[100];
    for (int i = 0; i < 100; i++) {
        arr[i] = 100 - i;
    }
    for (int i = 0; i < 99; i++) {
        for (int j = 0; j < 99 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                int tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
    printf("%d\n", arr[50]);
    return 0;
}
