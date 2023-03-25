from src.decompiler_data import Singleton
from src.logical_variable import ExecCondition
from src.region_type import RegionType
from src.regions.region import Region


class Template(metaclass=Singleton):
    def process(self, region: Region) -> Region | None:
        try:
            before, res, after = self.process_main(region)
            assert len(before) <= 1
            assert len(after) <= 1

            if before:
                before[0].children = [res]
            res.parent = before

            if after:
                after[0].parent = [res]
            res.children = after

            return res
        except Exception:
            pass

    def process_main(self, region: Region) -> (Region, Region, Region):
        pass


class Pipeline(metaclass=Singleton):
    def __init__(self):
        self.ordered_templates = [
            IfElseTemplate1(),
            IfElseTemplate2(),
            IfElseTemplate4(),
            IfElseTemplate3(),
            IfTemplate2(),
            IfTemplate1(),
        ]

    def process(self, region: Region) -> Region:
        res = region
        for template in self.ordered_templates:
            temp = template.process(region)
            if temp is not None:
                res = temp
                break
        answer = JoinTemplate().process(res)
        if answer is None:
            return region
        return answer


# rocm if-else without shared non-basic part
class IfElseTemplate1(Template):
    def process_main(self, region: Region) -> (Region, Region, Region):
        ba_1 = region
        assert ba_1.type == RegionType.BASIC
        assert len(ba_1.children) == 1

        li_1 = ba_1.children[0]
        assert li_1.type != RegionType.BASIC
        assert len(li_1.children) == 1

        ba_2 = li_1.children[0]
        assert ba_2.type == RegionType.BASIC
        assert len(ba_2.children) == 1

        ba_3 = ba_2.children[0]
        assert ba_3.type == RegionType.BASIC
        assert len(ba_3.children) == 1

        assert_if_else_exec_condition(ba_1, ba_3)

        li_2 = ba_3.children[0]
        assert li_2.type != RegionType.BASIC
        assert len(li_2.children) == 1

        ba_4 = li_2.children[0]
        assert ba_4.type == RegionType.BASIC
        assert len(ba_4.children) == 1

        ba_1.children = [li_1, li_2]
        li_1.parent = [ba_1]
        li_1.children = [ba_4]
        li_2.parent = [ba_1]
        li_2.children = [ba_4]
        ba_4.parent = [li_1, li_2]

        if_else_region = Region(RegionType.IF_ELSE_STATEMENT, ba_1)
        if_else_region.end = ba_4

        return ba_1.parent, if_else_region, ba_4.children


# rocm if-else with shared non-basic part
class IfElseTemplate2(Template):
    def process_main(self, region: Region) -> (Region, Region, Region):
        ba_1 = region
        assert ba_1.type == RegionType.BASIC
        assert len(ba_1.children) == 1

        li_1 = ba_1.children[0]
        assert li_1.type != RegionType.BASIC
        assert len(li_1.children) == 1

        ba_2 = li_1.children[0]
        assert ba_2.type == RegionType.BASIC
        assert len(ba_2.children) == 1

        li_2 = ba_2.children[0]
        assert li_2.type != RegionType.BASIC
        assert len(li_2.children) == 1

        ba_3 = li_2.children[0]
        assert ba_3.type == RegionType.BASIC
        assert len(ba_3.children) == 1

        assert_if_else_exec_condition(ba_1, ba_3)

        li_3 = ba_3.children[0]
        assert li_3.type != RegionType.BASIC
        assert len(li_3.children) == 1

        ba_4 = li_3.children[0]
        assert ba_4.type == RegionType.BASIC
        assert len(ba_4.children) == 1

        li_1.children = [li_2]
        li_2.parent = [li_1]
        li_2.children = [ba_4]

        li_1 = JoinTemplate().process(li_1)

        ba_1.children = [li_1, li_3]
        li_3.parent = [ba_1]
        li_3.children = [ba_4]
        ba_4.parent = [li_1, li_3]

        if_else_region = Region(RegionType.IF_ELSE_STATEMENT, ba_1)
        if_else_region.end = ba_4

        return ba_1.parent, if_else_region, ba_4.children


# s_cbranch_scc if_else
class IfElseTemplate3(Template):
    def process_main(self, region: Region) -> (Region, Region, Region):
        ba_1 = region
        assert ba_1.type == RegionType.BASIC
        assert len(ba_1.children) == 2
        assert 's_cbranch_scc' in ba_1.start.instruction[0]

        li_1, li_2 = ba_1.children
        assert li_1.type != RegionType.BASIC
        assert li_2.type != RegionType.BASIC
        assert len(li_1.children) == 1

        ba_2 = li_1.children[0]
        assert ba_2.type == RegionType.BASIC
        assert li_2.children[0] == ba_2

        if_else_region = Region(RegionType.IF_ELSE_STATEMENT, ba_1)
        if_else_region.end = ba_2

        return ba_1.parent, if_else_region, ba_2.children


# gcn if_else
class IfElseTemplate4(Template):
    def process_main(self, region: Region) -> (Region, Region, Region):
        ba_1 = region
        assert ba_1.type == RegionType.BASIC
        assert len(ba_1.children) == 1

        li_1 = ba_1.children[0]
        assert li_1.type != RegionType.BASIC
        assert len(li_1.children) == 1

        ba_2 = li_1.children[0]
        assert ba_2.type == RegionType.BASIC
        assert len(ba_2.children) == 1

        assert_if_else_exec_condition(ba_1, ba_2)

        li_2 = ba_2.children[0]
        assert li_2.type != RegionType.BASIC
        assert len(li_2.children) == 1

        ba_3 = li_2.children[0]
        assert ba_3.type == RegionType.BASIC

        ba_1.children = [li_1, li_2]
        li_1.children = [ba_3]
        li_2.parent = [ba_1]
        li_2.children = [ba_3]
        ba_3.parent = [li_1, li_2]

        if_else_region = Region(RegionType.IF_ELSE_STATEMENT, ba_1)
        if_else_region.end = ba_2

        return ba_1.parent, if_else_region, ba_3.children


# rocm if with exec restoration after if
class IfTemplate1(Template):
    def process_main(self, region: Region) -> (Region, Region, Region):
        ba_1 = region
        assert ba_1.type == RegionType.BASIC
        assert len(ba_1.children) == 1
        assert_if_exec_condition(ba_1)

        li_1 = ba_1.children[0]
        assert li_1.type != RegionType.BASIC
        assert len(li_1.children) == 1

        ba_2 = li_1.children[0]
        assert ba_2.type == RegionType.BASIC

        ba_1.children.append(ba_2)

        if_region = Region(RegionType.IF_STATEMENT, ba_1)
        if_region.end = ba_2

        return ba_1.parent, if_region, ba_2.children


# s_cbranch_scc if
class IfTemplate2(Template):
    def process_main(self, region: Region) -> (Region, Region, Region):
        ba_1 = region
        assert ba_1.type == RegionType.BASIC
        assert len(ba_1.children) == 2
        assert 's_cbranch_scc' in ba_1.start.instruction[0]

        li_1, ba_2 = ba_1.children if ba_1.children[0].type != RegionType.BASIC else ba_1.children[::-1]
        assert li_1.type != RegionType.BASIC
        assert ba_2.type == RegionType.BASIC
        assert len(li_1.children) == 1
        assert li_1.children[0] == ba_2

        ba_1.children = [li_1, ba_2]

        if_region = Region(RegionType.IF_STATEMENT, ba_1)
        if_region.end = ba_2

        return ba_1.parent, if_region, ba_2.children


# rocm if without exec restoration after if
class IfTemplate3(Template):
    def process_main(self, region: Region) -> (Region, Region, Region):
        ba_1 = region
        assert ba_1.type == RegionType.BASIC
        assert len(ba_1.children) == 1
        assert_if_exec_condition(ba_1)

        li_1 = ba_1.children[0]
        assert li_1.type != RegionType.BASIC
        assert len(li_1.children) == 0

        if_region = Region(RegionType.IF_STATEMENT, ba_1)
        if_region.end = ba_1

        return ba_1.parent, if_region, []


class JoinTemplate(Template):
    def process_main(self, region: Region) -> (Region, Region, Region):
        nb_1 = region
        assert nb_1.type != RegionType.BASIC
        assert len(nb_1.children) == 1

        nb_2 = nb_1.children[0]
        assert nb_2.type != RegionType.BASIC
        assert len(nb_2.children) <= 1

        joined = Region(RegionType.LINEAR, nb_1)
        joined.end = nb_2

        return nb_1.parent, joined, nb_2.children


def assert_if_exec_condition(ba):
    exec_condition_ba = ba.start.state.registers["exec"].exec_condition
    assert exec_condition_ba.top() != ''
    assert exec_condition_ba.top()[0] != '!'


def assert_if_else_exec_condition(ba_1, ba_2):
    assert_if_exec_condition(ba_1)
    exec_condition_ba_2 = ba_2.start.state.registers["exec"].exec_condition
    assert exec_condition_ba_2.top() != ''
    assert exec_condition_ba_2.top() == \
           ExecCondition.make_not(ba_1.start.state.registers["exec"].exec_condition.top())
