const std = @import("std");

pub fn main() void {
    var count: u32 = 0;
    var i: u32 = 0;
    while (i < 10) : (i += 1) {
        var j: u32 = 0;
        while (j < 10) : (j += 1) {
            var k: u32 = 0;
            while (k < 10) : (k += 1) {
                count += 1;
            }
        }
    }
    std.debug.print("{}\n", .{count});
}
