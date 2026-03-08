"""
灵根 - 来源于自身，决定附带属性（五行）
"""

from dataclasses import dataclass

from attribute import Attr


@dataclass
class Linggen:
    """灵根"""

    id: str
    name: str
    attr: Attr  # 附带属性


LINGGEN_LIST = [
    Linggen("metal", "金灵根", Attr.METAL),
    Linggen("wood", "木灵根", Attr.WOOD),
    Linggen("water", "水灵根", Attr.WATER),
    Linggen("fire", "火灵根", Attr.FIRE),
    Linggen("earth", "土灵根", Attr.EARTH),
    Linggen("none", "无灵根", Attr.NONE),
]
