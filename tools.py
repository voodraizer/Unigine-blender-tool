import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector



# -----------------------------------------------------------------------------------------
# Materials.
# -----------------------------------------------------------------------------------------
def CreateMaterialGeneric(self, context):
	'''
	Find material by name or create.
	Create material node tree.
	'''

	import os
	import sys
	file_path = os.path.dirname(os.path.abspath(__file__))
	textures_path = os.path.join(file_path, "default_tex") + "\\"

	obj = bpy.context.active_object
	mat = obj.active_material
	print("Materials: " + str(mat))

	if (mat is None):
		# create new material
		mat = bpy.data.materials.new(name = "Material")
		mat.use_nodes = True
		bpy.context.active_object.active_material = mat

	# delete all nodes
	for m in mat.node_tree.nodes:
		mat.node_tree.nodes.remove(m)
		

	mat_nodes = mat.node_tree.nodes
	mat_links = mat.node_tree.links

	# generate new node tree
	output = mat_nodes.new('ShaderNodeOutputMaterial')
	output.name = "Output"
	output.location = (0, 0)

	bsdf = mat_nodes.new('ShaderNodeBsdfPrincipled')
	bsdf.name = "Bsdf"
	bsdf.location = (-400, 0)
	mat_links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
	

	# albedo
	texture = mat_nodes.new('ShaderNodeTexImage')
	texture.name = "Albedo"
	texture.location = (-800, 50)
	texture.use_custom_color = True
	texture.color = (0.272209, 0.608, 0.378043)

	tex_path = textures_path + "default_alb.tga"
	tex_name = os.path.split(tex_path)[1]
	if (bpy.data.images.get(tex_name) == None):
		# bpy.ops.image.open(filepath='D:/wood_10_alb.tga')
		bpy.data.images.load(filepath=tex_path)
	texture.image = bpy.data.images.get(tex_name)

	mat_links.new(texture.outputs['Color'], bsdf.inputs['Base Color'])


	# normals
	texture = mat_nodes.new('ShaderNodeTexImage')
	texture.name = "Normals"
	texture.location = (-1000, -600)
	texture.use_custom_color = True
	texture.color = (0.272209, 0.608, 0.378043)

	tex_path = textures_path + "default_n.tga"
	tex_name = os.path.split(tex_path)[1]
	if (bpy.data.images.get(tex_name) == None):
		bpy.data.images.load(filepath=tex_path)
	texture.image = bpy.data.images.get(tex_name)
	texture.image.colorspace_settings.name = 'Non-Color'

	normalmap = mat_nodes.new("ShaderNodeNormalMap")
	normalmap.location = (-700, -600)
	normalmap.uv_map = "UVMap"
	mat_links.new(texture.outputs['Color'], normalmap.inputs['Color'])
	mat_links.new(normalmap.outputs['Normal'], bsdf.inputs['Normal'])


	# shading
	texture = mat_nodes.new('ShaderNodeTexImage')
	texture.name = "Shading"
	texture.location = (-1200, -250)
	texture.use_custom_color = True
	texture.color = (0.272209, 0.608, 0.378043)

	tex_path = textures_path + "default_sh.tga"
	tex_name = os.path.split(tex_path)[1]
	if (bpy.data.images.get(tex_name) == None):
		bpy.data.images.load(filepath=tex_path)
	texture.image = bpy.data.images.get(tex_name)
	texture.image.colorspace_settings.name = 'Linear'

	sep_rgb = mat_nodes.new(type="ShaderNodeSeparateRGB")
	sep_rgb.location = (-900, -300)
	sep_rgb.hide = True
	mat_links.new(texture.outputs['Color'], sep_rgb.inputs['Image'])

	mat_links.new(sep_rgb.outputs['R'], bsdf.inputs['Metallic'])

	maths = mat_nodes.new("ShaderNodeMath")
	maths.location = (-650, -350)
	maths.hide = True
	maths.operation = 'SUBTRACT'
	maths.inputs[0].default_value = 1
	mat_links.new(sep_rgb.outputs['G'], maths.inputs[1])
	mat_links.new(maths.outputs['Value'], bsdf.inputs['Roughness'])

	pass


class UNIGINETOOLS_OT_CreateMaterialGeneric(bpy.types.Operator):
	bl_label = "Create generic"
	bl_idname = "uniginetools.creatematerialgeneric"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		CreateMaterialGeneric(self, context)

		material_name = bpy.context.active_object.active_material.name
		message = "{} material created".format(material_name)
		self.report({'INFO'}, message)

		return {'FINISHED'}


class UNIGINETOOLS_CreateMaterials(bpy.types.Menu):
	bl_label = "Create materials"
	bl_idname = "UNIGINETOOLS_MT_create_materials"

	def draw(self, context):
		layout = self.layout
		layout.operator(UNIGINETOOLS_OT_CreateMaterialGeneric.bl_idname,
			text=UNIGINETOOLS_OT_CreateMaterialGeneric.bl_label)

# -----------------------------------------------------------------------------------------
# Objects.
# -----------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------
# Nodes.
# -----------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------
# Register/Unregister.
# -----------------------------------------------------------------------------------------
classes = (
	UNIGINETOOLS_OT_CreateMaterialGeneric,
	UNIGINETOOLS_CreateMaterials,
)

def materials_menu(self, context):
	layout = self.layout
	layout.separator()
	layout.label(text="Unigine tools")
	# layout.separator()
	layout.menu(UNIGINETOOLS_CreateMaterials.bl_idname, icon="MATERIAL")
	layout.separator()

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)
	
	bpy.types.MATERIAL_MT_context_menu.append(materials_menu)

	pass


def unregister():
	from bpy.utils import unregister_class
	for cls in classes:
		unregister_class(cls)
	
	bpy.types.MATERIAL_MT_context_menu.remove(materials_menu)

	pass


# if __name__ == "__main__":
# 	register()
