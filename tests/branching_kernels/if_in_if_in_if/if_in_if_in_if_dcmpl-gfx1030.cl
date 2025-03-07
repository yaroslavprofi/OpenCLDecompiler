__kernel __attribute__((reqd_work_group_size(64, 1, 1)))
void if_in_if_in_if(uint nEdges, __global uint *edges_x, __global uint *edges_y, uint some_const, __global double *weights, __global double *d, __global uint *changed)
{
    uint var0;
    double var1;
    uint var2;
    double var3;
    double var4;
    if ((uint)nEdges > (uint)get_global_id(0)) {
        var0 = edges_x[get_global_id(0)];
        var1 = d[var0];
        if ((double)var1 < (double)some_const) {
            var2 = edges_y[get_global_id(0)];
            var3 = weights[get_global_id(0)];
            var4 = d[var2];
            if ((uint)var4 > (uint)((double)var1 + (double)var3)) {
                d[var2] = (double)var1 + (double)var3;
                *changed = 1;
            }
        }
    }
}
