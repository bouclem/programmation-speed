const std = @import("std");

pub fn main() void {
    var arr: [100]u32 = undefined;
    var i: u32 = 0;
    while (i < 100) : (i += 1) {
        arr[i] = 100 - i;
    }
    i = 0;
    while (i < 99) : (i += 1) {
        var j: u32 = 0;
        while (j < 99 - i) : (j += 1) {
            if (arr[j] > arr[j + 1]) {
                const tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
    std.debug.print("{}\n", .{arr[50]});
}
