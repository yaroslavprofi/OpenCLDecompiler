import re
from collections import deque

from src.register_type import RegisterType
from src.decompiler_data import DecompilerData
from src.region_type import RegionType
from src.regions.region import Region
from src.templates.template import Pipeline


def add_parent_and_child(before_r, next_r, region, prev_child, prev_parent):
    index = before_r.children.index(prev_child)
    before_r.children[index] = region
    region.add_parent(before_r)

    if next_r is not None:
        index = next_r.parent.index(prev_parent)
        next_r.parent[index] = region
        region.add_child(next_r)


def check_if(curr_region):
    return curr_region.type == RegionType.BASIC and len(curr_region.children) == 2 \
           and (len(curr_region.children[0].children) > 0
                and curr_region.children[0].children[0] == curr_region.children[1]
                or len(curr_region.children[1].children) > 0
                and curr_region.children[1].children[0] == curr_region.children[0])


def check_if_else(curr_region):
    return curr_region.type == RegionType.BASIC and len(curr_region.children) == 2 \
           and len(curr_region.children[0].children) > 0 \
           and len(curr_region.children[1].children) > 0 \
           and curr_region.children[0].children[0] == curr_region.children[1].children[0]


def check_loop(region_start, region_end):
    return len(region_start.children) == 1 and len(region_start.children[0].children) == 1 \
           and region_start.children[0].children[0] == region_end


def create_new_region(prev_reg_1, prev_reg_2, next_reg):
    prev_reg_1.children.remove(next_reg)
    prev_reg_2.children.remove(next_reg)
    position = next_reg.parent.index(prev_reg_1)
    new_fiction_region = Region(RegionType.LINEAR, next_reg.start)
    next_reg.parent[position] = new_fiction_region
    next_reg.parent.remove(prev_reg_2)
    prev_reg_1.children.append(new_fiction_region)
    prev_reg_2.children.append(new_fiction_region)
    new_fiction_region.parent.append(prev_reg_1)
    new_fiction_region.parent.append(prev_reg_2)
    new_fiction_region.children.append(next_reg)
    return new_fiction_region


def join_regions(before_region, curr_region, next_region):
    result = before_region
    if before_region.type != RegionType.BASIC:
        region = Region(RegionType.LINEAR, before_region)
        region.end = curr_region
        if len(before_region.parent) > 0:
            parent = before_region.parent[0]
            index = parent.children.index(before_region)
            parent.children[index] = region
            region.add_parent(parent)
        else:
            result = region
        if next_region is not None:
            index = next_region.parent.index(curr_region)
            next_region.parent[index] = region
            region.add_child(next_region)
            if next_region.type != RegionType.BASIC and len(curr_region.parent) == 1:
                region_all = Region(RegionType.LINEAR, before_region)
                region_all.end = next_region
                if len(before_region.parent) > 0:
                    parent = before_region.parent[0]
                    index = parent.children.index(region)
                    parent.children[index] = region_all
                    region_all.add_parent(parent)
                else:
                    result = region_all
                if next_region.children:
                    child = next_region.children[0]
                    index = child.parent.index(next_region)
                    child.parent[index] = region_all
                    region_all.add_child(child)
        return result

    if next_region is not None and next_region != RegionType.BASIC and len(curr_region.parent) == 1:
        region_all = Region(RegionType.LINEAR, curr_region)
        region_all.end = next_region
        index = before_region.children.index(curr_region)
        before_region.children[index] = region_all
        region_all.add_parent(before_region)
        if next_region.children:
            child = next_region.children[0]
            index = child.parent.index(next_region)
            child.parent[index] = region_all
            region_all.add_child(child)
    return result


def make_region_graph_from_cfg():
    decompiler_data = DecompilerData()
    curr_node = decompiler_data.cfg
    region = Region(RegionType.LINEAR, curr_node)
    decompiler_data.set_starts_regions(curr_node, region)
    decompiler_data.set_ends_regions(curr_node, region)
    visited = [curr_node]
    q = deque()
    q.append(curr_node.children[0])
    while q:
        curr_node = q.popleft()
        if curr_node not in visited:
            visited.append(curr_node)
            if curr_node in decompiler_data.loops or curr_node in decompiler_data.back_edges:
                region_type = RegionType.BACK_EDGE
                if curr_node in decompiler_data.loops:
                    region_type = RegionType.START_LOOP
                region = Region(region_type, curr_node)
                decompiler_data.set_starts_regions(curr_node, region)
                decompiler_data.set_ends_regions(curr_node, region)
                for c_p in curr_node.parent:
                    if c_p in visited:
                        if decompiler_data.ends_regions.get(c_p) is not None:
                            parent = decompiler_data.ends_regions[c_p]
                        else:
                            parent = decompiler_data.ends_regions[curr_node.parent[0].children[0]]
                        parent.add_child(region)
                        region.add_parent(parent)
            elif len(curr_node.parent) == 1 and (len(curr_node.children) == 1 or len(curr_node.children) == 0):
                if decompiler_data.ends_regions[curr_node.parent[0]].type == RegionType.LINEAR:
                    region = decompiler_data.ends_regions.pop(curr_node.parent[0])
                    region.end = curr_node
                    decompiler_data.set_ends_regions(curr_node, region)
                else:
                    region = Region(RegionType.LINEAR, curr_node)
                    decompiler_data.set_starts_regions(curr_node, region)
                    decompiler_data.set_ends_regions(curr_node, region)
                    parent = decompiler_data.ends_regions[curr_node.parent[0]]
                    parent.add_child(region)
                    region.add_parent(parent)
            else:
                region = Region(RegionType.BASIC, curr_node)
                decompiler_data.set_starts_regions(curr_node, region)
                decompiler_data.set_ends_regions(curr_node, region)
                flag_of_continue = False
                for c_p in curr_node.parent:
                    if c_p not in visited and curr_node not in decompiler_data.loops:
                        flag_of_continue = True
                        break
                if flag_of_continue:
                    visited.remove(curr_node)
                    continue
                for c_p in curr_node.parent:
                    if c_p in visited:
                        if decompiler_data.ends_regions.get(c_p) is not None:
                            parent = decompiler_data.ends_regions[c_p]
                        else:
                            parent = decompiler_data.ends_regions[curr_node.parent[0].children[0]]
                        parent.add_child(region)
                        region.add_parent(parent)
            for child in curr_node.children:
                if child not in visited:
                    q.append(child)
                else:
                    region.add_child(decompiler_data.starts_regions[child])
                    decompiler_data.set_parent_for_starts_regions(child, region)


def make_region_graph_from_cfg_v2():
    decompiler_data = DecompilerData()
    curr_node = decompiler_data.cfg
    region = Region(RegionType.LINEAR, curr_node)
    decompiler_data.set_starts_regions(curr_node, region)
    decompiler_data.set_ends_regions(curr_node, region)
    visited = [curr_node]
    q = deque()
    q.append(curr_node.children[0])
    while q:
        curr_node = q.popleft()
        if curr_node not in visited:
            visited.append(curr_node)
            if curr_node in decompiler_data.loops or curr_node in decompiler_data.back_edges:
                region_type = RegionType.BACK_EDGE
                if curr_node in decompiler_data.loops:
                    region_type = RegionType.START_LOOP
                region = Region(region_type, curr_node)
                decompiler_data.set_starts_regions(curr_node, region)
                decompiler_data.set_ends_regions(curr_node, region)
                for c_p in curr_node.parent:
                    if c_p in visited:
                        if decompiler_data.ends_regions.get(c_p) is not None:
                            parent = decompiler_data.ends_regions[c_p]
                        else:
                            parent = decompiler_data.ends_regions[curr_node.parent[0].children[0]]
                        parent.add_child(region)
                        region.add_parent(parent)
            elif len(curr_node.parent) == 1 and len(curr_node.children) <= 1:
                if curr_node.state.registers["exec"].version != curr_node.parent[0].state.registers["exec"].version:
                    region = Region(RegionType.BASIC, curr_node)
                    decompiler_data.set_starts_regions(curr_node, region)
                    decompiler_data.set_ends_regions(curr_node, region)
                    parent = decompiler_data.ends_regions[curr_node.parent[0]]
                    parent.add_child(region)
                    region.add_parent(parent)
                elif decompiler_data.ends_regions[curr_node.parent[0]].type == RegionType.LINEAR:
                    region = decompiler_data.ends_regions.pop(curr_node.parent[0])
                    region.end = curr_node
                    decompiler_data.set_ends_regions(curr_node, region)
                else:
                    region = Region(RegionType.LINEAR, curr_node)
                    decompiler_data.set_starts_regions(curr_node, region)
                    decompiler_data.set_ends_regions(curr_node, region)
                    parent = decompiler_data.ends_regions[curr_node.parent[0]]
                    parent.add_child(region)
                    region.add_parent(parent)
            else:
                region = Region(RegionType.BASIC, curr_node)
                decompiler_data.set_starts_regions(curr_node, region)
                decompiler_data.set_ends_regions(curr_node, region)
                flag_of_continue = False

                for c_p in curr_node.parent:
                    if c_p not in visited and curr_node not in decompiler_data.loops:
                        flag_of_continue = True
                        break
                if flag_of_continue:
                    visited.remove(curr_node)
                    continue
                for c_p in curr_node.parent:
                    if c_p in visited:
                        if decompiler_data.ends_regions.get(c_p) is not None:
                            parent = decompiler_data.ends_regions[c_p]
                        else:
                            parent = decompiler_data.ends_regions[curr_node.parent[0].children[0]]
                        parent.add_child(region)
                        region.add_parent(parent)
            for child in curr_node.children:
                if child not in visited:
                    q.append(child)
                else:
                    region.add_child(decompiler_data.starts_regions[child])
                    decompiler_data.set_parent_for_starts_regions(child, region)


def process_if_statement_region(curr_region):
    region = Region(RegionType.IF_STATEMENT, curr_region)
    child0 = curr_region.children[0] if len(curr_region.children[0].parent) == 1 else \
        curr_region.children[1]
    child1 = curr_region.children[1] if len(curr_region.children[1].parent) > 1 else \
        curr_region.children[0]
    before_r = curr_region.parent[0]
    if len(child1.parent) > 2:
        child1 = create_new_region(curr_region, child0, child1)
    region.end = child1
    next_r = child1.children[0] if len(child1.children) > 0 else None
    add_parent_and_child(before_r, next_r, region, curr_region, region.end)
    return join_regions(before_r, region, next_r)


def process_if_else_statement_region(curr_region):
    region = Region(RegionType.IF_ELSE_STATEMENT, curr_region)
    child0 = curr_region.children[0]
    child1 = curr_region.children[1]
    region.end = child0.children[0]
    if len(region.end.parent) > 2:
        region.end = create_new_region(child0, child1, child0.children[0])
    before_r = curr_region.parent[0]
    next_r = region.end.children[0]
    add_parent_and_child(before_r, next_r, region, curr_region, region.end)
    return join_regions(before_r, region, next_r)


def make_var_for_loop(curr_node, register, version, prev_version):
    decompiler_data = DecompilerData()
    if decompiler_data.loops_variables.get(prev_version):
        variable = decompiler_data.loops_variables[prev_version]
    else:
        variable = "var" + str(decompiler_data.num_of_var)
        decompiler_data.num_of_var += 1
    # decompiler_data.make_var(first_reg_prev_version, variable,
    #                          curr_node.state.registers[register].data_type)
    decompiler_data.checked_variables[prev_version] = variable
    # decompiler_data.checked_variables[first_reg_version] = variable
    decompiler_data.loops_variables[version] = variable
    decompiler_data.loops_nodes_for_variables[curr_node] = version
    # decompiler_data.variables[first_reg_version] = variable
    decompiler_data.names_of_vars[variable] = curr_node.state.registers[register].data_type
    decompiler_data.variables[prev_version] = variable
    if curr_node.state.registers[register].type == RegisterType.ADDRESS_KERNEL_ARGUMENT:
        decompiler_data.address_params.add(variable)


def check_changes_in_reg(register, reg_versions_in_instruction, curr_node, reg_version_node):
    register_version = curr_node.state.registers[register].version
    instruction = curr_node.instruction[0]
    if reg_versions_in_instruction.get(register_version):
        change_node = reg_version_node[register_version]
        instruction_version_list = reg_versions_in_instruction[register_version]
        for version in instruction_version_list:
            instruction_register = version[:version.find("_")]
            instruction_register_version = curr_node.state.registers[instruction_register].version
            if version != instruction_register_version:
                if re.match(r"(flat|global)_store", instruction) or "cmp" in instruction:
                    prev_register_version = register_version
                else:
                    prev_register_version = curr_node.parent[0].state.registers[register].version
                make_var_for_loop(change_node, instruction_register, register_version, prev_register_version)


def process_loop(region_start, region_end):
    region = Region(RegionType.LOOP, region_start)
    region.end = region_end
    before_r = region_start.parent[0]
    next_r = region.end.children[1]
    add_parent_and_child(before_r, next_r, region, region_start, region.end)
    used_versions_of_registers = set()
    curr_node = region_start.start
    reg_versions_in_instruction = {}
    reg_version_node = {}
    first_reg = None
    first_reg_version = None
    while curr_node != region_end.start:
        list_of_reg_nums = list(range(1, len(curr_node.instruction))[1:])
        list_of_reg_nums = list_of_reg_nums if len(curr_node.instruction) == 1 else list_of_reg_nums + [1]
        if len(list_of_reg_nums) > 0:
            first_reg = curr_node.instruction[1]
            if len(first_reg) > 1 and first_reg[1] == "[":
                first_reg = first_reg[0] + first_reg[2: first_reg.find(":")]
            if "cmp" not in curr_node.instruction[0] \
                    and not re.match(r"(flat|global)_store", curr_node.instruction[0]) \
                    and curr_node.state.registers.get(first_reg):
                first_reg_version = curr_node.state.registers[first_reg].version
                reg_versions_in_instruction[first_reg_version] = []
                reg_version_node[first_reg_version] = curr_node
        for num_of_register in list_of_reg_nums:
            register = curr_node.instruction[num_of_register]
            if len(register) > 1 and register[1] == "[":
                register = register[0] + register[2: register.find(":")]
            if ("cmp" in curr_node.instruction[0]
                or re.match(r"(flat|global)_store", curr_node.instruction[0])
                or num_of_register > 1) \
                    and curr_node.state.registers.get(register):
                if register == first_reg \
                        and "cmp" not in curr_node.instruction[0] \
                        and not re.match(r"(flat|global)_store", curr_node.instruction[0]):
                    register_version = curr_node.parent[0].state.registers[register].version
                else:
                    register_version = curr_node.state.registers[register].version
                used_versions_of_registers.add(register_version)
            if curr_node.state.registers.get(register):
                if "cmp" not in curr_node.instruction[0] \
                        and not re.match(r"(flat|global)_store", curr_node.instruction[0]):
                    if num_of_register > 1 \
                            and register != first_reg:
                        reg_versions_in_instruction[first_reg_version].append(register_version)
                        check_changes_in_reg(register, reg_versions_in_instruction, curr_node, reg_version_node)
                else:
                    check_changes_in_reg(register, reg_versions_in_instruction, curr_node, reg_version_node)
            if "cmp" not in curr_node.instruction[0] \
                    and not re.match(r"(flat|global)_store", curr_node.instruction[0]) \
                    and num_of_register == 1 \
                    and curr_node.state.registers.get(register):
                separation = first_reg_version.find("_")
                first_reg_prev_version = first_reg_version[:separation + 1] \
                    + str(int(first_reg_version[separation + 1:]) - 1)
                if first_reg_prev_version in used_versions_of_registers:
                    make_var_for_loop(curr_node, register, first_reg_version, first_reg_prev_version)
        curr_node = curr_node.children[0]


def remove_region_connect(parent_region, child_region):
    parent_region.children.remove(child_region)
    child_region.parent.remove(parent_region)
    return parent_region, child_region


def process_control_structures_in_loop(region_start, region_end):
    start_region = region_start
    visited = []
    q = deque()
    q.append(start_region)
    after_region_end = region_end.children[1]
    while start_region.children[0] != after_region_end:
        curr_region = q.popleft()
        if curr_region not in visited:
            visited.append(curr_region)
            if check_loop(region_start, region_end):
                process_loop(region_start, region_end)
                return
            if curr_region.type == RegionType.BASIC and len(curr_region.children) == 2 \
                    and (after_region_end in [curr_region.children[0], curr_region.children[1]]):
                curr_region.type = RegionType.BREAK_REGION  # надо отдельно написать на return и обрезание на break
                next_region = curr_region.children[0] if curr_region.children[1] == after_region_end else \
                    curr_region.children[1]
                curr_region, after_region_end = remove_region_connect(curr_region, after_region_end)
                join_regions(curr_region.parent[0], curr_region, next_region)  # not good enough
                if curr_region.children:
                    for child in curr_region.children:
                        if child not in visited:
                            q.append(child)
                else:
                    q = deque()
                    q.append(start_region)
                    visited = []
            else:
                preprocess_if_and_if_else(curr_region, visited, start_region, q)


def get_one_loop_region(q_loops, curr_region, start_region, region_start, region_end):
    while q_loops:
        loop_region = q_loops.pop()
        if loop_region.type == RegionType.BACK_EDGE:
            loop_region.type = RegionType.CONTINUE_REGION
            join_regions(loop_region.parent[0], loop_region, loop_region.children[0])  # not good enough
        elif curr_region.start.instruction[1] == loop_region.start.instruction[0][:-1]:
            region_start = loop_region
            curr_loop = None
        else:
            start_region = loop_region
            curr_loop = loop_region
            q_loops.append(loop_region)
            break
    if check_loop(region_start, region_end):
        process_loop(region_start, region_end)
    else:
        process_control_structures_in_loop(region_start, region_end)
    return curr_loop, start_region, q_loops, region_start


def find_loops():
    decompiler_data = DecompilerData()
    start_region = decompiler_data.starts_regions[decompiler_data.loops[0]]
    q_loops = deque()  # очередь из элементов цикла
    curr_loop = start_region  # текущий старт цикла
    q_loops.append(start_region)
    q_regions = deque()  # очередь из всех регионов
    q_regions.append(start_region.children[0])
    visited = [start_region]
    while q_regions:
        curr_region = q_regions.popleft()
        if curr_region not in visited:
            visited.append(curr_region)
            if curr_region.type == RegionType.BACK_EDGE:
                if curr_region.start.instruction[1] == curr_loop.start.instruction[0][:-1]:
                    q_loops.append(curr_region)
                else:
                    region_end = curr_region  # вероятно это не так
                    region_start = curr_loop
                    curr_loop, start_region, q_loops, region_start = \
                        get_one_loop_region(q_loops, curr_region, start_region, region_start, region_end)
            elif curr_region.type == RegionType.START_LOOP:
                curr_loop = curr_region
                q_loops.append(curr_region)
            for curr_child in curr_region.children:
                if curr_child not in visited:
                    q_regions.append(curr_child)
    if q_loops:
        region_end = q_loops.pop()
        curr_region = region_end
        region_start = None
        get_one_loop_region(q_loops, curr_region, start_region, region_start, region_end)


def preprocess_if_and_if_else(curr_region, visited, start_region, q):
    if curr_region.type != RegionType.LINEAR:
        if check_if(curr_region):
            visited, q, start_region = process_if_statement_region(curr_region, visited, start_region, q)
        elif check_if_else(curr_region):
            visited, q, start_region = process_if_else_statement_region(curr_region, visited, start_region, q)
        else:
            if curr_region.children:
                for child in curr_region.children:
                    if child not in visited:
                        q.append(child)
    else:
        if curr_region.children:
            for child in curr_region.children:
                if child not in visited:
                    q.append(child)
    if not q:
        q = deque()
        q.append(start_region)
        visited = []
    return visited, q, start_region


# def if_else_template_1(region: Region) -> Region:
#     try:
#         before = region.parent
#         ba_1 = region
#         li_1 = ba_1.children[0]
#         ba_2 = li_1.children[0]
#         li_2 = ba_2.children[0]
#         ba_3 = li_2.children[0]
#         li_3 = ba_3.children[0]
#         ba_4 = li_3.children[0]
#         after = ba_4.children
#         if ba_1.type == RegionType.BASIC and \
#                 li_1.type == RegionType.LINEAR and \
#                 ba_2.type == RegionType.BASIC and \
#                 li_2.type == RegionType.LINEAR and \
#                 ba_3.type == RegionType.BASIC and \
#                 li_3.type == RegionType.LINEAR and \
#                 ba_4.type == RegionType.BASIC:
#             value = ""
#             value += li_2.value
#             value += "if (" + ba_1.start.state.registers["exec"].val.and_chain[0] + ") {\n"
#             value += '\n'.join(["\t" + row for row in li_1.value.split('\n')[:-1]]) + '\n'
#             value += "} else {\n"
#             value += '\n'.join(["\t" + row for row in li_3.value.split('\n')[:-1]]) + '\n'
#             value += "}\n"
#
#             if_else_region = Region(RegionType.LINEAR, None)
#             if_else_region.value = value
#
#             if len(before) > 0:
#                 before[0].children = [if_else_region]
#             if_else_region.parent = before
#             if_else_region.children = after
#             if len(after) > 0:
#                 after[0].parent = [if_else_region]
#
#             return if_else_region
#
#     except Exception:
#         return region
#     return region
#
#
# def if_else_template_2(region: Region) -> Region:
#     try:
#         before = region.parent
#         ba_1 = region
#         li_1 = ba_1.children[0]
#         ba_2 = li_1.children[0]
#         ba_3 = ba_2.children[0]
#         li_3 = ba_3.children[0]
#         ba_4 = li_3.children[0]
#         after = ba_4.children
#         if ba_1.type == RegionType.BASIC and \
#                 li_1.type == RegionType.LINEAR and \
#                 ba_2.type == RegionType.BASIC and \
#                 ba_3.type == RegionType.BASIC and \
#                 li_3.type == RegionType.LINEAR and \
#                 ba_4.type == RegionType.BASIC:
#             value = ""
#             value += "if (" + ba_1.start.state.registers["exec"].val.and_chain[0] + ") {\n"
#             value += '\n'.join(["\t" + row for row in li_1.value.split('\n')[:-1]]) + '\n'
#             value += "} else {\n"
#             value += '\n'.join(["\t" + row for row in li_3.value.split('\n')[:-1]]) + '\n'
#             value += "}\n"
#
#             if_else_region = Region(RegionType.LINEAR, None)
#             if_else_region.value = value
#
#             if len(before) > 0:
#                 before[0].children = [if_else_region]
#             if_else_region.parent = before
#             if_else_region.children = after
#             if len(after) > 0:
#                 after[0].parent = [if_else_region]
#
#             return if_else_region
#
#     except Exception:
#         return region
#     return region
#
#
# def if_else_template_3(region: Region) -> Region:
#     try:
#         before = region.parent
#         ba_1 = region
#         li_1, li_2 = ba_1.children
#         ba_2 = li_1.children[0]
#         ba_2_test = li_2.children[0]
#         after = ba_2.children
#         if ba_1.type == RegionType.BASIC and \
#                 li_1.type == RegionType.LINEAR and \
#                 li_2.type == RegionType.LINEAR and \
#                 ba_2.type == RegionType.BASIC and \
#                 ba_2 == ba_2_test:
#
#             statement = ba_1.start.state.registers["scc"].val
#             if "scc1" in ba_1.start.instruction[0]:
#                 statement = "!(" + statement + ")"
#             value = ""
#             value += "if (" + statement + ") {\n"
#             value += '\n'.join(["\t" + row for row in li_1.value.split('\n')[:-1]]) + '\n'
#             value += "} else {\n"
#             value += '\n'.join(["\t" + row for row in li_2.value.split('\n')[:-1]]) + '\n'
#             value += "}\n"
#
#             if_else_region = Region(RegionType.LINEAR, None)
#             if_else_region.value = value
#
#             if len(before) > 0:
#                 before[0].children = [if_else_region]
#             if_else_region.parent = before
#             if_else_region.children = after
#             if len(after) > 0:
#                 after[0].parent = [if_else_region]
#
#             return if_else_region
#
#     except Exception:
#         return region
#     return region
#
#
# def if_template_2(region: Region) -> Region:
#     try:
#         before = region.parent
#         ba_1 = region
#         li_1 = ba_1.children[0]
#         after = li_1.children
#         if ba_1.type == RegionType.BASIC and \
#                 li_1.type == RegionType.LINEAR and \
#                 len(ba_1.start.state.registers["exec"].val.and_chain) > \
#                 len(before[0].end.state.registers["exec"].val.and_chain) and \
#                 ba_1.start.state.registers["exec"].val.and_chain[0][0] != "~" and \
#                 after == []:
#             value = ""
#             value += "if (" + ba_1.start.state.registers["exec"].val.and_chain[0] + ") {\n"
#             value += '\n'.join(["\t" + row for row in li_1.value.split('\n')[:-1]]) + '\n'
#             value += "}\n"
#
#             if_region = Region(RegionType.LINEAR, None)
#             if_region.value = value
#
#             if len(before) > 0:
#                 before[0].children = [if_region]
#             if_region.parent = before
#
#             return if_region
#
#     except Exception:
#         return region
#     return region
#
#
# def if_template_1(region: Region) -> Region:
#     try:
#         before = region.parent
#         ba_1 = region
#         li_1 = ba_1.children[0]
#         ba_2 = li_1.children[0]
#         after = ba_2.children
#         if ba_1.type == RegionType.BASIC and \
#                 li_1.type == RegionType.PROCESSED and \
#                 ba_2.type == RegionType.BASIC:
#             statement_reg = "scc" if "scc" in ba_1.start.instruction[0] else "exec"
#             if statement_reg == "exec" and not (
#                     len(ba_1.start.state.registers["exec"].val.and_chain) >
#                     len(before[0].end.state.registers["exec"].val.and_chain) and
#                     ba_1.start.state.registers["exec"].val.and_chain[0][0] != "~"):
#                 return region
#             decompiler_data = DecompilerData()
#             if_region = Region(RegionType.PROCESSED, None)
#             for key in decompiler_data.variables.keys():
#                 reg = key[:key.find("_")]
#                 if region.start.parent[0].state.registers[reg].version == key \
#                         and decompiler_data.variables[key] in decompiler_data.names_of_vars.keys() \
#                         and decompiler_data.variables[key] != region.start.parent[0].state.registers[reg].val:
#                     if "exec" in region.start.parent[0].state.registers[reg].val:
#                         continue
#                     if_region.value += decompiler_data.variables[key] + " = " \
#                                   + region.start.parent[0].state.registers[reg].val + ";\n"
#             val = ba_1.start.state.registers[statement_reg].val
#             if_region.value += "if (" + ((val
#                                 if "scc0" in ba_1.start.instruction[0]
#                                 else "!(" + val + ")")
#                                if statement_reg == "scc"
#                                else val.and_chain[0]) + ") {\n"
#             if_region.value += '\n'.join(["\t" + row for row in li_1.value.split('\n')[:-1]]) + '\n'
#             if_region.value += "}\n"
#
#             if len(before) > 0:
#                 before[0].children = [if_region]
#             if_region.parent = before
#             if_region.children = after
#             if len(after) > 0:
#                 after[0].parent = [if_region]
#
#             return if_region
#
#     except Exception:
#         return region
#     return region


def process_region_graph_v2(region: Region, visited: set) -> Region:
    visited.add(region)

    for child in region.children:
        if child not in visited:
            process_region_graph_v2(child, visited)

    return Pipeline().process(region)


def process_region_graph_dfs(region: Region, visited: set) -> Region:
    visited.add(region)
    result = region

    for child in region.children:
        if child not in visited:
            result = process_region_graph_dfs(child, visited)

    if region.type == RegionType.LOOP:
        return join_regions(region.parent[0], region, region.children[0])
    elif region.type != RegionType.LINEAR:
        if check_if(region):
            return process_if_statement_region(region)
        if check_if_else(region):
            return process_if_else_statement_region(region)
    return result


def process_region_graph():
    decompiler_data = DecompilerData()
    if decompiler_data.loops:
        find_loops()
    decompiler_data.improve_cfg = process_region_graph_dfs(decompiler_data.starts_regions[decompiler_data.cfg], set({}))