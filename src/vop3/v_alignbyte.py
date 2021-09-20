from src.base_instruction import BaseInstruction
from src.decompiler_data import DecompilerData, check_reg_for_val, make_new_value_for_reg
from src.operation_status import OperationStatus


class VAlignbyte(BaseInstruction):
    def execute(self, node, instruction, flag_of_status, suffix):
        decompiler_data = DecompilerData()
        output_string = ''
        vdst = instruction[1]
        src0 = instruction[2]
        src1 = instruction[3]
        src2 = instruction[4]

        if suffix == "b32":
            if flag_of_status == OperationStatus.to_print_unresolved:
                decompiler_data.write(vdst + " = (((ulong)" + src0 + ") << 32) | " + src1
                                      + ") >> ((" + src2 + " & 3) * 8) // v_alignbyte_b32\n")
                return node
            if flag_of_status == OperationStatus.to_fill_node:
                src0, _ = check_reg_for_val(node, src0)
                src1, _ = check_reg_for_val(node, src1)
                src2, _ = check_reg_for_val(node, src2)
                new_value = 'amd_bytealign(' + src0 + ', ' + src1 + ', ' + src2 + ')'
                return make_new_value_for_reg(node, new_value, vdst, [src0, src1, src2], suffix)
            if flag_of_status == OperationStatus.to_print:
                return output_string
