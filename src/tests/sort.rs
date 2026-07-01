fn main() {
    let mut arr: [u32; 100] = [0; 100];
    for i in 0..100 {
        arr[i] = (100 - i) as u32;
    }
    for i in 0..99 {
        for j in 0..(99 - i) {
            if arr[j] > arr[j + 1] {
                let tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
    println!("{}", arr[50]);
}
