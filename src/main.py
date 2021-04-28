import bpy
import sys
import os
sys.path.append(os.path.expanduser("~/Users/william/Documents/masters_thesis/DataPipe/src"))
print(sys.path)
from scene_module import BlendScene
from projector_module import BlendProjector



def main():

    BlendScene.set_up_scene()

    BlendProjector.add_collections_and_viewlayers()
    BlendProjector.print_collection_names()
    BlendProjector.add_light_source()

main()