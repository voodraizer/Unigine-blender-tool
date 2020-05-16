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
	if "tools" in locals(): importlib.reload(tools)
	if "tmp_cry_migrate" in locals(): importlib.reload(tmp_cry_migrate)


DEFINE_CRY_MIGRATE = True

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

		layout = self.layout
		layout.separator()

		col = layout.column(align=True)
		row = col.split(factor = 0.5)
		row.operator(tools.UNIGINETOOLS_OT_CreateDefaultUILayout.bl_idname, text="Default UI")
		if (DEFINE_CRY_MIGRATE):
			row.operator(tmp_cry_migrate.UNIGINETOOLS_OT_RecreateMaterialFromXml.bl_idname, text="Recreate mats")

		layout.separator()

		col = layout.column(align=True)
		row = col.split(factor = 0.5)
		row.operator(tools.UNIGINETOOLS_OT_CreateUnigineMaterial.bl_idname, text="Create Unigine mat")

		row.operator(tools.UNIGINETOOLS_OT_CopyTexturesToProject.bl_idname, text="Copy textures")
		


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
	from . import tmp_cry_migrate
	
	tools.register()
	tmp_cry_migrate.register()
	
	for cls in classes:
		register_class(cls)
	

	# bpy.types.Scene.export_helper_settings = PointerProperty(type=ExportHelperSettings)
	# bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)
	bpy.utils.register_manual_map(add_object_manual_map)
	

def unregister():
	from bpy.utils import unregister_class

	from . import tools
	from . import tmp_cry_migrate
		
	tools.unregister()
	tmp_cry_migrate.unregister()
	
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

	