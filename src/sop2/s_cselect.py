from base_instruction import BaseInstruction
from decompiler_data import DecompilerData
from integrity import Integrity
from register import Register
from type_of_reg import Type


class SCselect(BaseInstruction):
    def execute(self, node, instruction, flag_of_status, suffix):
        decompiler_data = DecompilerData.Instance()
        output_string = ""
        if suffix == 'b64':
            sdst = instruction[1]
            ssrc0 = instruction[2]
            ssrc1 = instruction[3]
            if flag_of_status:
                if ssrc0 == "exec":
                    ssrc0 = "1"
                new_val = node.state.registers["scc"].val + " ? " + ssrc0 + " : " + ssrc1
                node.state.registers[sdst] = Register(new_val, Type.unknown, Integrity.integer)
                if decompiler_data.versions.get(sdst) is None:
                    decompiler_data.versions[sdst] = 0
                node.state.make_version(decompiler_data.versions, sdst)
                if sdst in [ssrc0, ssrc1]:
                    node.state.registers[sdst].make_prev()
                node.state.registers[sdst].type_of_data = suffix
                return node
            return output_string
            # decompiler_data.output_file.write(sdst + " = scc ? " + ssrc0 + " : " + ssrc1 + "\n")
