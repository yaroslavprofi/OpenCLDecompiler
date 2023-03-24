from src.decompiler_data import Singleton
from src.region_type import RegionType
from src.regions.region import Region


class Template(metaclass=Singleton):
    def process(self, region: Region) -> Region | None:
        try:
            before = region.parent
            assert len(before) <= 1

            res, after = self.process_main(region)
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
            IfTemplate1(),
        ]

    def process(self, region: Region) -> Region:
        res = region
        for template in self.ordered_templates:
            temp = template.process(region)
            if temp is not None:
                res = temp
                break
        return JoinTemplate().process(res)


class IfTemplate1(Template):
    def process_main(self, region: Region) -> (Region, Region):
        ba_1 = region
        assert ba_1.type == RegionType.BASIC
        assert len(ba_1.children) == 1

        li_1 = ba_1.children[0]
        assert li_1.type == RegionType.LINEAR
        assert len(li_1.children) == 1

        ba_2 = li_1.children[0]
        assert ba_2.type == RegionType.BASIC

        if_region = Region(RegionType.IF_STATEMENT, ba_1)
        if_region.end = ba_2

        return if_region, ba_2.children


class JoinTemplate(Template):
    def process_main(self, region: Region) -> (Region, Region):
        nb_1 = region
        assert nb_1.type != RegionType.BASIC
        assert len(nb_1.children) == 1

        nb_2 = nb_1.children[0]
        assert nb_2.type != RegionType.BASIC
        assert len(nb_2.children) == 0

        joined = Region(RegionType.LINEAR, region)
        joined.end = nb_2

        return joined, []
