from src.base_instruction import BaseInstruction
from src.decompiler_data import make_new_value_for_reg
from src.register_type import RegisterType


class SBfe(BaseInstruction):
    def __init__(self, node, suffix):
        super().__init__(node, suffix)
        self.sdst = self.instruction[1]
        self.ssrc0 = self.instruction[2]
        self.ssrc1 = self.instruction[3]

    def to_print_unresolved(self):
        tab = "    "
        shift = "shift" + str(self.decompiler_data.number_of_shift)
        length = "length" + str(self.decompiler_data.number_of_length)

        if self.suffix == 'u32':
            self.decompiler_data.write("uchar " + shift + " = " + self.ssrc1 + " & 31 // s_bfe_u32\n")
            self.decompiler_data.write("uchar " + length + " = (" + self.ssrc1 + ">>16) & 07xf\n")
            self.decompiler_data.write("if (" + length + "==0)\n")
            self.decompiler_data.write(tab + self.sdst + " = 0\n")
            self.decompiler_data.write("if (" + shift + " + " + length + " < 32)\n")
            self.decompiler_data.write(tab + self.sdst + " = " + self.ssrc0 + " << (32 - " + shift + " - " + length
                                       + ") >> (32 - " + length + ")\n")
            self.decompiler_data.write("else\n")
            self.decompiler_data.write(tab + self.sdst + " = " + self.ssrc0 + " >> " + shift + "\n")
            self.decompiler_data.write("scc = " + self.sdst + " != 0\n")
            self.decompiler_data.number_of_length += 1
            self.decompiler_data.number_of_shift += 1
            return self.node
        elif self.suffix == 'i32':
            self.decompiler_data.write("uchar " + shift + " = " + self.ssrc1 + " & 31 // s_bfe_i32\n")
            self.decompiler_data.write("uchar " + length + " = (" + self.ssrc1 + ">>16) & 07xf\n")
            self.decompiler_data.write("if (" + length + "==0)\n")
            self.decompiler_data.write(tab + self.sdst + " = 0\n")
            self.decompiler_data.write("if (" + shift + " + " + length + " < 32)\n")
            self.decompiler_data.write(tab + self.sdst + " = (int)" + self.ssrc0 + " << (32 - " + shift + " - " + length
                                       + ") >> (32 - " + length + ")\n")
            self.decompiler_data.write("else\n")
            self.decompiler_data.write(tab + self.sdst + " = (int)" + self.ssrc0 + " >> " + shift + "\n")
            self.decompiler_data.write("scc = " + self.sdst + " != 0\n")
            self.decompiler_data.number_of_length += 1
            self.decompiler_data.number_of_shift += 1
            return self.node
        else:
            return super().to_print_unresolved()

    def to_fill_node(self):
        if self.suffix == 'u32':
            if self.ssrc1 == "0x20010":
                new_value = "get_work_dim()"
                reg_type = RegisterType.WORK_DIM
            elif self.ssrc1 == '0x100010':
                new_value = "get_local_size(1)"
                reg_type = RegisterType.LOCAL_SIZE_Y
            else:
                print("Unknown pattern in s_bfe")
                raise NotImplementedError()
            return make_new_value_for_reg(self.node, new_value, self.sdst, [], self.suffix, reg_type=reg_type)
        elif self.suffix == 'i32':
            return self.node
        else:
            return super().to_fill_node()
