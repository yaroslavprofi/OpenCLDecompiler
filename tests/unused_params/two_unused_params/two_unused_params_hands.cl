__kernel void two_unused_params(int n, int w, int z, __global int *data, __global int *data1, int x, int y)
{
    int var3;
    if ((int)n > (int)get_global_id(0)) {
        data[get_global_id(0)] = x;
    }
    else {
        var3 = data1[get_global_id(1)];
        data[get_global_id(1)] = (ulong)y + (ulong)var3;
    }
}
