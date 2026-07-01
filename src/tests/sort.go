package main

import "fmt"

func main() {
	arr := make([]int, 100)
	for i := 0; i < 100; i++ {
		arr[i] = 100 - i
	}
	for i := 0; i < 99; i++ {
		for j := 0; j < 99-i; j++ {
			if arr[j] > arr[j+1] {
				arr[j], arr[j+1] = arr[j+1], arr[j]
			}
		}
	}
	fmt.Println(arr[50])
}
