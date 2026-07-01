package main

import "fmt"

func isPrime(n int) bool {
	if n < 2 {
		return false
	}
	for i := 2; i*i <= n; i++ {
		if n%i == 0 {
			return false
		}
	}
	return true
}

func main() {
	count := 0
	for i := 2; i <= 10000; i++ {
		if isPrime(i) {
			count++
		}
	}
	fmt.Println(count)
}
