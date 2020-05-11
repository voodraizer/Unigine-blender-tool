import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

# -----------------------------------------------------------------------------------------
# Utils.
# -----------------------------------------------------------------------------------------
def GetDefaultTexFolder():
	'''
	Get default textures for addon.
	'''
	import os
	import sys
	file_path = os.path.dirname(os.path.abspath(__file__))
	textures_path = os.path.join(file_path, "default_tex") + "\\"

	return textures_path


# -----------------------------------------------------------------------------------------
# Create unigine materials.
# -----------------------------------------------------------------------------------------
def CreateUnigineXmlMaterial(mat, mat_file_path, mat_name, rel_blend_folder):
	'''
	Create unigine material and link existing textures.
	'''

	def GetPathFromImage(image):
		image_path = image.filepath
		
		if ("default_n.tga" in image_path or "default_sh.tga" in image_path or "default_n.tga" in image_path):
			return None

		if (image_path.startswith("//..\..\..\Textures")):
			image_path = (image_path[image_path.find("Textures"):]).replace("\\", "/")
		if (image_path.startswith("//")):
			image_path = os.path.join(rel_blend_folder, image_path[2:]).replace("\\", "/")
		
		return image_path

	import xml.etree.ElementTree as ET
	import os
	import uuid
	import hashlib

	# <?xml version="1.0" encoding="utf-8"?>

	xml_root = ET.Element('material')
	xml_root.set('version', "2.11.0.0")
	xml_root.set('name', mat_name)

	mat_rel_path = mat_file_path[mat_file_path.find("models"):]
	unigine_uuid = hashlib.sha1(mat_rel_path.encode('utf-8'))
	xml_root.set('guid', unigine_uuid.hexdigest())
	# print("==================================================")
	# print(unigine_uuid.hexdigest())
	# print(unigine_mat_path)
	# print("==================================================")

	# material base type.
	# if (mat_shader == "Illum"):
	xml_root.set('base_material', "mesh_base")
	
	# textures.
	xml_child = ET.SubElement(xml_root, 'texture')
	xml_child.set('name', "albedo")
	albedo = mat.node_tree.nodes.get("Albedo")
	if (not albedo is None):
		# albedo
		image_path = GetPathFromImage(albedo.image)
		if (image_path):
			xml_child.text = image_path
		else:
			# xml_child.text = "guid://5219d6ddb5dbd1520e843a369ad2b64326bb24e2"	# white texture from core/textures/common/
			xml_child.text = "Textures/cry_missing/pink_alb.tga"


	xml_child = ET.SubElement(xml_root, 'texture')
	xml_child.set('name', "normal")
	normals = mat.node_tree.nodes.get("Normals")
	if (not normals is None):
		# normal map
		image_path = GetPathFromImage(normals.image)
		if (image_path):
			xml_child.text = image_path
		else:
			# xml_child.text = "guid://692dbb7d56d633e22551bd47f4d92cd2d498270d" # default normal
			xml_child.text = "Textures/cry_missing/normal_n.tga"

	
	xml_child = ET.SubElement(xml_root, 'texture')
	xml_child.set('name', "shading")
	shading = mat.node_tree.nodes.get("Shading")
	if (not shading is None):
		# shading map
		image_path = GetPathFromImage(shading.image)
		if (image_path):
			xml_child.text = image_path
		else:
			xml_child.text = "Textures/cry_missing/normal_sh.tga"
	

	# Parameters.
	xml_child = ET.SubElement(xml_root, 'parameter')
	xml_child.text = "1"
	xml_child.set('name', "metalness")
	xml_child.set('expression', "0")


	xml_child = ET.SubElement(xml_root, 'parameter')
	xml_child.text = "1 1 1 1"
	xml_child.set('name', "specular_color")
	xml_child.set('expression', "0")


	xml_child = ET.SubElement(xml_root, 'parameter')
	xml_child.text = "1"
	xml_child.set('name', "gloss")
	xml_child.set('expression', "0")

	if (not albedo is None and albedo.outputs["Alpha"].links):
		# Alpha test.
		xml_child = ET.SubElement(xml_root, 'options')
		xml_child.set('transparent', "1")
		
		xml_child = ET.SubElement(xml_root, 'parameter')
		xml_child.text = "1.3"
		xml_child.set('name', "transparent")
		xml_child.set('expression', "0")


	print("==================================================")
	print(def_globals.xml_prettify(xml_root))
	print("==================================================")

	# save mat.
	print("Saved: " + mat_file_path)
	tree = ET.ElementTree(xml_root)
	tree.write(mat_file_path)

	pass


def CreateUnigineMaterials(self, context):
	import os

	mat = bpy.context.active_object.active_material
	mat_name = mat.name

	# paths
	blend_folder = os.path.dirname(bpy.data.filepath)
	rel_blend_folder = blend_folder[blend_folder.find("models"):]
	full_path = os.path.normpath(os.path.join(def_globals.DESTINATION_ASSETS_PATH, rel_blend_folder)).replace("\\", "/")
	full_mat_path = os.path.normpath(os.path.join(full_path, "materials"))
	mat_file_path = full_mat_path + "\\" + mat_name + ".mat"

	# TODO
	# Если материал уже существует просто апдейтить пути к текстурам

	CreateUnigineXmlMaterial(mat, mat_file_path, mat_name, rel_blend_folder)
	pass


class UNIGINETOOLS_OT_CreateUnigineMaterial(bpy.types.Operator):
	bl_label = "Create Unigine material"
	bl_idname = "uniginetools.create_unigine_material"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		CreateUnigineMaterials(self, context)

		# material_name = bpy.context.active_object.active_material.name
		# message = "{} material created".format(material_name)
		# self.report({'INFO'}, message)

		return {'FINISHED'}

# -----------------------------------------------------------------------------------------
# Create blender materials.
# -----------------------------------------------------------------------------------------
def CreateMaterialGeneric(self, context, obj = None, name = ""):
	'''
	Find material by name or create.
	Create material node tree.
	'''

	import os

	textures_path = GetDefaultTexFolder()

	# obj = bpy.context.active_object
	
	mat = None
	if (name == ""):
		if (not obj is None): mat = obj.active_material
	else:
		mat = bpy.data.materials.get(name)	

	if (mat is None):
		# create new material
		if (name == ""):  name = "Material"
		mat = bpy.data.materials.new(name = name)
		# bpy.context.active_object.active_material = mat
	
	mat.use_nodes = True

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
	texture.location = (-1400, -600)
	texture.use_custom_color = True
	texture.color = (0.272209, 0.608, 0.378043)

	tex_path = textures_path + "default_n.tga"
	tex_name = os.path.split(tex_path)[1]
	if (bpy.data.images.get(tex_name) == None):
		bpy.data.images.load(filepath=tex_path)
	texture.image = bpy.data.images.get(tex_name)
	texture.image.colorspace_settings.name = 'Non-Color'

	sep = mat_nodes.new("ShaderNodeSeparateRGB")
	sep.location = (-1100, -650)
	sep.hide = True
	comb = mat_nodes.new("ShaderNodeCombineRGB")
	comb.location = (-800, -650)
	comb.hide = True
	maths = mat_nodes.new("ShaderNodeMath")
	maths.operation = 'SUBTRACT'
	maths.inputs[0].default_value = 1
	maths.location = (-950, -600)
	maths.hide = True
	mat_links.new(texture.outputs['Color'], sep.inputs['Image'])
	mat_links.new(sep.outputs['R'], comb.inputs[0])
	mat_links.new(sep.outputs['G'], maths.inputs[1])
	mat_links.new(sep.outputs['B'], comb.inputs[2])
	mat_links.new(maths.outputs['Value'], comb.inputs[1])


	normalmap = mat_nodes.new("ShaderNodeNormalMap")
	normalmap.location = (-600, -500)
	normalmap.uv_map = "UVMap"
	mat_links.new(comb.outputs['Image'], normalmap.inputs['Color'])
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

	return mat


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
# UI Layout.
# -----------------------------------------------------------------------------------------
def BlenderDefaultUI(self, context):

	# workspace
	blend_path = GetDefaultTexFolder() + "default_workspaces.blend"

	bpy.ops.workspace.append_activate(idname = "Animation", filepath = blend_path)

	workspaces = [ws for ws in bpy.data.workspaces if ws != context.workspace]
	bpy.data.batch_remove(ids=workspaces)

	if (bpy.data.workspaces.get("Animation") is None):
		bpy.ops.workspace.append_activate(idname = "Animation", filepath = blend_path)
	if (bpy.data.workspaces.get("Shading") is None):
		bpy.ops.workspace.append_activate(idname = "Shading", filepath = blend_path)
	if (bpy.data.workspaces.get("UV Editing") is None):
		bpy.ops.workspace.append_activate(idname = "UV Editing", filepath = blend_path)
	if (bpy.data.workspaces.get("Modeling") is None):
		bpy.ops.workspace.append_activate(idname = "Modeling", filepath = blend_path)
	if (bpy.data.workspaces.get("Layout") is None):
		bpy.ops.workspace.append_activate(idname = "Layout", filepath = blend_path)


	
	bpy.context.window.workspace = bpy.data.workspaces['Modeling']
	bpy.data.workspaces.update()


	for area in bpy.data.workspaces['Modeling'].screens[0].areas:
		if area.type == 'OUTLINER':
			for spaces in area.spaces:
				if spaces.type == 'OUTLINER':
					# outliner window settings
					area.spaces.active.show_restrict_column_select = True
					area.spaces.active.show_restrict_column_viewport = False
					area.spaces.active.show_restrict_column_hide = True
					
		if area.type == 'VIEW_3D':
			# viewport window settings
			area.spaces.active.show_gizmo_navigate = False
			area.spaces.active.overlay.show_floor = False
			area.spaces.active.overlay.show_axis_x = False
			area.spaces.active.overlay.show_axis_y = False
			area.spaces.active.overlay.show_axis_z = False


	# properties window settings
	# bpy.context.space_data.context = 'SCENE'

	pass


class UNIGINETOOLS_OT_CreateDefaultUILayout(bpy.types.Operator):
	bl_label = "Default ui layout."
	bl_idname = "uniginetools.create_default_ui_layout"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		BlenderDefaultUI(self, context)
		
		self.report({'INFO'}, "default layout")

		return {'FINISHED'}


# -----------------------------------------------------------------------------------------
# Register/Unregister.
# -----------------------------------------------------------------------------------------
classes = (
	UNIGINETOOLS_OT_CreateUnigineMaterial,
	UNIGINETOOLS_OT_CreateMaterialGeneric,
	UNIGINETOOLS_CreateMaterials,
	UNIGINETOOLS_OT_CreateDefaultUILayout,
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
