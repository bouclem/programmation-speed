const std = @import("std");

fn isPrime(n: u32) bool {
    if (n < 2) return false;
    var i: u32 = 2;
    while (i * i <= n) : (i += 1) {
        if (n % i == 0) return false;
    }
    return true;
}

pub fn main() void {
    var count: u32 = 0;
    var i: u32 = 2;
    while (i <= 10000) : (i += 1) {
        if (isPrime(i)) count += 1;
    }
    std.debug.print("{}\n", .{count});
}
