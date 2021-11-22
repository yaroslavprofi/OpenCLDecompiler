from src.base_instruction import BaseInstruction
from src.decompiler_data import make_op, make_new_value_for_reg


class SSub(BaseInstruction):
    def __init__(self, node, suffix):
        super().__init__(node, suffix)
        self.sdst = self.instruction[1]
        self.ssrc0 = self.instruction[2]
        self.ssrc1 = self.instruction[3]

    def to_print_unresolved(self):
        temp = "temp" + str(self.decompiler_data.number_of_temp)
        if self.suffix == 'i32':
            self.decompiler_data.write(self.sdst + " = " + self.ssrc0 + " - " + self.ssrc1 + " // s_sub_i32\n")
            self.decompiler_data.write("long " + temp + " = (long)" + self.ssrc0 + " - (long)" + self.ssrc1 + "\n")
            self.decompiler_data.write("scc = " + temp + " > ((1LL << 31) - 1) || " + temp + " < (-1LL << 31)\n")
            self.decompiler_data.number_of_temp += 1
            return self.node
        elif self.suffix == 'u32':
            self.decompiler_data.write("ulong " + temp + " = (ulong)" + self.ssrc0
                                       + " - (ulong)" + self.ssrc1 + " // s_sub_u32\n")
            self.decompiler_data.write(self.sdst + " = " + temp + "\n")
            self.decompiler_data.write("scc = (" + temp + ">>32)!=0\n")
            self.decompiler_data.number_of_temp += 1
            return self.node
        else:
            return super().to_print_unresolved()

    def to_fill_node(self):
        if self.suffix == 'u32':
            new_value, src0_reg, src1_reg = make_op(self.node, self.ssrc0, self.ssrc1, " - ", '(ulong)', '(ulong)')
            reg_entire = self.node.state.registers[self.ssrc1].integrity
            return make_new_value_for_reg(self.node, new_value, self.sdst, [self.ssrc0, self.ssrc1],
                                          self.suffix, reg_entire=reg_entire)
        else:
            return super().to_fill_node()
