'''
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

print("########### __init__ Start ###########")
bl_info = {
    "name" : "DataPipe",
    "author" : "William Eikrem",
    "description" : "Pipeline addon for generating synthetic 3D datasets for use in training neural networks",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy
from . import pipeline_panel
from . import pipeline_op
from .src.config_module import input_storage



## This is needed for multi file addons. Otherwise only the __init__.py file will be reloaded.
# [Blender Logo] -> System -> Reload Scripts
import os
if locals().get('loaded'):
    print("Addon was previously loaded. Force-reloading submodules.")
    loaded = False
    from importlib import reload
    from sys import modules
    modules[__name__] = reload(modules[__name__])
    for name, module in modules.items():
        if name.startswith(f"{__package__}."):
            globals()[name] = reload(module)
    del reload, modules

loaded = True

#################### Scene settings TEMP ####################
bpy.context.scene.unit_settings.system_rotation = 'RADIANS'


#Reset dict every time addon is loaded
input_storage.reset_config_dict()

def register():
    try: 
        pipeline_op.register()
        pipeline_panel.register()
    except RuntimeError as e:
        print(e)
        # This prevents having to restart blender if a registration fails midway.
        unregister()

# This is run when the addon is disabled.
def unregister():
    try:
        pipeline_op.unregister()
        pipeline_panel.unregister()
    except RuntimeError:
        pass

print("########### __init__ End ###########")