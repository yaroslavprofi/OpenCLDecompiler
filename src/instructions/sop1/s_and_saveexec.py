from src.base_instruction import BaseInstruction
from src.decompiler_data import set_reg_value


class SAndSaveexec(BaseInstruction):
    def __init__(self, node, suffix):
        super().__init__(node, suffix)
        self.sdst = self.instruction[1]
        self.ssrc0 = self.instruction[2]

    def to_print_unresolved(self):
        if self.suffix in ["b32", "b64"]:
            exec_reg = "exec_lo" if self.suffix == "b32" else "exec"
            self.decompiler_data.write(f"{self.sdst} = {exec_reg} // {self.instruction[0]}\n")
            self.decompiler_data.write(f"{exec_reg} = {self.ssrc0} & {exec_reg}\n")
            self.decompiler_data.write(f"scc = {exec_reg} != 0\n")
            return self.node
        return super().to_print_unresolved()

    def to_fill_node(self):
        if self.suffix in ["b32", "b64"]:
            exec_reg = self.node.state.registers["exec"]
            ssrc0_val = self.node.state.registers[self.ssrc0].val

            set_reg_value(self.node, exec_reg.val, self.sdst, ["exec"], self.suffix,
                          exec_condition=exec_reg.exec_condition,
                          reg_type=exec_reg.type,
                          reg_entire=exec_reg.integrity)

            new_exec_condition = exec_reg.exec_condition & ssrc0_val

            return set_reg_value(self.node, new_exec_condition.top(), "exec", [self.ssrc0, "exec"], self.suffix,
                                 exec_condition=new_exec_condition,
                                 reg_type=exec_reg.type,
                                 reg_entire=exec_reg.integrity)
        return super().to_fill_node()

    def to_print(self):
        self.output_string = self.node.state.registers["exec"].val
        return self.output_string
