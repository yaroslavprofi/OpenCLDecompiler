import copy

from src.cfg import make_cfg_node, make_unresolved_node
from src.code_printer import create_opencl_body
from src.decompiler_data import DecompilerData, optimize_names_of_vars
from src.flag_type import FlagType
from src.global_data import process_global_data, gdata_type_processing
from src.kernel_params import process_kernel_params
from src.node import Node
from src.node_processor import check_realisation_for_node
from src.regions.functions_for_regions import make_region_graph_from_cfg_v2, process_region_graph_v2
from src.versions import find_max_and_prev_versions, check_for_use_new_version, change_values


def process_single_instruction(exec_stack, row, last_node):
    curr_node = make_cfg_node(row, last_node)
    if not check_realisation_for_node(curr_node, row):
        return None

    prev_exec = last_node.state.registers["exec"]
    curr_exec = curr_node.state.registers["exec"]
    parents = curr_node.parent[:]
    if curr_exec.version != prev_exec.version:
        if len(curr_exec.exec_condition.and_chain) > \
                len(prev_exec.exec_condition.and_chain):
            exec_stack.append(curr_node)
        else:
            while len(exec_stack) > 0:
                parents.append(exec_stack.pop())
    if last_node is not None and last_node.instruction != "branch" and curr_node not in last_node.children:
        last_node.add_child(curr_node)
    if len(parents) > 1:
        find_max_and_prev_versions(curr_node, parents)
    return curr_node


def process_src_with_unresolved_instruction(set_of_instructions):
    decompiler_data = DecompilerData()
    last_node_state = decompiler_data.initial_state
    num = 0
    while num < len(set_of_instructions):
        row = set_of_instructions[num]
        instruction = row.strip().replace(',', ' ').split()
        num += 1
        curr_node = make_unresolved_node(instruction, last_node_state)
        if curr_node is None:
            decompiler_data.write(row + "\n")


def process_src(name_of_program, config_data, set_of_instructions, set_of_global_data_bytes,
                set_of_global_data_instruction):
    decompiler_data = DecompilerData()
    decompiler_data.reset(name_of_program)
    initial_set_of_instructions = copy.deepcopy(set_of_instructions)
    process_global_data(set_of_global_data_instruction, set_of_global_data_bytes)
    decompiler_data.set_config_data(config_data)
    process_kernel_params(set_of_instructions)
    last_node = Node([""], decompiler_data.initial_state)
    decompiler_data.set_cfg(last_node)
    exec_stack = []
    if decompiler_data.flag_for_decompilation == FlagType.ONLY_CLRX:
        process_src_with_unresolved_instruction(initial_set_of_instructions)
        return
    for row in set_of_instructions:
        if 's_cbranch_execz' in row:
            continue
        last_node = process_single_instruction(exec_stack, row, last_node)
        if last_node is None:
            if decompiler_data.flag_for_decompilation == FlagType.ONLY_OPENCL:
                break
            decompiler_data.flag_for_decompilation = FlagType.ONLY_CLRX
            process_src_with_unresolved_instruction(initial_set_of_instructions)
            return

    optimize_names_of_vars()
    if decompiler_data.global_data:
        gdata_type_processing()
    check_for_use_new_version()
    decompiler_data.remove_unusable_versions()

    make_region_graph_from_cfg_v2()
    decompiler_data.improve_cfg = process_region_graph_v2(
        decompiler_data.starts_regions[decompiler_data.cfg], set({}))
    if decompiler_data.checked_variables != {} or decompiler_data.variables != {}:
        change_values()
    create_opencl_body()
