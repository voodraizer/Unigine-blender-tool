bl_info = {
	"name": "Unigine tools",
	"description": "Unigine tools",
	"author": "Voodraizer",
	"version": (0, 0, 1),
	"blender": (2, 80, 0),
	"location": "Materials, Scene properties",
	"warning": 'work in progress',
	"wiki_url": "https://github.com/voodraizer/Unigine-blender-tool/",
	"tracker_url": "",
	"category": "Tools"
}



import bpy
import os
import platform
from bpy.types import Menu, Panel, Operator
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty, PointerProperty, CollectionProperty


import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Support 'reload' case.
if "bpy" in locals():
	import importlib
	if "tools" in locals():
		importlib.reload(tools)



# -----------------------------------------------------------------------------------------
# UI.
# -----------------------------------------------------------------------------------------
class Addon_UI(bpy.types.Panel):
	bl_idname = "Unigine tools."
	bl_label = "Unigine tools."
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "scene"
	
	
	
	def draw(self, context):
		scene = context.scene

		pass



# -----------------------------------------------------------------------------------------
# Register/Unregister.
# -----------------------------------------------------------------------------------------
classes = (
	Addon_UI,
	# ExportHelperSettings,
)


def register():
	from bpy.utils import register_class

	from . import tools
	
	tools.register()
	
	for cls in classes:
		register_class(cls)
	

	# bpy.types.Scene.export_helper_settings = PointerProperty(type=ExportHelperSettings)
	# bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)
	bpy.utils.register_manual_map(add_object_manual_map)
	

def unregister():
	from bpy.utils import unregister_class

	from . import tools
		
	tools.unregister()
	
	for cls in classes:
		unregister_class(cls)
	
	# try:
	# 	del bpy.types.Scene.export_helper_settings
	# except:
	# 	pass

	# bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)
	bpy.utils.unregister_manual_map(add_object_manual_map)


# def add_object_button(self, context):
#     self.layout.operator(
#         OBJECT_OT_add_object.bl_idname,
#         text="Add Object",
#         icon='PLUGIN')


def add_object_manual_map():
	# This allows you to right click on a button and link to documentation
    url_manual_prefix = "https://github.com/voodraizer/Unigine-blender-tool/"
    url_manual_mapping = (
        ("", ""),
    )
    return url_manual_prefix, url_manual_mapping
	
	

if __name__ == "__main__":
	register()

	