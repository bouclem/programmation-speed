fn main() {
    let mut count = 0;
    for _ in 0..10 {
        for _ in 0..10 {
            for _ in 0..10 {
                count += 1;
            }
        }
    }
    println!("{}", count);
}
