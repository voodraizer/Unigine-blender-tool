import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


TEX_NODE_COLOR = (0.272209, 0.608, 0.378043)
MAT_GROUP_NAMES = ['MG_Generic', 'MG_VertexBlend', 'VB_Blend_coefficient']

# -----------------------------------------------------------------------------------------
# Utils.
# -----------------------------------------------------------------------------------------
def GetDefaultResFolder():
	'''
	Get default textures for addon.
	'''
	import os
	import sys
	file_path = os.path.dirname(os.path.abspath(__file__))
	textures_path = os.path.join(file_path, "default_resources") + "\\"

	return textures_path


def CreateTextureNode(mat_nodes, name = "Texture"):
	'''

	'''
	texture = mat_nodes.new('ShaderNodeTexImage')
	texture.name = name
	texture.location = (0, 0)
	texture.use_custom_color = True
	texture.color = TEX_NODE_COLOR

	return texture


def LoadDefaultTexture(node, tex_type):
	'''

	'''
	import os

	texture_name = ""
	if (tex_type == "Albedo"): texture_name = "default_alb.tga"
	if (tex_type == "Shading"): texture_name = "default_sh.tga"
	if (tex_type == "Normals"): texture_name = "default_n.tga"

	tex_path = GetDefaultResFolder() + texture_name
	tex_name = os.path.split(tex_path)[1]
	if (bpy.data.images.get(tex_name) == None):
		bpy.data.images.load(filepath=tex_path)

	node.image = bpy.data.images.get(tex_name)

	if (tex_type == "Shading"): node.image.colorspace_settings.name = 'Linear'
	if (tex_type == "Normals"): node.image.colorspace_settings.name = 'Non-Color'


def GetPathFromImage(image, rel_blend_folder):
	import os

	image_path = image.filepath.replace("/", "\\").lower()
	
	if ("default_alb.tga" in image_path or "default_sh.tga" in image_path or "default_n.tga" in image_path):
		return None
	
	import def_globals
	proj_path = def_globals.ART_ASSETS_PATH.replace("/", "\\").lower()
	
	if (proj_path in image_path):
		image_path = image_path[len(proj_path):]
		return image_path

	image_path = image_path.replace("..", "")
	for ch in image_path:
		if (ch == "\\"):
			image_path = image_path[1:]
		else:
			break
		
	print("\n Image path ==>   " + image_path)
	# if (image_path.startswith("\\..\..\..\Textures")):
	# if (".." in image_path):
	# 	image_path = (image_path[image_path.find("textures"):]).replace("\\", "/")
	# if (image_path.startswith("//")):
	# 	image_path = os.path.join(rel_blend_folder, image_path[2:]).replace("\\", "/")

	# print("\n ==>   " + image_path)
	# print(" ==>   " + proj_path)
	
	return image_path


# -----------------------------------------------------------------------------------------
# Create unigine materials.
# -----------------------------------------------------------------------------------------
def CreateUnigineMaterialHeader(xml_root, mat_file_path, mat_name, mat_base):
	import xml.etree.ElementTree as ET
	import uuid
	import hashlib

	# <?xml version="1.0" encoding="utf-8"?>

	# xml_root = ET.Element('material')
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
	xml_root.set('base_material', mat_base)
	pass


def CreateUnigineMaterialTexture(xml_root, image_node, type = "albedo", rel_blend_folder = ""):
	import xml.etree.ElementTree as ET

	xml_child = ET.SubElement(xml_root, 'texture')
	xml_child.set('name', type)
	if (not image_node is None):
		image_path = GetPathFromImage(image_node.image, rel_blend_folder)
		if (image_path):
			xml_child.text = image_path
		else:
			xml_child.text = "guid://5219d6ddb5dbd1520e843a369ad2b64326bb24e2"	# white texture from core/textures/common/

			if ("albedo" in type):
				xml_child.text = "Textures/cry_missing/pink_alb.tga"
			if ("shading" in type):
				xml_child.text = "Textures/cry_missing/normal_sh.tga"
			if ("normal" in type):
				# xml_child.text = "guid://692dbb7d56d633e22551bd47f4d92cd2d498270d" # default normal
				xml_child.text = "Textures/cry_missing/normal_n.tga"
	pass


def CreateunigineMaterialParameter(xml_root, param_name, param_value):
	import xml.etree.ElementTree as ET

	xml_child = ET.SubElement(xml_root, 'parameter')
	xml_child.text = param_value
	xml_child.set('name', param_name)
	xml_child.set('expression', "0")


def CreateunigineMaterialOptions(xml_root, param_name, param_value):
	import xml.etree.ElementTree as ET

	xml_child = ET.SubElement(xml_root, 'options')
	xml_child.set(param_name, param_value)


def CreateunigineMaterialState(xml_root, param_name, param_value):
	import xml.etree.ElementTree as ET

	xml_child = ET.SubElement(xml_root, 'state')
	xml_child.set('name', param_name)
	xml_child.text = param_value


def CreateUnigineXmlMaterialGeneric(mat, mat_file_path, mat_name, rel_blend_folder):
	'''
	Create unigine material and link existing textures.
	'''

	import xml.etree.ElementTree as ET
	import os

	xml_root = ET.Element('material')
	
	CreateUnigineMaterialHeader(xml_root, mat_file_path, mat_name, "mesh_base")
	
	# textures.
	
	# albedo.
	image_node = mat.node_tree.nodes.get("Albedo")
	CreateUnigineMaterialTexture(xml_root, image_node, "albedo", rel_blend_folder)

	# shading.
	image_node = mat.node_tree.nodes.get("Shading")
	CreateUnigineMaterialTexture(xml_root, image_node, "shading", rel_blend_folder)

	# normals.
	image_node = mat.node_tree.nodes.get("Normals")
	CreateUnigineMaterialTexture(xml_root, image_node, "normal", rel_blend_folder)
	

	# parameters.
	# CreateunigineMaterialParameter(xml_root, "metalness", "1")
	# CreateunigineMaterialParameter(xml_root, "specular_color", "1 1 1 1")
	# CreateunigineMaterialParameter(xml_root, "gloss", "1")

	albedo = mat.node_tree.nodes.get("Albedo")
	if (not albedo is None and albedo.outputs["Alpha"].links):
		CreateunigineMaterialOptions(xml_root, "transparent", "1")
		CreateunigineMaterialParameter(xml_root, "transparent", "1.3")


	import def_globals
	print("==================================================")
	print(def_globals.xml_prettify(xml_root))
	print("==================================================")

	# save mat.
	print("Saved: " + mat_file_path)
	tree = ET.ElementTree(xml_root)
	tree.write(mat_file_path)

	pass


def CreateUnigineXmlMaterialVertexBlend(mat, mat_file_path, mat_name, rel_blend_folder):
	'''
	Create unigine material and link existing textures.
	'''
	import xml.etree.ElementTree as ET
	import os

	xml_root = ET.Element('material')
	
	CreateUnigineMaterialHeader(xml_root, mat_file_path, mat_name, "base_mesh_vblend_4")

	# states.
	CreateunigineMaterialState(xml_root, "vertex_blend_enable", "1")
	CreateunigineMaterialState(xml_root, "vertex_color_blend_r", "1")
	CreateunigineMaterialState(xml_root, "vertex_color_blend_g", "1")

	# textures.

	# set 1.
	image_node = mat.node_tree.nodes.get("Albedo")
	CreateUnigineMaterialTexture(xml_root, image_node, "albedo", rel_blend_folder)
	image_node = mat.node_tree.nodes.get("Shading")
	CreateUnigineMaterialTexture(xml_root, image_node, "shading", rel_blend_folder)
	image_node = mat.node_tree.nodes.get("Normals")
	CreateUnigineMaterialTexture(xml_root, image_node, "normal", rel_blend_folder)
	
	# set 2.
	image_node = mat.node_tree.nodes.get("Albedo 2")
	CreateUnigineMaterialTexture(xml_root, image_node, "albedo_blend_r", rel_blend_folder)
	image_node = mat.node_tree.nodes.get("Shading 2")
	CreateUnigineMaterialTexture(xml_root, image_node, "shading_blend_r", rel_blend_folder)
	image_node = mat.node_tree.nodes.get("Normals 2")
	CreateUnigineMaterialTexture(xml_root, image_node, "normal_blend_r", rel_blend_folder)

	# set 3.
	image_node = mat.node_tree.nodes.get("Albedo 3")
	CreateUnigineMaterialTexture(xml_root, image_node, "albedo_blend_g", rel_blend_folder)
	image_node = mat.node_tree.nodes.get("Shading 3")
	CreateUnigineMaterialTexture(xml_root, image_node, "shading_blend_g", rel_blend_folder)
	image_node = mat.node_tree.nodes.get("Normals 3")
	CreateUnigineMaterialTexture(xml_root, image_node, "normal_blend_g", rel_blend_folder)

	# parameters.
	CreateunigineMaterialParameter(xml_root, "blend_factor_r", "1")
	CreateunigineMaterialParameter(xml_root, "blend_falloff_r", "1")
	CreateunigineMaterialParameter(xml_root, "blend_alpha_r", "1")
	CreateunigineMaterialParameter(xml_root, "blend_normals_r", "1")

	import def_globals
	print("==================================================")
	print(def_globals.xml_prettify(xml_root))
	print("==================================================")

	# save mat.
	print("Saved: " + mat_file_path)
	tree = ET.ElementTree(xml_root)
	tree.write(mat_file_path)

	pass


def CreateUnigineMaterials(self, context, mat = None):
	'''

	'''
	import os

	import def_globals

	# paths
	blend_folder = os.path.dirname(bpy.data.filepath)
	rel_blend_folder = blend_folder[blend_folder.find("models"):]
	full_path = os.path.normpath(os.path.join(def_globals.DESTINATION_ASSETS_PATH, rel_blend_folder)).replace("\\", "/")
	full_mat_path = os.path.normpath(os.path.join(full_path, "materials"))
	mat_file_path = full_mat_path + "\\" + mat.name + ".mat"

	# TODO
	# Если материал уже существует просто апдейтить пути к текстурам

	for node in mat.node_tree.nodes:
		if (node.type != 'GROUP'): continue
		if (node.node_tree.name == "MG_Generic"):
			CreateUnigineXmlMaterialGeneric(mat, mat_file_path, mat.name, rel_blend_folder)
			break
		if (node.node_tree.name == "MG_VertexBlend"):
			CreateUnigineXmlMaterialVertexBlend(mat, mat_file_path, mat.name, rel_blend_folder)
			break

	pass


class UNIGINETOOLS_OT_CreateUnigineMaterial(bpy.types.Operator):
	bl_label = "Create Unigine material"
	bl_idname = "uniginetools.create_unigine_material"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		
		for obj in bpy.context.selected_objects:
			for slots in obj.material_slots:
				mat = slots.material
				if (mat is None): continue
				CreateUnigineMaterials(self, context, mat = mat)

		# material_name = bpy.context.active_object.active_material.name
		# message = "{} material created".format(material_name)
		# self.report({'INFO'}, message)

		return {'FINISHED'}


# -----------------------------------------------------------------------------------------
# Create blender materials.
# -----------------------------------------------------------------------------------------
def CreateMaterialGeneric(self, context, obj = None, mat_name = ""):
	'''
	
	'''
	import os

	mat = None
	
	if (not obj is None): mat = obj.active_material
	
	if (not mat_name == ""):
		mat = bpy.data.materials.get(mat_name)
		if (mat is None):
			# create new material
			mat = bpy.data.materials.new(name = mat_name)


	if (mat is None): return None
	
	ImportMaterialNodeGroups()

	mat.use_nodes = True

	# delete all nodes
	for m in mat.node_tree.nodes:
		mat.node_tree.nodes.remove(m)
		

	mat_nodes = mat.node_tree.nodes
	mat_links = mat.node_tree.links

	# generate new node tree
	output = mat_nodes.new('ShaderNodeOutputMaterial')
	output.name = "Output"
	output.location = (305, 320)

	# group
	node_group = mat_nodes.new('ShaderNodeGroup')
	node_group.location = (-20, 296)
	node_group.use_custom_color = True
	node_group.color = (0.38, 0.54, 0.6)
	node_group.width = 200
	node_group.node_tree = bpy.data.node_groups['MG_Generic']

	mat_links.new(node_group.outputs['BSDF'], output.inputs['Surface'])
	

	# albedo
	texture = CreateTextureNode(mat_nodes, "Albedo")
	texture.location = (-585, 550)
	LoadDefaultTexture(texture, "Albedo")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Albedo'])

	# shading
	texture = CreateTextureNode(mat_nodes, "Shading")
	texture.location = (-585, 251)
	LoadDefaultTexture(texture, "Shading")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Shading'])

	# normals
	texture = CreateTextureNode(mat_nodes, "Normals")
	texture.location = (-585, -47)
	LoadDefaultTexture(texture, "Normals")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Normals'])


	return mat


def ImportMaterialNodeGroups():
	"""

	"""

	old_groups = []
	old_group_suffix = "_old_group"

	# rename and store old groups
	for gr_n in MAT_GROUP_NAMES:
		if (not bpy.data.node_groups.get(gr_n) is None):
			gr = bpy.data.node_groups.get(gr_n)
			gr.name = gr_n + old_group_suffix
			gr.use_fake_user = False
			old_groups.append(gr)

	import os

	filepath = os.path.join(GetDefaultResFolder(), 'node_library.blend')

	#  load new groups
	with bpy.data.libraries.load(filepath) as (data_from, data_to):
		data_to.node_groups = data_from.node_groups

	for node_group in data_to.node_groups:
		# log.debug('Importing material node group: %s', node_group.name)
		node_group.use_fake_user = True

	# replace old nodes from materials
	for mat in bpy.data.materials:
		if (mat.use_nodes):
			for node in mat.node_tree.nodes:
				if (node.type == 'GROUP'):
					orig_node_group = node.node_tree.name[:node.node_tree.name.find(old_group_suffix)]
					if (not bpy.data.node_groups.get(orig_node_group) is None):
						node.node_tree = bpy.data.node_groups.get(orig_node_group)
					
	
	# delete old groups
	for gr in old_groups:
		bpy.data.node_groups.remove(gr)

	pass


def CreateMaterialVertexBlend(self, context, obj = None, mat_name = ""):
	'''

	'''
	mat = None
	
	if (not obj is None): mat = obj.active_material
	
	if (not mat_name == ""):
		mat = bpy.data.materials.get(mat_name)
		if (mat is None):
			# create new material
			mat = bpy.data.materials.new(name = mat_name)


	if (mat is None): return None

	ImportMaterialNodeGroups()

	mat.use_nodes = True

	mat_nodes = mat.node_tree.nodes
	mat_links = mat.node_tree.links

	# delete all nodes
	for n in mat_nodes:
		mat_nodes.remove(n)

	output = mat_nodes.new('ShaderNodeOutputMaterial')
	output.location = (300, 300)

	# Material group node (The datablock is not yet assigned)
	node_group = mat_nodes.new('ShaderNodeGroup')
	node_group.location = (-205, 300)
	node_group.use_custom_color = True
	node_group.color = (0.38, 0.54, 0.6)
	node_group.width = 300
	node_group.node_tree = bpy.data.node_groups['MG_VertexBlend']

	mat_links.new(node_group.outputs['BSDF'], output.inputs['Surface'])

	vert_color = mat_nodes.new("ShaderNodeVertexColor")
	vert_color.location = (-490, -225)

	mat_links.new(vert_color.outputs['Color'], node_group.inputs['Vertex color'])

	# Textures mask
	texture = CreateTextureNode(mat_nodes, "Mask")
	texture.location = (-1200, -135)
	
	mat_links.new(texture.outputs['Color'], node_group.inputs['Blend mask'])

	# Textures 1
	texture = CreateTextureNode(mat_nodes, "Albedo")
	texture.location = (-1200, 770)
	LoadDefaultTexture(texture, "Albedo")
	LoadDefaultTexture(texture, "Albedo")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Albedo'])

	texture = CreateTextureNode(mat_nodes, "Shading")
	texture.location = (-1470, 770)
	LoadDefaultTexture(texture, "Shading")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Shading'])

	texture = CreateTextureNode(mat_nodes, "Normals")
	texture.location = (-1740, 770)
	LoadDefaultTexture(texture, "Normals")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Normals'])

	# Textures 2
	texture = CreateTextureNode(mat_nodes, "Albedo 2")
	texture.location = (-1200, 470)
	LoadDefaultTexture(texture, "Albedo")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Albedo 2'])

	texture = CreateTextureNode(mat_nodes, "Shading 2")
	texture.location = (-1470, 470)
	LoadDefaultTexture(texture, "Shading")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Shading 2'])

	texture = CreateTextureNode(mat_nodes, "Normals 2")
	texture.location = (-1740, 470)
	LoadDefaultTexture(texture, "Normals")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Normals 2'])

	# Textures 3
	texture = CreateTextureNode(mat_nodes, "Albedo 3")
	texture.location = (-1200, 170)
	LoadDefaultTexture(texture, "Albedo")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Albedo 3'])

	texture = CreateTextureNode(mat_nodes, "Shading 3")
	texture.location = (-1470, 170)
	LoadDefaultTexture(texture, "Shading")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Shading 3'])

	texture = CreateTextureNode(mat_nodes, "Normals 3")
	texture.location = (-1740, 170)
	LoadDefaultTexture(texture, "Normals")
	mat_links.new(texture.outputs['Color'], node_group.inputs['Normals 3'])

	return mat


def Debug_PrintMaterialNodes(self, context):
	obj = bpy.context.active_object
	mat = obj.active_material

	mat_nodes = mat.node_tree.nodes
	mat_links = mat.node_tree.links

	for m_n in mat_nodes:
		print("============================================")
		if (m_n.type == "TEX_IMAGE"):
			print("Type: " + m_n.type + " Name: " + m_n.image.name + " Pos: " + str(m_n.location))
		else:
			print("Type: " + m_n.type + " Name: " + m_n.name + " Pos: " + str(m_n.location))


class UNIGINETOOLS_OT_CreateMaterialGeneric(bpy.types.Operator):
	bl_label = "Create generic"
	bl_idname = "uniginetools.creatematerialgeneric"
	bl_options = {'REGISTER', 'UNDO'}

	@staticmethod
	def oops(self, context):
		self.layout.label(text = "Failed to create material!")

	def execute(self, context):
		
		obj = bpy.context.active_object
		if (not obj is None): mat_name = obj.active_material

		mat = CreateMaterialGeneric(self, context, obj)

		if (not mat is None):
			message = "{} material created".format(mat.name)
			self.report({'INFO'}, message)
		else:
			bpy.context.window_manager.popup_menu(UNIGINETOOLS_OT_CreateMaterialGeneric.oops, title="Error", icon='ERROR')

		return {'FINISHED'}


class UNIGINETOOLS_OT_CreateMaterialVertexBlend(bpy.types.Operator):
	bl_label = "Create vertex blend"
	bl_idname = "uniginetools.create_material_vertex_blend"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		
		obj = bpy.context.active_object
		if (not obj is None): mat_name = obj.active_material

		mat = CreateMaterialVertexBlend(self, context, obj)

		if (not mat is None):
			message = "{} material created".format(mat.name)
			self.report({'INFO'}, message)
		else:
			bpy.context.window_manager.popup_menu(UNIGINETOOLS_OT_CreateMaterialGeneric.oops, title="Error", icon='ERROR')

		return {'FINISHED'}


class UNIGINETOOLS_OT_DebugPrintMaterial(bpy.types.Operator):
	bl_label = "Debug print material nodes"
	bl_idname = "uniginetools.debug_print_material"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		Debug_PrintMaterialNodes(self, context)

		material_name = bpy.context.active_object.active_material.name
		message = "{} debug printed".format(material_name)
		self.report({'INFO'}, message)

		return {'FINISHED'}


class UNIGINETOOLS_CreateMaterials(bpy.types.Menu):
	bl_label = "Create materials"
	bl_idname = "UNIGINETOOLS_MT_create_materials"

	def draw(self, context):
		layout = self.layout
		layout.operator(UNIGINETOOLS_OT_CreateMaterialGeneric.bl_idname,
			text=UNIGINETOOLS_OT_CreateMaterialGeneric.bl_label)
		layout.operator(UNIGINETOOLS_OT_CreateMaterialVertexBlend.bl_idname,
			text=UNIGINETOOLS_OT_CreateMaterialVertexBlend.bl_label)

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
	blend_path = GetDefaultResFolder() + "default_workspaces.blend"

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
	UNIGINETOOLS_OT_CreateMaterialVertexBlend,
	UNIGINETOOLS_CreateMaterials,
	UNIGINETOOLS_OT_DebugPrintMaterial,
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
