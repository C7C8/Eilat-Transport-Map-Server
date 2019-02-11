from fastkml import kml
import pickle
from shapely.geometry import box

"""Hacked together module for filtering KML and removing useless nodes, because
Israel's national GTFS-derived KML is HUGE and I really need less than 1 MB of it."""


def filter_kml(builder_root, exist_root, bounds):
    """Function for filtering KML to only elements within the given map bounds. Don't
    pass a KML root node directly to builder_root, it'll glitch!"""
    if not getattr(exist_root, 'features', None):
        if bounds.contains(exist_root.geometry):
            builder_root.append(exist_root)
    else:
        new_builder_root = type(exist_root)()
        temp = list(exist_root.features())
        for feature in temp:
            filter_kml(new_builder_root, feature, bounds)
        builder_root.append(new_builder_root)


def prune_kml(root):
    """Walk through a KML tree and get rid of any branches that have no children"""
    if not getattr(root, 'features', None):
        return True
    elif len(root._features) == 0:
        return False
    else:
        root._features = list(filter(lambda f: prune_kml(f), root._features))
        return len(root._features) > 0


# The below commented-out code is used to load KML from an existing KML file called 'output.kml'.
# However, parsing a 300+ MB file takes about 30 seconds, so I loaded it up *once*, pickled the
# resulting object, then just loaded **that** instead, which takes less than 2 seconds with an
# SSD despite still being 200 MB (turns out that pickle files are easier to parse)

# k = kml.KML()
# with open("output.kml", "r") as file:
#     doc = file.read().encode("utf-8")
#
# print("Length: {}".format(len(doc)))
# k.from_string(doc)

with open("kml.pkl", "rb") as file:
    k = pickle.load(file)

filteredMap = kml.KML()
mapBounds = box(34.900423, 29.515590, 34.998930, 29.596243)
for feature in k.features():
    filter_kml(filteredMap, feature, mapBounds)

prune_kml(filteredMap)
with open("filtered.kml", "w") as file:
    file.write(filteredMap.to_string(prettyprint=True))

