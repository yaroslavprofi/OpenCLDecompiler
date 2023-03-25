from src.instructions.sopp.s_cbranch import SCbranch
from src.logical_variable import ExecCondition


class SCbranchScc1(SCbranch):
    def to_print_unresolved(self):
        reladdr = self.instruction[1]
        self.decompiler_data.write("pc = scc==1 ?" + reladdr + " : pc+4 // s_cbranch_scc1\n")
        return self.node

    def to_print(self):
        # if cond == True, then we are not in if branch, thus we need to invert the condition to enter if branch
        self.output_string = ExecCondition.make_not(self.node.state.registers["scc"].val)
        return self.output_string
