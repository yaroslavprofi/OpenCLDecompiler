from src.base_instruction import BaseInstruction
from src.decompiler_data import DecompilerData, make_op
from src.integrity import Integrity
from src.operation_status import OperationStatus
from src.register import Register
from src.register_type import RegisterType


class SAddc(BaseInstruction):
    def execute(self, node, instruction, flag_of_status, suffix):
        decompiler_data = DecompilerData()
        output_string = ""
        if suffix == 'u32':
            sdst = instruction[1]
            ssrc0 = instruction[2]
            ssrc1 = instruction[3]
            if flag_of_status == OperationStatus.to_print_unresolved:
                temp = "temp" + str(decompiler_data.number_of_temp)
                decompiler_data.write("ulong " + temp + " = (ulong)" + ssrc0
                                      + " + (ulong)" + ssrc1 + " + scc // s_addc_u32\n")
                decompiler_data.write(sdst + " = " + temp + "\n")
                decompiler_data.write("scc = " + temp + " >> 32\n")
                decompiler_data.number_of_temp += 1
                return node
            new_val, ssrc0_reg, ssrc1_reg = make_op(node, ssrc0, ssrc1, " + ", '(ulong)', '(ulong)')
            if flag_of_status == OperationStatus.to_fill_node:
                if ssrc0_reg and ssrc1_reg:
                    if node.state.registers[ssrc0].type == RegisterType.address_paramA:
                        if node.state.registers[ssrc0].type_of_data in ['u32', 'i32', 'gu32', 'gi32']:
                            new_val, _, _ = make_op(node, ssrc1, "4", " / ", '', '')
                            new_val, _, _ = make_op(node, ssrc0, new_val, " + ", '', '')
                            node.state.registers[sdst] = \
                                Register(new_val, RegisterType.address_paramA, Integrity.entire)
                    else:
                        node.state.registers[sdst] = \
                            Register(new_val, RegisterType.unknown, Integrity.entire)
                else:
                    type_reg = RegisterType.int32
                    if ssrc0_reg:
                        type_reg = node.state.registers[ssrc0].type
                    if ssrc1_reg:
                        type_reg = node.state.registers[ssrc1].type
                    if node.state.registers[ssrc0].type == RegisterType.address_paramA:
                        if node.state.registers[ssrc0].type_of_data in ['u32', 'i32', 'gu32', 'gi32']:
                            new_val, _, _ = make_op(node, ssrc1, "4", " / ", '', '')
                            new_val, _, _ = make_op(node, ssrc0, new_val, " + ", '', '')
                    node.state.registers[sdst] = \
                        Register(new_val, type_reg, Integrity.entire)
                decompiler_data.make_version(node.state, sdst)
                if sdst in [ssrc0, ssrc1]:
                    node.state.registers[sdst].make_prev()
                if node.state.registers[ssrc0].type == RegisterType.address_paramA:
                    if ssrc0 == sdst:
                        node.state.registers[sdst].type_of_data = node.parent[0].state.registers[ssrc0].type_of_data
                    else:
                        node.state.registers[sdst].type_of_data = node.state.registers[ssrc0].type_of_data
                else:
                    node.state.registers[sdst].type_of_data = suffix
                return node
            return output_string
