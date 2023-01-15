__kernel __attribute__((reqd_work_group_size(64, 1, 1)))
void short_char_test(short y, char x, __global uint *data0, __global uint *data1)
{
    uint id = get_global_id(0);
    data0[id] = x;
    data1[id] = y;
}
