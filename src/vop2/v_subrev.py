from src.base_instruction import BaseInstruction
from src.decompiler_data import make_op, make_new_value_for_reg


class VSubrev(BaseInstruction):
    def __init__(self, node, suffix):
        super().__init__(node, suffix)
        self.vdst = self.instruction[1]
        self.vcc = self.instruction[2]
        self.src0 = self.instruction[3]
        self.src1 = self.instruction[4]

    def to_print_unresolved(self):
        if self.suffix == 'u32':
            temp = "temp" + str(self.decompiler_data.number_of_temp)
            mask = "mask" + str(self.decompiler_data.number_of_mask)
            self.decompiler_data.write("ulong " + temp + " = (ulong)" + self.src1
                                       + " - (ulong)" + self.src0 + " // v_subrev_u32\n")
            self.decompiler_data.write(self.vdst + " = CLAMP ? (" + temp + ">>32 ? 0 : " + temp + ") : " + temp + "\n")
            self.decompiler_data.write(self.vcc + " = 0\n")  # vop2, sdst
            self.decompiler_data.write("ulong " + mask + " = (1ULL<<LANEID)\n")
            self.decompiler_data.write(self.vcc + " = (" + self.vcc + "&~" + mask + ") | (("
                                       + temp + ">>32) ? " + mask + " : 0)\n")
            self.decompiler_data.number_of_temp += 1
            self.decompiler_data.number_of_mask += 1
            return self.node
        else:
            return super().to_print_unresolved()

    def to_fill_node(self):
        if self.suffix == 'u32':
            new_value, src0_reg, src1_reg = make_op(self.node, self.src1, self.src0, " - ", '(ulong)', '(ulong)')
            reg_entire = self.node.state.registers[self.src1].integrity
            return make_new_value_for_reg(self.node, new_value, self.vdst, [self.src0, self.src1],
                                          self.suffix, reg_entire=reg_entire)
        else:
            return super().to_fill_node()
