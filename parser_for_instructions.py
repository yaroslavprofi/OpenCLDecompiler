from enum import Enum, auto
from collections import deque
import copy


class Type(Enum):
    unknown = auto()
    global_id_x = auto()
    global_id_y = auto()
    global_id_z = auto()
    work_group_id_x = auto()
    work_group_id_y = auto()
    work_group_id_z = auto()
    work_item_id_x = auto()
    work_item_id_y = auto()
    work_item_id_z = auto()
    global_offset_x = auto()
    global_offset_y = auto()
    global_offset_z = auto()
    arguments_pointer = auto()
    work_group_id_x_local_size = auto()
    work_group_id_y_local_size = auto()
    work_group_id_z_local_size = auto()
    work_group_id_x_local_size_offset = auto()
    work_group_id_y_local_size_offset = auto()
    work_group_id_z_local_size_offset = auto()
    work_group_id_x_work_item_id = auto()
    param_global_id_x = auto()
    param_global_id_y = auto()
    param_global_id_z = auto()
    param = auto()
    paramA = auto()
    int32 = auto()


class Integrity(Enum):
    integer = auto()
    low_part = auto()
    high_part = auto()


class Register:
    def __init__(self, val, type_of_elem, integrity):
        self.val = val
        self.type: Type = type_of_elem
        self.integrity: Integrity = integrity


class State:
    def __init__(self):
        self.registers = \
            {
                "s0": None,
                "s1": None,
                "s2": None,
                "s3": None,
                "s4": None,
                "s5": None,
                "s6": None,
                "s7": None,
                "s8": None,
                "s9": None,
                "s10": None,
                "s11": None,
                "v0": None,
                "v1": None,
                "v2": None,
                "v3": None,
                "v4": None,
                "v5": None,
                "pc": None,
                "scc": None,
                "vcc": None,
                "exec": None
            }

    def find_first_last_num_to_from(self, to_registers, from_registers):
        left_board_from = from_registers.find("[")
        last_to = 0
        first_to = 0
        first_from = 0
        name_of_register = ""
        name_of_from = ""
        num_of_registers = 0
        if left_board_from != -1:
            separation_from = from_registers.index(":")
            right_board_from = from_registers.index("]")
            first_from = int(from_registers[(left_board_from + 1):separation_from])
            last_from = int(from_registers[(separation_from + 1):right_board_from])
            num_of_registers = last_from - first_from + 1
            name_of_from = from_registers[:left_board_from]
            from_registers = name_of_from + str(first_from)
        else:
            num_of_registers = 1
        left_board_to = to_registers.find("[")
        if left_board_to != -1:
            separation_to = to_registers.index(":")
            right_board_to = to_registers.index("]")
            first_to = int(to_registers[(left_board_to + 1):separation_to])
            last_to = int(to_registers[(separation_to + 1):right_board_to])
            name_of_register = to_registers[:left_board_to]
            to_registers = name_of_register + str(first_to)
        return first_to, last_to, num_of_registers, from_registers, to_registers, name_of_register, name_of_from, first_from

    def upload(self, to_registers, from_registers, offset, parameter_of_kernel):
        first_to, last_to, num_of_registers, from_registers, to_registers, name_of_register, name_of_from, first_from \
            = self.find_first_last_num_to_from(to_registers, from_registers)
        if self.registers[from_registers].type == Type.arguments_pointer:
            if offset == "0x0":
                self.registers[to_registers] = Register("get_global_offset(0)", Type.global_offset_x, Integrity.integer)
                self.registers[name_of_register + str(first_to + 1)] = Register("get_global_offset(0)",
                                                                                Type.global_offset_x, Integrity.integer)
                if last_to - first_to > 1:
                    self.registers[name_of_register + str(last_to - 1)] = \
                        Register("get_global_offset(1)", Type.global_offset_y, Integrity.integer)
                    self.registers[name_of_register + str(last_to)] = \
                        Register("get_global_offset(1)", Type.global_offset_y, Integrity.integer)
            if offset == "0x8":
                self.registers[to_registers] = Register("get_global_offset(1)", Type.global_offset_y, Integrity.integer)
                self.registers[name_of_register + str(first_to + 1)] = \
                    Register("get_global_offset(1)", Type.global_offset_y, Integrity.integer)
                if last_to - first_to > 1:
                    self.registers[name_of_register + str(last_to - 1)] = \
                        Register("get_global_offset(2)", Type.global_offset_z, Integrity.integer)
                    self.registers[name_of_register + str(last_to)] = \
                        Register("get_global_offset(2)", Type.global_offset_z, Integrity.integer)
            if offset == "0x10":
                self.registers[to_registers] = Register("get_global_offset(2)", Type.global_offset_z, Integrity.integer)
                self.registers[name_of_register + str(first_to + 1)] = Register("get_global_offset(2)",
                                                                                Type.global_offset_z, Integrity.integer)
            if offset == "0x30":
                val_of_register = parameter_of_kernel["param0"]
                if val_of_register[0] == "*":
                    type_param = Type.paramA
                    val_of_register = val_of_register[1:]
                else:
                    type_param = Type.param
                if last_to - first_to >= 1:
                    self.registers[to_registers] = Register(val_of_register, type_param, Integrity.low_part)
                    self.registers[name_of_register + str(last_to)] = \
                        Register(val_of_register, type_param, Integrity.high_part)
                else:
                    self.registers[to_registers] = Register(val_of_register, type_param, Integrity.integer)
            if offset == "0x38":
                val_of_register = parameter_of_kernel["param1"]
                if val_of_register[0] == "*":
                    type_param = Type.paramA
                    val_of_register = val_of_register[1:]
                else:
                    type_param = Type.param
                if last_to - first_to >= 1:
                    self.registers[to_registers] = Register(val_of_register, type_param, Integrity.low_part)
                    self.registers[name_of_register + str(last_to)] = \
                        Register(val_of_register, type_param, Integrity.high_part)
                else:
                    self.registers[to_registers] = Register(val_of_register, type_param, Integrity.integer)
            if offset == "0x40":
                val_of_register = parameter_of_kernel["param2"]
                if val_of_register[0] == "*":
                    type_param = Type.paramA
                    val_of_register = val_of_register[1:]
                else:
                    type_param = Type.param
                if last_to - first_to >= 1:
                    self.registers[to_registers] = Register(val_of_register, type_param, Integrity.low_part)
                    self.registers[name_of_register + str(last_to)] = \
                        Register(val_of_register, type_param, Integrity.high_part)
                else:
                    self.registers[to_registers] = Register(val_of_register, type_param, Integrity.integer)


class Node:
    def __init__(self, instruction, state):
        self.instruction = instruction
        self.children = []
        self.parent = []
        self.state = state

    def add_child(self, child):
        self.children.append(child)

    def add_parent(self, parent):
        self.parent.append(parent)


class TypeNode(Enum):
    basic = auto()
    linear = auto()
    ifstatement = auto()


class Region:
    def __init__(self, type_of_node, start):
        self.type: TypeNode = type_of_node
        self.start = start
        self.end = start
        self.parent = []
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def add_parent(self, parent):
        self.parent.append(parent)


class Decompiler:
    def __init__(self, output_file):
        self.output_file = output_file
        self.cfg = None
        self.improve_cfg = None
        # self.last_node = None
        self.number_of_temp = 0
        self.number_of_shift = 0
        self.number_of_length = 0
        self.number_of_mask = 0
        self.number_of_cc = 0
        self.number_of_sf0 = 0
        self.number_of_sf1 = 0
        self.number_of_sf2 = 0
        self.number_of_tmp = 0
        self.number_of_v0 = 0
        self.number_of_v1 = 0
        self.number_of_v = 0
        self.number_of_vm = 0
        self.number_of_p = 0
        self.initial_state = State()
        self.sgprsnum = 0
        self.vgprsnum = 0
        self.params = {}
        self.to_node = {}  # метка, с которой начинается блок -> вершина
        self.from_node = {}  # метку, которую ожидает вершина -> вершина ("лист ожидания")
        self.starts_regions = {}  # Node или Region -> Region
        self.ends_regions = {}  # Node или Region -> Region

    def process_config(self, set_of_config, name_of_program):
        dimentions = set_of_config[0][6:]
        if len(dimentions) > 0:
            self.initial_state.registers["s6"] = Register("s6", Type.work_group_id_x, Integrity.integer)
            self.initial_state.registers["v0"] = Register("get_local_id(0)", Type.work_item_id_x, Integrity.integer)
        if len(dimentions) > 1:
            self.initial_state.registers["s7"] = Register("s7", Type.work_group_id_y, Integrity.integer)
            self.initial_state.registers["v1"] = Register("get_local_id(1)", Type.work_item_id_y, Integrity.integer)
        if len(dimentions) > 2:
            self.initial_state.registers["s8"] = Register("s8", Type.work_group_id_z, Integrity.integer)
            self.initial_state.registers["v2"] = Register("get_local_id(2)", Type.work_item_id_z, Integrity.integer)

        size_of_work_groups = set_of_config[1].replace(',', ' ').split()
        self.output_file.write("__kernel __attribute__((reqd_work_group_size(" + size_of_work_groups[1] + ", "
                               + size_of_work_groups[2] + ", " + size_of_work_groups[3] + ")))\n")
        self.sgprsnum = int(set_of_config[2][10:])
        self.vgprsnum = int(set_of_config[3][10:])
        self.initial_state.registers["s4"] = Register("s4", Type.arguments_pointer, Integrity.low_part)
        self.initial_state.registers["s5"] = Register("s5", Type.arguments_pointer, Integrity.high_part)
        parameters = set_of_config[17:]
        self.output_file.write("void " + name_of_program + "(")
        num_of_param = 0
        flag_start = False
        for param in parameters:
            if not flag_start:
                flag_start = True
            else:
                self.output_file.write(", ")
            set_of_param = param.strip().replace(',', ' ').split()
            name_param = set_of_param[1]
            type_param = set_of_param[3]
            flag_param = ""
            if len(set_of_param) > 4:
                flag_param = "__" + set_of_param[4] + " "
            if type_param[-1] == "*":
                name_param = "*" + name_param
                type_param = type_param[:-1]
            self.params["param" + str(num_of_param)] = name_param
            self.output_file.write(flag_param + type_param + " " + name_param)
            num_of_param += 1
        self.output_file.write(")\n")

    def process_src(self):
        with open('experiments\\train.asm', 'r') as file:
            body_of_file = file.read().splitlines()
        flag_config = False
        flag_instructions = False
        set_of_instructions = []
        set_of_config = []
        name_of_program = ""
        for row in body_of_file:
            row = row.strip()
            if row.find(".kernel ") != -1:
                name_of_program = row.split()[1]
            if row == ".config":
                flag_config = True
                flag_instructions = False
            elif row == ".text":
                flag_instructions = True
            elif flag_instructions:
                set_of_instructions.append(row)
            elif flag_config:
                set_of_config.append(row)
            else:
                continue

        self.process_config(set_of_config, name_of_program)
        last_node = Node("", self.initial_state)  # root
        last_node_state = self.initial_state
        self.cfg = last_node
        for row in set_of_instructions:
            # instruction = row.strip().replace(',', ' ').split()

            curr_node = self.make_cfg_node(row, last_node_state)
            curr_node.add_parent(last_node)
            last_node_state = copy.deepcopy(curr_node.state)
            last_node.add_child(curr_node)
            last_node = curr_node
        self.process_cfg()
        self.output_file.write("{\n")
        self.make_output(self.improve_cfg, '')
        # while curr_node.children:
        #     self.to_openCL(curr_node.children[0], False)
        #     curr_node = curr_node.children[0]

    def make_cfg_node(self, instruction, last_node_state):
        return self.to_openCL(Node(instruction, last_node_state), True)

    def make_op(self, node, register1, register2, operation):
        return node.state.registers[register1].val + operation + node.state.registers[register2].val

    def union_regions(self, before_region, curr_region, next_region, start_region):
        start_now = start_region
        if before_region.type != TypeNode.basic:
            region = Region(TypeNode.linear, before_region)
            region.end = curr_region
            if before_region == start_now:
                start_now = region
            else:
                parent = before_region.parent[0]
                parent.children.remove(before_region)
                parent.add_child(region)
                region.add_parent(parent)
            next_region.parent.remove(curr_region)
            next_region.add_parent(region)
            region.add_child(next_region)
            if next_region != TypeNode.basic:
                region_all = Region(TypeNode.linear, before_region)
                region_all.end = next_region
                if start_now == region:
                    start_now = region_all
                else:
                    parent = before_region.parent[0]
                    parent.remove(region)
                    parent.add_child(region_all)
                    region_all.add_parent(parent)
                if next_region.children:
                    child = next_region.children[0]
                    child.parent.remove(next_region)
                    child.add_parent(region_all)
                    region_all.add_child(child)
            return start_now

        if next_region != TypeNode.basic:
            region_all = Region(TypeNode.linear, curr_region)
            region_all.end = next_region
            before_region.remove(curr_region)
            before_region.add_child(region_all)
            region_all.add_parent(before_region)
            if next_region.children:
                child = next_region.children[0]
                child.parent.remove(next_region)
                child.add_parent(region_all)
                region_all.add_child(child)
        return start_region

    def process_cfg(self):
        curr_node = self.cfg
        region = Region(TypeNode.linear, curr_node)
        self.starts_regions[curr_node] = region
        self.ends_regions[curr_node] = region
        visited = [curr_node]
        q = deque()
        q.append(curr_node.children[0])
        while q:
            curr_node = q.popleft()
            if curr_node not in visited:
                visited.append(curr_node)
                if len(curr_node.parent) == 1 and (len(curr_node.children) == 1 or len(curr_node.children) == 0):
                    if self.ends_regions[curr_node.parent[0]].type == TypeNode.linear:
                        region = self.ends_regions.pop(curr_node.parent[0])
                        region.end = curr_node
                        self.ends_regions[curr_node] = region
                    else:
                        region = Region(TypeNode.linear, curr_node)
                        self.starts_regions[curr_node] = region
                        self.ends_regions[curr_node] = region
                        parent = self.ends_regions[curr_node.parent[0]]
                        parent.add_child(region)
                        region.add_parent(parent)

                else:
                    region = Region(TypeNode.basic, curr_node)
                    self.starts_regions[curr_node] = region
                    self.ends_regions[curr_node] = region
                    for c_p in curr_node.parent:
                        if curr_node in visited:
                            if self.ends_regions.get(c_p) is not None:
                                parent = self.ends_regions[c_p]
                            else:
                                parent = self.ends_regions[curr_node.parent[0].children[0]]
                            parent.add_child(region)
                            region.add_parent(parent)

                for child in curr_node.children:
                    if child not in [visited]:
                        q.append(child)
        start_region = self.starts_regions[self.cfg]
        visited = []
        q = deque()
        q.append(start_region)
        while start_region.children:
            curr_region = q.popleft()
            if curr_region not in visited:
                visited.append(curr_region)
                if curr_region.type != TypeNode.linear:
                    if curr_region.type == TypeNode.basic and len(curr_region.children) == 2 \
                            and curr_region.children[1].type == TypeNode.basic \
                            and curr_region.children[0].children[0] == curr_region.children[1]:
                        region = Region(TypeNode.ifstatement, curr_region)
                        child0 = curr_region.children[0]
                        child1 = curr_region.children[1]
                        region.end = child1
                        visited.append(child1)
                        visited.append(child0)
                        before_r = curr_region.parent[0]
                        before_r.children.remove(curr_region)
                        before_r.add_child(region)
                        region.add_parent(before_r)
                        next_r = child1.children[0]
                        next_r.parent.remove(child1)
                        next_r.add_parent(region)
                        region.add_child(next_r)
                        start_region = self.union_regions(before_r, region, next_r, start_region)
                        if curr_region.children:
                            for child in curr_region.children:
                                if child not in [visited]:
                                    q.append(child)
                        else:
                            q = deque()
                            q.append(start_region)
                            visited = []
                    else:
                        if curr_region.children:
                            for child in curr_region.children:
                                if child not in [visited]:
                                    q.append(child)
                        else:
                            q = deque()
                            q.append(start_region)
                            visited = []

                else:
                    if curr_region.children:
                        for child in curr_region.children:
                            if child not in [visited]:
                                q.append(child)
                    else:
                        q = deque()
                        q.append(start_region)
                        visited = []
        self.improve_cfg = start_region

    def make_output(self, region, indent):
        if region.type == TypeNode.linear:
            if isinstance(region.start, Node):
                self.output_file.write(indent)
                reg = region.start
                if region.start == self.cfg:
                    reg = self.cfg.children[0]
                while reg != region.end:
                    self.to_openCL(reg, False)  # надо правильно будет переделать OpenCL
                    reg = reg.children[0]
                self.to_openCL(reg, False)
            else:
                reg = region.start
                self.make_output(reg, indent)
                while reg != region.end:
                    reg = reg.children[0]
                    self.make_output(reg, indent)
        elif region.type == TypeNode.ifstatement:
            self.output_file.write("    if (")
            self.to_openCL(region.start.start, False)
            self.output_file.write(") {\n")
            self.make_output(region.start.children[0], '    ')
            self.output_file.write("    }\n")

    def to_openCL(self, node, flag_of_status):
        if node.instruction[0] == ".":
            if flag_of_status:
                self.to_node[node.instruction[:-1]] = node
                if self.from_node.get(node.instruction[:-1]) is not None:
                    self.from_node[node.instruction[:-1]].add_child(node)
                    node.add_parent(self.from_node.pop(node.instruction[:-1]))
                    node.state = node.parent[-1].state
                return node
        tab = "    "
        instruction = node.instruction.strip().replace(',', ' ').split()
        operation = instruction[0]
        parts_of_operation = operation.split('_')
        prefix = parts_of_operation[0]
        suffix = ""
        root = parts_of_operation[1]
        if len(parts_of_operation) >= 3:
            for part in parts_of_operation[2:]:
                if part in ["b32", 'b64', "u32", "u64", "i32", "dwordx4", "dwordx2", "dword"]:  # дописать!
                    if suffix != "":
                        suffix = part + "_" + suffix
                    else:
                        suffix = part
                else:
                    root = root + "_" + part
        if prefix == "ds":
            if root == "bpermute":
                if suffix == "b32":
                    tmp = "tmp" + str(self.number_of_tmp)
                    dst = instruction[1]
                    addr = instruction[2]
                    src = instruction[3]
                    offset = instruction[4][7:]
                    self.output_file.write("uint64 " + tmp + "\n")  # именно массив
                    self.output_file.write("for (short i = 0; i < 64; i++)\n")
                    self.output_file.write("{\n")
                    self.output_file.write(tab + "uint lane_id = " + addr + "[(i + (" + offset + " >> 2)) & 63]\n")
                    self.output_file.write(tab + tmp + "[i] = exec & (1ULL << lane_id) != 0) ? " + src + "[lane_id] : 0\n")
                    self.output_file.write("}\n")
                    self.output_file.write("for (short i = 0; i < 64; i++)\n")
                    self.output_file.write(tab + "if (exec & (1ULL << i) != 0)\n")
                    self.output_file.write(tab + tab + dst + "[i] = " + tmp + "[i]\n")
                    self.number_of_tmp += 1

            elif root == "read":
                if suffix == "b32":
                    vdst = instruction[1]
                    addr = instruction[2]
                    offset = instruction[3][7:]
                    self.output_file.write(vdst + " = *(uint)(ds + ((" + addr + " + " + offset + ") & ~3)\n")

                elif suffix == "b64":
                    vdst = instruction[1]
                    addr = instruction[2]
                    offset = instruction[3][7:]
                    self.output_file.write(vdst + " = *(ulong)(ds + ((" + addr + " + " + offset + ") & ~7)\n")

            elif root == "read2":
                if suffix == "b64":
                    v0 = "v0" + str(self.number_of_v0)
                    v1 = "v1" + str(self.number_of_v1)
                    vdst = instruction[1]
                    addr = instruction[2]
                    offset0 = instruction[3][8:]
                    offset1 = instruction[4][8:]
                    self.output_file.write("ulong* " + v0 + " = (ulong*)(ds + (" + addr + " + " + offset0 + " * 8) & ~7)\n")
                    self.output_file.write("ulong* " + v1 + " = (ulong*)(ds + (" + addr + " + " + offset1 + " * 8) & ~7)\n")
                    self.output_file.write(vdst + " = *" + v0 + " | (ulonglong(*" + v1 + ") << 64)\n")  # uint128????
                    self.number_of_v0 += 1
                    self.number_of_v1 += 1

            elif root == "write":
                if suffix == "b32":
                    v = "v" + str(self.number_of_v)
                    addr = instruction[1]
                    vdata0 = instruction[2]
                    offset = instruction[3][7:]
                    self.output_file.write("uint* " + v + "\n")
                    self.output_file.write(v + " = (uint*)(ds + ((" + addr + " + " + offset + ") & ~3))\n")
                    self.output_file.write("*" + v + " = " + vdata0 + "\n")
                    self.number_of_v += 1

                elif suffix == "b64":
                    v = "v" + str(self.number_of_v)
                    addr = instruction[1]
                    vdata0 = instruction[2]
                    offset = instruction[3][7:]
                    self.output_file.write("ulong* " + v + "\n")
                    self.output_file.write(v + " = (ulong*)(ds + ((" + addr + " + " + offset + ") & ~3))\n")
                    self.output_file.write("*" + v + " = " + vdata0 + "\n")
                    self.number_of_v += 1

            elif root == "write2":
                if suffix == "b64":
                    v0 = "v0" + str(self.number_of_v0)
                    v1 = "v1" + str(self.number_of_v1)
                    addr = instruction[1]
                    vdata0 = instruction[2]
                    vdata1 = instruction[3]
                    offset0 = instruction[4][8:]
                    offset1 = instruction[5][8:]
                    self.output_file.write("ulong* " + v0 + " = (ulong*)(ds + (" + addr + " + " + offset0 + " * 8) & ~7)\n")
                    self.output_file.write("ulong* " + v1 + " = (ulong*)(ds + (" + addr + " + " + offset1 + " * 8) & ~7)\n")
                    self.output_file.write("*" + v0 + " = " + vdata0 + "\n")
                    self.output_file.write("*" + v1 + " = " + vdata1 + "\n")
                    self.number_of_v0 += 1
                    self.number_of_v1 += 1


        elif prefix == "flat":  # не очень понятное описание, особенно про inst_offset
            if root == "atomic_add":
                vdst = instruction[1]
                vaddr = instruction[2]
                vdata = instruction[3]
                vm = "vm" + str(self.number_of_vm)
                p = "p" + str(self.number_of_p)
                inst_offset = instruction[4]  # не очень понятно, должно ли это быть в виде INST_OFFSET:OFFSET
                self.output_file.write("uint* " + vm + " = (uint*)(" + vaddr + " + " + inst_offset + ")\n")
                self.output_file.write("uint " + p + " = *" + vm + "; *" + vm + " = *" + vm + " + " + vdata + "; "
                        + vdst + " = (glc) ? " + p + " : " + vdst + '\n')
                self.number_of_vm += 1
                self.number_of_p += 1

            elif root == "load":
                if suffix == "dword":
                    vdst = instruction[1]
                    vaddr = instruction[2]
                    inst_offset = instruction[3]
                    self.output_file.write(vdst + " = *(uint)(" + vaddr + " + " + inst_offset + "\n")

                elif suffix == "dwordx4":
                    vdst = instruction[1]
                    vaddr = instruction[2]
                    inst_offset = instruction[3]
                    vm = "vm" + str(self.number_of_vm)
                    self.output_file.write("short* " + vm + " = (" + vaddr + " + " + inst_offset + ")\n")
                    self.output_file.write(vdst + "[0] = *(uint*)" + vm + "\n")
                    self.output_file.write(vdst + "[1] = *(uint*)(" + vm + " + 4)\n")
                    self.output_file.write(vdst + "[2] = *(uint*)(" + vm + " + 8)\n")
                    self.output_file.write(vdst + "[3] = *(uint*)(" + vm + " + 12)\n")
                    self.number_of_vm += 1

            elif root == "store":
                if suffix == "dword":
                    vaddr = instruction[1]
                    vdata = instruction[2]
                    inst_offset = "0" if len(instruction) < 4 else instruction[3]
                    first_to, last_to, num_of_registers, from_registers, to_registers, name_of_register, name_of_from, first_from \
                        = node.state.find_first_last_num_to_from(vaddr, vdata)
                    if flag_of_status:
                        if first_to == last_to:
                            node.state.registers[to_registers] = \
                                Register(node.state.registers[vdata].val, node.state.registers[from_registers].type,
                                         Integrity.integer)
                        else:
                            node.state.registers[to_registers] = \
                                Register(node.state.registers[vdata].val, node.state.registers[from_registers].type,
                                         Integrity.low_part)
                            to_now = name_of_register + str(first_to + 1)
                            node.state.registers[to_now] = \
                                Register(node.state.registers[vdata].val, node.state.registers[from_registers].type,
                                         Integrity.high_part)
                        return node
                    if inst_offset != "0":
                        self.output_file.write(
                            "*(uint*)(" + node.parent[0].state.registers[to_registers].val + " + " + inst_offset + ") = " +
                            node.state.registers[name_of_register + str(first_to)].val + "\n")
                    else:
                        self.output_file.write(tab + node.parent[0].state.registers[to_registers].val + " = " + node.state.registers[
                            name_of_register + str(first_to)].val + "\n")
                    # self.output_file.write("*(uint*)(" + vaddr + " + " + inst_offset + ") = " + vdata + "\n")  # нужен ли номер...

                elif suffix == "dwordx4":
                    vaddr = instruction[1]
                    vdata = instruction[2]
                    inst_offset = instruction[3]
                    vm = "vm" + str(self.number_of_vm)
                    self.output_file.write("short* " + vm + " = (" + vaddr + " + " + inst_offset + ")\n")
                    self.output_file.write("*(uint*)(" + vm + ") = " + vdata + "[0]\n")
                    self.output_file.write("*(uint*)(" + vm + " + 4) = " + vdata + "[1]\n")
                    self.output_file.write("*(uint*)(" + vm + " + 8) = " + vdata + "[2]\n")
                    self.output_file.write("*(uint*)(" + vm + " + 12) = " + vdata + "[3]\n")
                    self.number_of_vm += 1

        elif prefix == 'global':  # offset - опциональная часть?
            if root == "load":
                if suffix == "dword":
                    vdst = instruction[1]
                    vaddr = instruction[2]
                    saddr = "0" if instruction[3] == "off" else instruction[3]
                    inst_offset = "0" if len(instruction) == 4 else instruction[4]
                    self.output_file.write(vdst + " = *(uint*)(" + vaddr + " + " + saddr + " + " + inst_offset + ")\n")

                elif suffix == "dwordx2":
                    vdst = instruction[1]
                    vaddr = instruction[2]
                    saddr = "0" if instruction[3] == "off" else instruction[3]
                    inst_offset = "0" if len(instruction) == 4 else instruction[4]
                    self.output_file.write(vdst + " = *(ulong*)(" + vaddr + " + " + saddr + " + " + inst_offset + ")\n")

            elif root == "store":
                if suffix == "dword":
                    vaddr = instruction[1]
                    vdata = instruction[2]
                    saddr = 0 if instruction[3] == "off" else instruction[3]
                    inst_offset = 0 if len(instruction) == 4 else instruction[4]
                    self.output_file.write("*(uint*)(" + vaddr + " + " + saddr + " + " + inst_offset + ") = " + vdata + "\n")

                elif suffix == "dwordx2":
                    vaddr = instruction[1]
                    vdata = instruction[2]
                    saddr = 0 if instruction[3] == "off" else instruction[3]
                    inst_offset = 0 if len(instruction) == 4 else instruction[4]
                    self.output_file.write("*(ulong*)(" + vaddr + " + " + saddr + " + " + inst_offset + ") = " + vdata + "\n")

        elif prefix == 's':
            if root == 'add':
                if suffix == 'u32':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    new_val = "(ulong)" + ssrc0 + " + (ulong)" + ssrc1
                    if flag_of_status:
                        if node.state.registers[ssrc0].type == Type.work_group_id_x_local_size \
                                and node.state.registers[ssrc1].type == Type.global_offset_x:
                            node.state.registers[sdst] = \
                                Register(new_val, Type.work_group_id_x_local_size_offset, Integrity.integer)
                        elif node.state.registers[ssrc0].type == Type.work_group_id_y_local_size \
                                and node.state.registers[ssrc1].type == Type.global_offset_y:
                            node.state.registers[sdst] = \
                                Register(new_val, Type.work_group_id_y_local_size_offset, Integrity.integer)
                        elif node.state.registers[ssrc0].type == Type.work_group_id_z_local_size \
                                and node.state.registers[ssrc1].type == Type.global_offset_z:
                            node.state.registers[sdst] = \
                                Register(new_val, Type.work_group_id_z_local_size_offset, Integrity.integer)
                        return node

                    # temp = "temp" + str(self.number_of_temp)
                    # self.output_file.write("ulong " + temp + " = " + new_val + "\n")
                    # self.output_file.write(sdst + " = " + temp + "\n")
                    # self.output_file.write("scc = " + temp + " >> 32\n")
                    # self.number_of_temp += 1

            elif root == 'addc':
                if suffix == 'u32':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    temp = " temp" + str(self.number_of_temp)
                    self.output_file.write("ulong " + temp + " = (ulong)" + ssrc0 + " + (ulong)" + ssrc1 + " scc\n")
                    self.output_file.write(sdst + " = " + temp + "\n")
                    self.output_file.write("scc = " + temp + " >> 32\n")
                    self.number_of_temp += 1

            elif root == 'and':
                if suffix == 'b32' or suffix == 'b64':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    self.output_file.write(sdst + " = " + ssrc0 + " & " + ssrc1 + "\n")
                    self.output_file.write("scc = " + sdst + " != 0\n")

            elif root == 'and_saveexec':
                if suffix == 'b64':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    if flag_of_status:
                        node.state.registers[sdst] = node.state.registers["exec"]
                        node.state.registers["exec"] = node.state.registers[ssrc0]
                        return node
                    # self.output_file.write(sdst + " = " + "exec\n")
                    # self.output_file.write("exec = " + ssrc0 + " & exec\n")
                    # self.output_file.write("scc = exec != 0\n")

            elif root == 'andn2':
                if suffix == 'b64':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    self.output_file.write(sdst + " = " + ssrc0 + " & ~" + ssrc1 + "\n")
                    self.output_file.write("scc = " + sdst + " != 0\n")

            elif root == 'ashr':
                if suffix == 'i32':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    self.output_file.write(sdst + " = (int)" + ssrc0 + " >> (" + ssrc1 + " & 31)\n")
                    self.output_file.write("scc = " + sdst + " != 0\n")

            elif root == 'barrier':
                self.output_file.write("barrier(CLK_LOCAL_MEM_FENCE);\n")

            elif root == 'bfe':
                if suffix == 'u32':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    shift = "shift" + str(self.number_of_shift)
                    length = "length" + str(self.number_of_length)
                    self.output_file.write("uchar " + shift + " = " + ssrc1 + " & 31\n")
                    self.output_file.write("uchar " + length + " = (" + ssrc0 + " >> 16) & 0x7f\n")
                    self.output_file.write("if (" + length + " == 0)\n")
                    self.output_file.write(tab + sdst + " = 0\n")
                    self.output_file.write("if (" + shift + " + " + length + " < 32)\n")
                    self.output_file.write(tab + sdst + " = " + ssrc0 + " << (32 - " + shift + " - " + length + ") >> (32 - "
                            + length + "\n")
                    self.output_file.write("else\n")
                    self.output_file.write(tab + sdst + " = " + instruction[2] + " >> " + shift + "\n")
                    self.output_file.write("scc = " + ssrc0 + " != 0\n")
                    self.number_of_length += 1
                    self.number_of_shift += 1

            elif root == 'branch':
                reladdr = instruction[1]
                self.output_file.write("pc = " + reladdr + "\n")

            elif root == 'cbranch_execz':
                reladdr = instruction[1]
                if flag_of_status:
                    if self.to_node.get(reladdr) is not None:
                        node.add_child(self.to_node[reladdr])
                        self.to_node[reladdr].add_parent(node)
                    else:
                        self.from_node[reladdr] = node
                    return node
                self.output_file.write(node.state.registers["exec"].val)
                # self.output_file.write("pc = exec == 0 ? " + reladdr + " : pc + 4\n")

            elif root == 'cbranch_scc0':
                reladdr = instruction[1]
                self.output_file.write("pc = scc0 == 0 ? " + reladdr + " : pc + 4\n")

            elif root == 'cbranch_scc1':
                reladdr = instruction[1]
                self.output_file.write("pc = scc1 == 0 ? " + reladdr + " : pc + 4\n")

            elif root == 'cbranch_vccnz':
                reladdr = instruction[1]
                self.output_file.write("pc = vcc != 0 ? " + reladdr + " : pc + 4")

            elif root == 'cmp_eq':
                if suffix == 'i32' or suffix == 'u32':
                    ssrc0 = instruction[1]
                    ssrc1 = instruction[2]
                    self.output_file.write("scc = " + ssrc0 + " == " + ssrc1 + "\n")

            elif root == 'cmp_ge':
                if suffix == 'i32':
                    ssrc0 = instruction[1]
                    ssrc1 = instruction[2]
                    self.output_file.write("scc = (int)" + ssrc0 + " >= (int)" + ssrc1 + "\n")

                elif suffix == 'u32':
                    ssrc0 = instruction[1]
                    ssrc1 = instruction[2]
                    self.output_file.write("scc = " + ssrc0 + " >= " + ssrc1 + "\n")

            elif root == 'cmp_lt':
                if suffix == 'i32':
                    ssrc0 = instruction[1]
                    ssrc1 = instruction[2]
                    self.output_file.write("scc = (int)" + ssrc0 + " < (int)" + ssrc1 + "\n")

            elif root == 'cselect':
                if suffix == 'b64':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    self.output_file.write(sdst + " = scc ? " + ssrc0 + " : " + ssrc1 + "\n")

            elif root == 'endpgm':
                if flag_of_status:
                    return node
                self.output_file.write("}\n")
            # здесь должна будет быть закрывающаяся скобка
            elif root == 'getpc':
                if suffix == 'b64':
                    sdst = instruction[1]
                    self.output_file.write(sdst + " = pc + 4\n")

            elif root == 'load':
                if suffix == 'dword':
                    sdata = instruction[1]
                    sbase = instruction[2]
                    offset = instruction[3]
                    first_to, last_to, num_of_registers, from_registers, to_registers, name_of_register, name_of_from, first_from \
                        = node.state.find_first_last_num_to_from(sdata, sbase)
                    if flag_of_status:
                        node.state.upload(sdata, sbase, offset, self.params)
                        return node
                    # self.output_file.write(sdata + " = *(uint*)(smem + (" + offset + " & ~3))\n")

                elif suffix == 'dwordx2':
                    sdata = instruction[1]
                    sbase = instruction[2]
                    offset = instruction[3]
                    first_to, last_to, num_of_registers, from_registers, to_registers, name_of_register, name_of_from, first_from \
                        = node.state.find_first_last_num_to_from(sdata, sbase)
                    if flag_of_status:
                        node.state.upload(sdata, sbase, offset, self.params)
                        return node
                    # self.output_file.write(sdata + " = " + node.state.registers[to_registers].val + "\n")
                    # self.output_file.write(sdata + " = *(ulong*)(smem + (" + offset + " & ~3))\n")  # smem??? как и dc..

                elif suffix == 'dwordx4' or suffix == 'dwordx8':
                    sdata = instruction[1]
                    sbase = instruction[2]
                    offset = instruction[3]
                    first_to, last_to, num_of_registers, from_registers, to_registers, name_of_register, name_of_from, first_from \
                        = node.state.find_first_last_num_to_from(sdata, sbase)
                    if flag_of_status:
                        node.state.upload(sdata, sbase, offset, self.params)
                        return node
                    # self.output_file.write("for (short i = 0; i < " + suffix[-1] + "; i++)\n")
                    # self.output_file.write(tab + sdata + " = *(uint*)(smem + i * 4 + (" + offset + " & ~3))\n")

            elif root == 'lshl':
                if suffix == 'b32' or suffix == 'b64':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    if flag_of_status:
                        if node.state.registers[ssrc0].type == Type.work_group_id_x:
                            node.state.registers[sdst] = Register(ssrc0 + " * " + str(pow(2, int(ssrc1))),
                                                                  Type.work_group_id_x_local_size, Integrity.integer)
                            node.state.registers["scc"] = Register(sdst + "!= 0", Type.int32, Integrity.integer)
                            return node
                        elif node.state.registers[ssrc0].type == Type.work_group_id_y:
                            node.state.registers[sdst] = Register(ssrc0 + " * " + str(pow(2, int(ssrc1))),
                                                                  Type.work_group_id_y_local_size, Integrity.integer)
                            node.state.registers["scc"] = Register(sdst + "!= 0", Type.int32, Integrity.integer)
                            return node
                        elif node.state.registers[ssrc0].type == Type.work_group_id_z:
                            node.state.registers[sdst] = Register(ssrc0 + " * " + str(pow(2, int(ssrc1))),
                                                                  Type.work_group_id_z_local_size, Integrity.integer)
                            node.state.registers["scc"] = Register(sdst + "!= 0", Type.int32, Integrity.integer)
                            return node
                        return node
                    # self.output_file.write(sdst + " = " + node.state.registers[sdst].val + "\n")
                    # self.output_file.write("scc = " + sdst + " != 0\n")
                    # self.output_file.write(sdst + " = " + ssrc0 + " << (" + ssrc1 + " & " + str(int(suffix[1:]) - 1) + ")\n")

            elif root == 'mov':
                if suffix == 'b32' or suffix == 'b64':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    if flag_of_status:
                        if node.state.registers.get(ssrc0) is not None:
                            node.state.registers[sdst] = Register(ssrc0, node.state.registers[ssrc0].type,
                                                                  Integrity.integer)
                        else:
                            node.state.registers[sdst] = Register(ssrc0, Type.int32, Integrity.integer)
                        return node
                    # self.output_file.write(sdst + " = " + ssrc0 + "\n")

            elif root == 'movk':
                if suffix == 'i32':
                    sdst = instruction[1]
                    simm16 = instruction[2]
                    self.output_file.write(sdst + " = " + simm16 + "\n")

            elif root == 'mul':
                if suffix == 'i32':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    self.output_file.write(sdst + " = " + ssrc0 + " * " + ssrc1 + "\n")

            elif root == 'mulk':
                if suffix == 'i32':
                    sdst = instruction[1]
                    simm16 = instruction[2]
                    self.output_file.write(sdst + " = " + sdst + " * " + simm16 + "\n")

            elif root == 'not':
                if suffix == 'b64':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    self.output_file.write(sdst + " = ~" + ssrc0 + "\n")
                    self.output_file.write("scc = " + sdst + " != 0\n")

            elif root == 'set_gpr_idx_on':
                ssrc0 = instruction[1]
                imm8 = instruction[2]
                self.output_file.write("mode = (mode & ~(1U << 27)) | (1U << 27)\n")
                self.output_file.write("m0 = (m0 & 0xffff0f00) | ((" + imm8 + " & 15) << 12) | (" + ssrc0 + " & 0xff)\n")

            elif root == 'set_gpr_idx_off':
                self.output_file.write("mode = (mode & ~(1U << 27))\n")

            elif root == 'setpc':
                if suffix == 'b64':
                    ssrc0 = instruction[1]
                    self.output_file.write("pc = " + ssrc0 + "\n")

            elif root == 'setreg':  # возможно это неправда
                if suffix == 'b32':
                    hwreg = instruction[1]
                    hwregname = instruction[2]
                    bitoffset = instruction[3]
                    bitsize = instruction[4]
                    sdst = instruction[5]
                    mask = "mask" + str(self.number_of_mask)
                    self.output_file.write("uint " + mask + " = (1U << " + bitsize + ") - 1U) << " + bitoffset + "\n")
                    self.output_file.write(hwreg + " = (" + hwreg + "& ~" + mask + ") | ((" + sdst + " << " + bitoffset + ") & " + mask
                            + ")\n")
                    self.number_of_mask += 1

            elif root == 'sub':
                if suffix == 'i32':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    temp = "temp" + str(self.number_of_temp)
                    self.output_file.write(sdst + " = " + ssrc0 + " - " + ssrc1 + "\n")
                    self.output_file.write("long " + temp + " = (long)" + ssrc0 + " - (long)" + ssrc1 + "\n")  # SEXT64 - long?
                    self.output_file.write("scc = " + temp + " > ((1LL << 31) - 1) || " + temp + " < (-1LL << 31)\n")
                    self.number_of_temp += 1

                elif suffix == 'u32':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    temp = "temp" + str(self.number_of_temp)
                    self.output_file.write("ulong " + temp + " = (ulong)" + ssrc0 + " - (ulong)" + ssrc1 + "\n")
                    self.output_file.write(sdst + " = " + temp + "\n")
                    self.output_file.write("scc = (" + temp + " >> 32) != 0\n")
                    self.number_of_temp += 1

            elif root == 'subb':
                if suffix == 'u32':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    ssrc1 = instruction[3]
                    temp = "temp" + str(self.number_of_temp)
                    self.output_file.write("ulong " + temp + " = (ulong)" + ssrc0 + " - (ulong)" + ssrc1 + " - scc\n")
                    self.output_file.write(sdst + " = " + temp + "\n")
                    self.output_file.write("scc = (" + temp + " >> 32) & 1\n")
                    self.number_of_temp += 1

            elif root == 'swappc':
                if suffix == 'b64':
                    sdst = instruction[1]
                    ssrc0 = instruction[2]
                    self.output_file.write(sdst + " = pc + 4\n")
                    self.output_file.write("pc = " + ssrc0 + "\n")

            elif root == 'waitcnt':
                if flag_of_status:
                    return node
                # self.output_file.write("Not resolve yet. Maybe you lose.\n")

        elif prefix == 'v':
            # if root == "add_co":
            #     if suffix == "u32":
            # не 1.2
            if root == "add":
                if suffix == "u32":
                    vdst = instruction[1]
                    sdst = instruction[2]
                    src0 = instruction[3]
                    src1 = instruction[4]
                    new_val = "(ulong)" + src0 + " + (ulong)" + src1
                    if flag_of_status:
                        if node.state.registers[src0].type == Type.work_group_id_x_local_size_offset and \
                                node.state.registers[src1].type == Type.work_item_id_x or \
                                node.state.registers[src0].type == Type.global_offset_x and \
                                node.state.registers[src1].type == Type.work_group_id_x_work_item_id:
                            new_integrity = node.state.registers[src1].integrity
                            node.state.registers[vdst] = Register("get_global_id(0)", Type.global_id_x, new_integrity)
                        elif node.state.registers[src0].type == Type.work_group_id_y_local_size_offset and \
                                node.state.registers[src1].type == Type.work_item_id_y or \
                                node.state.registers[src0].type == Type.global_offset_y and \
                                node.state.registers[src1].type == Type.work_group_id_y_work_item_id:
                            new_integrity = node.state.registers[src1].integrity
                            node.state.registers[vdst] = Register("get_global_id(1)", Type.global_id_y, new_integrity)
                        elif node.state.registers[src0].type == Type.work_group_id_z_local_size_offset and \
                                node.state.registers[src1].type == Type.work_item_id_z:
                            new_integrity = node.state.registers[src1].integrity
                            node.state.registers[vdst] = Register("get_global_id(2)", Type.global_id_z, new_integrity)
                        elif node.state.registers[src0].type == Type.paramA \
                                and node.state.registers[src1].type in [Type.global_id_x, Type.global_id_y,
                                                                        Type.global_id_z, Type.unknown,
                                                                        Type.work_item_id_x, Type.work_item_id_y,
                                                                        Type.work_item_id_z]:
                            new_integrity = node.state.registers[src1].integrity
                            node.state.registers[vdst] = \
                                Register(node.state.registers[src0].val + "[" + node.state.registers[src1].val + "]",
                                         Type.param_global_id_x, new_integrity)
                        elif node.state.registers[src0].type == Type.work_group_id_x_local_size and node.state.registers[src1].type == Type.work_item_id_x:
                            new_integrity = node.state.registers[src1].integrity
                            node.state.registers[vdst] = \
                                Register("", Type.work_group_id_x_work_item_id, new_integrity)
                        elif node.state.registers[src0].type == Type.work_group_id_y_local_size and node.state.registers[src1].type == Type.work_item_id_y:
                            new_integrity = node.state.registers[src1].integrity
                            node.state.registers[vdst] = \
                                Register("", Type.work_group_id_y_work_item_id, new_integrity)
                        # elif node.state.registers[src0].type == Type.global_id_y and node.state.registers[src1].type == Type.global_id_z\
                        #         or node.state.registers[src0].type == Type.global_id_z and node.state.registers[src1].type == Type.global_id_y:
                        #     new_integrity = node.state.registers[src1].integrity
                        #     node.state.registers[vdst] = \
                        #         Register(node.state.registers[src0].val + " + " + node.state.registers[src1].val,
                        #                  Type.unknown, new_integrity)
                        elif node.state.registers[src0].type == Type.work_group_id_x_local_size and \
                                node.state.registers[src1].type == Type.work_item_id_x:
                            new_integrity = node.state.registers[src1].integrity
                            node.state.registers[vdst] = \
                                Register("get_global_id(0) - get_global_offset(0)", Type.unknown, new_integrity)
                        # elif node.state.registers[src0]. type == Type.param or node.state.registers[src1]. type == Type.param:
                        else:
                            new_integrity = node.state.registers[src1].integrity
                            node.state.registers[vdst] = Register(self.make_op(node, src0, src1, " + "), Type.unknown,
                                                                  new_integrity)
                        # elif node.state.registers[src0].type == Type.param and node.state.registers[src1].type
                        # не хватает описания sdst
                        return node
                    # if node.state.registers[vdst].integrity == Integrity.integer:
                    #     new_val = node.state.registers[vdst].val
                    #     temp = "temp" + str(self.number_of_temp)
                    #     mask = "mask" + str(self.number_of_mask)
                    #     self.output_file.write("ulong " + temp + " = " + new_val + "\n")
                    #     self.output_file.write(vdst + " = clamp ? min(" + temp + ", 0xffffffff) : " + temp + "\n")
                    #     self.output_file.write(sdst + " = 0\n")
                    #     self.output_file.write("ulong " + mask + " = (1ULL << laneid)\n")
                    #     self.output_file.write(sdst + " = (" + sdst + " & ~" + mask + ") | ((" + temp + " >> 32) ? " + mask + " : 0\n")
                    #     self.number_of_temp += 1
                    #     self.number_of_mask += 1

            # elif root == "add3":
            #     if suffix == "u32":
            #
            # elif root == "addc_co":
            #     if suffix == "u32":
            # не 1.2

            elif root == "addc":
                if suffix == "u32":
                    vdst = instruction[1]
                    sdst = instruction[2]
                    src0 = instruction[3]
                    src1 = instruction[4]
                    ssrc2 = instruction[5]
                    new_val = " = (ulong)" + src0 + " + (ulong)" + src1
                    if flag_of_status:
                        if node.state.registers[src0].type == Type.paramA and node.state.registers[
                            src1].type == Type.global_id_x:
                            new_integrity = node.state.registers[src1].integrity
                            node.state.registers[vdst] = Register(node.state.registers[src0].val + "[get_global_id(0)]",
                                                                  Type.param_global_id_x, new_integrity)
                        return node
                    # if node.state.registers[vdst].integrity == Integrity.integer:
                    #     new_val = node.state.registers[vdst].val
                    #     temp = "temp" + str(self.number_of_temp)
                    #     mask = "mask" + str(self.number_of_mask)
                    #     cc = "cc" + str(self.number_of_cc)
                    #     self.output_file.write("ulong " + mask + " = (1ULL << laneid)\n")
                    #     self.output_file.write("uchar " + cc + " = ((" + ssrc2 + " & " + mask + ") ? 1 : 0)\n")
                    #     self.output_file.write("ulong " + temp + " = " + new_val + " + " + cc + "\n")
                    #     self.output_file.write(sdst + " = 0\n")
                    #     self.output_file.write(vdst + " = clamp ? min(" + temp + ", 0xffffffff) : " + temp + "\n")
                    #     self.output_file.write(sdst + " = (" + sdst + " & ~" + mask + ") | ((" + temp + " >> 32) ? " + mask + " : 0)\n")
                    #     self.number_of_temp += 1
                    #     self.number_of_mask += 1
                    #     self.number_of_mask += 1

            elif root == "alignbit":
                if suffix == "b32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    src2 = instruction[4]
                    self.output_file.write(vdst + " = (((ulong)" + src0 + ") << 32) | " + src1 + ") >> (" + src2 + " & 31)\n")

            elif root == "alignbyte":
                if suffix == "b32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    src2 = instruction[4]
                    self.output_file.write(vdst + " = (((ulong)" + src0 + ") << 32) | " + src1 + ") >> ((" + src2 + " & 3) * 8)\n")

            elif root == "and":
                if suffix == "b32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(vdst + " = " + src0 + " & " + src1 + "\n")

            elif root == "and_or":
                if suffix == "b32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    src2 = instruction[4]
                    self.output_file.write(vdst + " = (" + src0 + " & " + src1 + ") | " + src2 + "\n")

            elif root == "bfi":
                if suffix == "b32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    src2 = instruction[4]
                    self.output_file.write(vdst + " = (" + src0 + " & " + src1 + ") | (~" + src0 + " & " + src2 + ")\n")

            elif root == "cmp_eq":
                if suffix == "u32" or suffix == "i32":
                    sdst = instruction[1]
                    src0 = instruction[2] if instruction[2][0] != "v" else node.state.registers[instruction[2]].val
                    src1 = instruction[3] if instruction[3][0] != "v" else node.state.registers[instruction[3]].val
                    if flag_of_status:
                        node.state.registers[sdst] = Register(src0 + " == " + src1, Type.unknown, Integrity.integer)
                        return node
                    #self.output_file.write(sdst + " = (uint)" + src0 + " == (uint)" + src1 + "\n")

            elif root == "cmp_ge":
                if suffix == "u32":
                    sdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(sdst + " = (uint)" + src0 + " >= (uint)" + src1 + "\n")

            elif root == "cmp_gt":
                if suffix == "u64":
                    sdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(sdst + " = (ulong)" + src0 + " > (uint)" + src1 + "\n")

            elif root == "cmp_lg":
                if suffix == "i32":
                    sdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(sdst + " = (int)" + src0 + " != (int)" + src1 + "\n")

                elif suffix == "u32":
                    sdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(sdst + " = (uint)" + src0 + " != (uint)" + src1 + "\n")

            elif root == "cmp_lt":
                if suffix == "u32":
                    sdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(sdst + " = (uint)" + src0 + " < (uint)" + src1 + "\n")

            elif root == "cmpx_class":  # постоянно пишут про sdst(lane) зачем...
                if suffix == "f64":
                    self.output_file.write("Not resolve yet. Maybe you lose.\n")

            elif root == "cmpx_eq":
                if suffix == "f64":
                    sdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(sdst + " = as_double(" + src0 + ") == as_double(" + src1 + ")\n")
                    self.output_file.write("exec = " + sdst + "\n")

            elif root == "cmpx_le":
                if suffix == "u32":
                    sdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(sdst + " = (uint)" + src0 + " <= (uint)" + src1 + "\n")
                    self.output_file.write("exec = " + " = " + sdst + "\n")

            elif root == "cndmask":
                if suffix == "b32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    ssrc2 = instruction[4]
                    self.output_file.write(vdst + " = " + ssrc2 + " & (1ULL << laneid) ? " + src1 + " : " + src0 + "\n")

            elif root == "cvt":
                if suffix == "f32_u32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    self.output_file.write(vdst + " = (float)" + src0 + "\n")

                elif suffix == "f64_i32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    self.output_file.write(vdst + " = (double)(int)" + src0 + "\n")

                elif suffix == "u32_f32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    self.output_file.write(instruction[1] + " = 0\n")
                    self.output_file.write("if (!isnan(as_float(" + src0 + ")))\n")
                    self.output_file.write(tab + vdst + " = (int)min(convert_int_rtz(as_float(" + src0 + ")), 4294967295.0)\n")

            elif root == "div_fixup":
                if suffix == "f64":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    src2 = instruction[4]
                    sf0 = "sf0" + str(self.number_of_sf0)
                    sf1 = "sf1" + str(self.number_of_sf1)
                    sf2 = "sf2" + str(self.number_of_sf2)
                    self.output_file.write("double " + sf0 + " = as_double(" + src0 + ")\n")
                    self.output_file.write("double " + sf1 + " = as_double(" + src1 + ")\n")
                    self.output_file.write("double " + sf2 + " = as_double(" + src2 + ")\n")
                    self.output_file.write("if (isnan(" + sf1 + ") && !isnan(" + sf2 + "))\n")
                    self.output_file.write(tab + vdst + " = nan(" + sf1 + ")\n")
                    self.output_file.write("else if (abs(" + sf2 + "))\n")
                    self.output_file.write(tab + vdst + " = nan(" + sf2 + ")\n")  # nan не может принимать что-то нецелое
                    self.output_file.write("else if (" + sf1 + " == 0.0 && " + sf2 + " == 0.0)\n")
                    self.output_file.write(tab + vdst + " = NAN\n")
                    self.output_file.write("else if (abs(" + sf1 + ") == INFINITY)\n")
                    self.output_file.write(tab + vdst + " = -NAN\n")
                    self.output_file.write("else if (" + sf1 + " == 0.0)\n")
                    self.output_file.write(tab + vdst + " = INFINITY * sign(" + sf1 + ") * sign(" + sf2 + ")\n")
                    self.output_file.write("else if (abs(" + sf1 + ") == INFINITY)\n")
                    self.output_file.write(tab + vdst + " = sign(" + sf1 + ") * sign(" + sf2 + ") >= 0 ? 0.0 : -0.0\n")
                    self.output_file.write("else if (isnan(" + sf0 + "))\n")
                    self.output_file.write(tab + vdst + " = sign(" + sf1 + ") * sign(" + sf2 + ") * INFINITY\n")
                    self.output_file.write("else\n")
                    self.output_file.write(tab + vdst + " = " + sf0 + "\n")

            elif root == "fma":
                if suffix == "f64":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    src2 = instruction[4]
                    self.output_file.write(
                        vdst + " = " + "as_double(" + src0 + ") * as_double(" + src1 + ") + as_double(" + src2 + ")\n")

            elif root == "lshlrev":
                if suffix == "b32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    if flag_of_status:
                        return node
                    # self.output_file.write(vdst + " = " + src1 + " << (" + src0 + " & 31)\n")

                elif suffix == "b64":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    first_to, last_to, num_of_registers, from_registers, to_registers, name_of_register, name_of_from, first_from \
                        = node.state.find_first_last_num_to_from(vdst, src1)
                    if flag_of_status:
                        to_registers_1 = name_of_register + str(last_to)
                        from_registers_1 = name_of_from + str(first_from + 1)
                        if node.state.registers[from_registers].type in [Type.global_id_x, Type.global_id_y, Type.global_id_z] \
                                and node.state.registers[name_of_register + str(first_from + 1)].val == "0":
                            # node.state.registers[to_registers] = \
                            #     Register(from_registers + " * " + str(pow(2, int(src0))), Type.global_id_x, Integrity.low_part)
                            # node.state.registers[to_registers_1] = \
                            #     Register(from_registers_1 + " * " + str(pow(2, int(src0))), Type.global_id_x, Integrity.high_part)
                            node.state.registers[to_registers] = \
                                Register(node.state.registers[from_registers].val, node.state.registers[from_registers].type,
                                         Integrity.low_part)
                            node.state.registers[to_registers_1] = \
                                Register(node.state.registers[from_registers_1].val, node.state.registers[from_registers].type,
                                         Integrity.high_part)
                        # нет описания под y и z
                        return node
                    # self.output_file.write(vdst + " = " + node.state.registers[to_registers].val + " + " + node.state.registers[name_of_register + str(last_to)].val + "\n") #понять, что хочу выводить
                    # self.output_file.write(vdst + " = " + src1 + " << (" + src0 + " & 63)\n")

            elif root == "lshrrev":
                if suffix == "b64":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(vdst + " = " + src1 + " >> (" + src0 + " & 63)\n")

            elif root == "min":
                if suffix == "u32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(vdst + " = min(" + src0 + ", " + src1 + ")\n")

            elif root == "mul":
                if suffix == "f64":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    self.output_file.write(vdst + " = as_double(" + src0 + ") * as_double(" + src1 + ")\n")

            elif root == "mul_lo":
                if suffix == "u32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    src1 = instruction[3]
                    if flag_of_status:
                        new_integrity = node.state.registers[src1].integrity
                        node.state.registers[vdst] = Register(self.make_op(node, src0, src1, " * "), Type.unknown,
                                                              new_integrity)
                        return node

            elif root == "mov":
                if suffix == "b32":
                    vdst = instruction[1]
                    src0 = instruction[2]
                    if flag_of_status:
                        if node.state.registers.get(src0) is not None:
                            node.state.registers[vdst] = \
                                Register(node.state.registers[src0].val, node.state.registers[src0].type,
                                         Integrity.integer)
                        else:
                            node.state.registers[vdst] = Register(src0, Type.int32, Integrity.integer)
                        return node
                    # self.output_file.write(vdst + " = " + node.state.registers[vdst].val + "\n")
                    # self.output_file.write(vdst + " = " + src0 + "\n")
            elif root == "sub":
                if suffix == "u32":
                    vdst = instruction[1]
                    vcc = instruction[2]
                    src0 = instruction[3]
                    src1 = instruction[4]
                    if flag_of_status:
                        new_integrity = node.state.registers[src1].integrity
                        node.state.registers[vdst] = Register(self.make_op(node, src0, src1, " - "), Type.unknown,
                                                              new_integrity)
                        return node

            elif root == "subrev":
                if suffix == "u32":
                    vdst = instruction[1]
                    vcc = instruction[2]
                    src0 = instruction[3]
                    src1 = instruction[4]
                    if flag_of_status:
                        new_integrity = node.state.registers[src1].integrity
                        node.state.registers[vdst] = Register(self.make_op(node, src1, src0, " - "), Type.unknown,
                                                              new_integrity)
                        return node

        else:
            self.output_file.write("Not resolve yet. Maybe you lose.\n")
    # нет таких инструкций


def main():
    output_file = open('experiments\\train_OpenCL.txt', 'w')
    decompiler = Decompiler(output_file)
    decompiler.process_src()
    output_file.close()


if __name__ == "__main__":
    main()
