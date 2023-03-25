from src.decompiler_data import DecompilerData, evaluate_from_hex
from src.node import Node
from src.node_processor import to_opencl
from src.opencl_types import make_opencl_type
from src.operation_status import OperationStatus
from src.region_type import RegionType


def create_opencl_body():
    decompiler_data = DecompilerData()
    write_global_data()
    decompiler_data.write(decompiler_data.get_function_definition())
    decompiler_data.write("{\n")
    for var in sorted(decompiler_data.names_of_vars.keys()):
        if " " not in var:
            type_of_var = make_opencl_type(decompiler_data.names_of_vars[var])
            if var in decompiler_data.address_params:
                var = "*" + var
            if "___" in var:
                var = var[:var.find("___")]
            decompiler_data.write("    " + type_of_var + " " + var + ";\n")
    offsets = list(decompiler_data.lds_vars.keys())
    offsets.append(decompiler_data.config_data.local_size)
    offsets.sort()
    for key in range(len(offsets) - 1):
        size_var = int((offsets[key + 1] - offsets[key]) / (int(decompiler_data.lds_vars[offsets[key]][1][1:]) / 8))
        type_of_var = make_opencl_type(decompiler_data.lds_vars[offsets[key]][1])
        decompiler_data.write("    __local " + type_of_var + " " + decompiler_data.lds_vars[offsets[key]][0]
                              + "[" + str(size_var) + "]" + ";\n")
    make_output_from_region(decompiler_data.improve_cfg, '    ')
    decompiler_data.write("}\n")


def write_global_data():
    decompiler_data = DecompilerData()
    for key, var in sorted(decompiler_data.type_gdata.items()):
        if var in ('uint', 'int'):
            list_of_gdata_values = evaluate_from_hex(decompiler_data.global_data[key], 4, '<i')
        elif var in ('ulong', 'long'):
            list_of_gdata_values = evaluate_from_hex(decompiler_data.global_data[key], 8, '<q')
        elif var == 'float':
            list_of_gdata_values = evaluate_from_hex(decompiler_data.global_data[key], 4, '<f')
        elif var == 'double':
            list_of_gdata_values = evaluate_from_hex(decompiler_data.global_data[key], 8, '<d')
        elif var in ('int2', 'int4', 'int8'):
            list_of_gdata_values = evaluate_from_hex(decompiler_data.global_data[key], 4, '<i')
        decompiler_data.write("__constant " + var + " " + key + "[] = {")
        if var in ('int2', 'int4', 'int8'):
            num = int(var[-1])
            for index, element in enumerate(list_of_gdata_values):
                if index == 0:
                    decompiler_data.write('(' + var + ')(')
                    decompiler_data.write(element)
                elif index % num == 0:
                    decompiler_data.write(', (' + var + ')(')
                    decompiler_data.write(element)
                elif index % num == num - 1:
                    decompiler_data.write(', ' + element)
                    decompiler_data.write(')')
                else:
                    decompiler_data.write(', ' + element)
        else:
            for index, element in enumerate(list_of_gdata_values):
                if index:
                    decompiler_data.write(', ' + element)
                else:
                    decompiler_data.write(element)
        decompiler_data.write("};\n\n")


def make_output_for_loop_vars(curr_node, indent):
    decompiler_data = DecompilerData()
    key = decompiler_data.loops_nodes_for_variables[curr_node]
    reg = key[:key.find("_")]
    loop_variable = decompiler_data.loops_variables[key]
    decompiler_data.write(indent + loop_variable + " = " + curr_node.state.registers[reg].val + ";\n")


def make_output_for_linear_region(region, indent):
    decompiler_data = DecompilerData()
    if isinstance(region.start, Node):
        if region.start == decompiler_data.cfg:
            curr_node = decompiler_data.cfg.children[0]
        else:
            curr_node = region.start
        while True:
            new_output = to_opencl(curr_node, OperationStatus.TO_PRINT)
            if decompiler_data.loops_nodes_for_variables.get(curr_node):
                make_output_for_loop_vars(curr_node, indent)
            elif new_output != "" and new_output is not None:
                decompiler_data.write(indent + new_output + ";\n")
            if curr_node == region.end:
                break
            curr_node = curr_node.children[0]
    else:
        curr_region = region.start
        make_output_from_region(curr_region, indent)
        while curr_region != region.end:
            curr_region = curr_region.children[0]
            make_output_from_region(curr_region, indent)


def make_output_from_part_of_if_else(region, indent, num_of_branch):
    decompiler_data = DecompilerData()
    branch_body = region.start.children[num_of_branch]
    make_output_from_region(branch_body, indent + '    ')
    to_print: dict = {}
    for key in decompiler_data.variables.keys():
        reg = key[:key.find("_")]
        r_node_parent = region.start.children[num_of_branch].end
        while not isinstance(r_node_parent, Node):
            r_node_parent = r_node_parent.end
        if r_node_parent.state.registers.get(reg) is not None \
                and r_node_parent.state.registers[reg].version == key \
                and decompiler_data.variables[key] in decompiler_data.names_of_vars.keys() \
                and decompiler_data.variables[key] != r_node_parent.state.registers[reg].val \
                and (region.start.start.parent[0].state.registers[reg] is None
                     or r_node_parent.state.registers[reg].version !=
                     region.start.start.parent[0].state.registers[reg].version):
            to_print[decompiler_data.variables[key].removeprefix("*")] = r_node_parent.state.registers[reg].val
    for var, value in to_print.items():
        decompiler_data.write(f"{indent}    {var} = {value};\n")


def make_output_from_branch_variable(region, indent):
    decompiler_data = DecompilerData()
    for key in decompiler_data.variables.keys():
        reg = key[:key.find("_")]
        if region.start.start.parent[0].state.registers[reg] is not None \
                and region.start.start.parent[0].state.registers[reg].version == key \
                and decompiler_data.variables[key] in decompiler_data.names_of_vars.keys() \
                and decompiler_data.variables[key] != region.start.start.parent[0].state.registers[reg].val:
            if "exec" in region.start.start.parent[0].state.registers[reg].val:
                continue
            decompiler_data.write(
                indent + decompiler_data.variables[key] + " = "
                + region.start.start.parent[0].state.registers[reg].val + ";\n")


def make_output_from_if_statement_region(region, indent):
    decompiler_data = DecompilerData()
    make_output_from_branch_variable(region, indent)
    decompiler_data.write(indent + "if (")
    decompiler_data.write(to_opencl(region.start.start, OperationStatus.TO_PRINT))
    decompiler_data.write(") {\n")
    make_output_from_part_of_if_else(region, indent, 0)
    decompiler_data.write(indent + "}\n")


def make_output_from_if_else_statement_region(region, indent):
    decompiler_data = DecompilerData()
    make_output_from_if_statement_region(region, indent)
    decompiler_data.write(indent + "else {\n")
    make_output_from_part_of_if_else(region, indent, 1)
    decompiler_data.write(indent + "}\n")


def make_output_from_loop_region(region, indent):
    decompiler_data = DecompilerData()
    printed_vars = []
    for key in decompiler_data.variables.keys():
        reg = key[:key.find("_")]
        probably_printed_var = decompiler_data.variables[key]
        if region.start.start.parent[0].state.registers[reg] is not None \
                and region.start.start.parent[0].state.registers[reg].version == key \
                and probably_printed_var in decompiler_data.names_of_vars.keys() \
                and probably_printed_var not in printed_vars:
            printed_vars.append(probably_printed_var)
            if "*" in probably_printed_var:
                probably_printed_var = probably_printed_var[1:]
            decompiler_data.write(
                indent + probably_printed_var + " = "
                + region.start.start.parent[0].state.registers[reg].val + ";\n")
    decompiler_data.write(indent + "do {\n")
    make_output_from_region(region.start.children[0], indent + '    ')
    decompiler_data.write(indent + "} while (")
    statement = to_opencl(region.end.start, OperationStatus.TO_PRINT)
    if "scc0" in region.end.start.instruction[0]:
        statement = "!(" + statement + ")"
    decompiler_data.write(statement)
    decompiler_data.write(");\n")


def make_output_from_break_region(region, indent):
    decompiler_data = DecompilerData()
    break_node = region.start
    decompiler_data.write(indent + "if (")
    statement = to_opencl(break_node, OperationStatus.TO_PRINT)
    if break_node.instruction[0][-4:] in ["scc0", "vccz"]:
        statement = "!(" + statement + ")"
    decompiler_data.write(statement)
    decompiler_data.write(") {\n")
    decompiler_data.write(indent + "    break;\n")
    decompiler_data.write(indent + "}\n")


def make_output_from_region(region, indent):
    decompiler_data = DecompilerData()
    if region.type == RegionType.LINEAR:
        make_output_for_linear_region(region, indent)
    elif region.type == RegionType.IF_STATEMENT:
        make_output_from_if_statement_region(region, indent)
    elif region.type == RegionType.IF_ELSE_STATEMENT:
        make_output_from_if_else_statement_region(region, indent)
    elif region.type == RegionType.LOOP:
        make_output_from_loop_region(region, indent)
    elif region.type == RegionType.CONTINUE_REGION:
        decompiler_data.write(indent + "continue;\n")
    elif region.type == RegionType.BREAK_REGION:
        make_output_from_break_region(region, indent)
    elif region.type == RegionType.RETURN_REGION:
        decompiler_data.write(indent + "return;\n")
