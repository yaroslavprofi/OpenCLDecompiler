from src.base_instruction import BaseInstruction
from src.decompiler_data import make_op, set_reg_value


class SXor(BaseInstruction):
    def __init__(self, node, suffix):
        super().__init__(node, suffix)
        self.sdst = self.instruction[1]
        self.ssrc0 = self.instruction[2]
        self.ssrc1 = self.instruction[3]

    def to_print_unresolved(self):
        if self.suffix == 'b32':
            self.decompiler_data.write(f"{self.sdst} = {self.ssrc0} ^ {self.ssrc1} // {self.instruction[0]}\n")
            return self.node
        return super().to_print_unresolved()

    def to_fill_node(self):
        if self.suffix == 'b32':
            if self.ssrc0 == "exec":
                new_exec_condition = self.node.state.registers[self.ssrc0].exec_condition ^ \
                                     self.node.state.registers[self.ssrc1].exec_condition
                new_value = new_exec_condition.top()
                reg_entire = self.node.state.registers[self.ssrc0].integrity
            else:
                new_exec_condition = None
                new_value = make_op(self.node, self.ssrc0, self.ssrc1, " ^ ")
                reg_entire = self.node.state.registers[self.ssrc1].integrity
            return set_reg_value(self.node, new_value, self.sdst, [self.ssrc0, self.ssrc1], self.suffix,
                                 exec_condition=new_exec_condition,
                                 reg_entire=reg_entire)
        return super().to_fill_node()
