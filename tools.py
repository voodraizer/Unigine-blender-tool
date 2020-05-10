import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


# -----------------------------------------------------------------------------------------
# Utils.
# -----------------------------------------------------------------------------------------
def GetDefaultTexFolder():
	import os
	import sys
	file_path = os.path.dirname(os.path.abspath(__file__))
	textures_path = os.path.join(file_path, "default_tex") + "\\"

	return textures_path

# -----------------------------------------------------------------------------------------
# Materials from xml.
# -----------------------------------------------------------------------------------------
import sys
sys.path.append("c:/GITs/MigrateCryAssetsToUnigine/")

import def_globals


def GetXmlMat(ref_path):
	import os
	import xml.etree.ElementTree as ET

	materials = []

	mat_tree = ET.parse(def_globals.MATERIALS_XML)
	mat_root = mat_tree.getroot()

	for mat in mat_root.iter('Material'):
		path_mat = def_globals.xml_get(mat, "mtl_file").lower().replace("/", "\\")
		if (ref_path == path_mat):
			# print("Found mat: " + xml_get(mat, "mtl_file"))
			materials.append(mat)

	return materials


def AssignTexture(node, tex_type, tex_path):
	import os

	def UpdateTextureNode(texture_path):
		texture_name = os.path.split(texture_path)[1]

		if (os.path.exists(texture_path)):
			if (bpy.data.images.get(texture_name) == None): bpy.data.images.load(filepath = texture_path)
			
			node.image = bpy.data.images.get(texture_name)
			node.image.update()

		pass

	texture_path = os.path.join(def_globals.DESTINATION_ASSETS_PATH, tex_path)

	if (node.name == "Albedo" and tex_type == "Diffuse"):
		UpdateTextureNode(texture_path)
	
	if (node.name == "Normals" and tex_type == "Bumpmap"):
		UpdateTextureNode(texture_path)

	if (node.name == "Shading" and tex_type == "Diffuse"):
		# found shading by albedo texture name.
		texture_path = texture_path.replace("_alb", "_sh")
		UpdateTextureNode(texture_path)
		



def AddTexturesToMaterials(mat, textures):
	print("------------------------------------------------")
	mat_nodes = mat.node_tree.nodes

	for n in mat_nodes:
		for tex in textures:
			AssignTexture(n, tex[0], tex[1])

	pass


def CreateMaterialsFromXml(self, context, materials):

	PROJECT_DIR = def_globals.DESTINATION_ASSETS_PATH

	import os
	import xml.etree.ElementTree as ET

	for mat in materials:
		mat_name = def_globals.xml_get(mat, "name")
		textures = []

		for tex in mat.iter('Texture'):
			texture_path_orig = def_globals.xml_get(tex, "file")
			
			texture_path = os.path.split(texture_path_orig)[0]
			texture_name = os.path.split(texture_path_orig)[1]
			
			texture_name = texture_name.replace(".tif", "").replace(".tga", "")
			texture_name = def_globals.convert_suffixes_to_unigine(texture_name)
			texture_name = texture_name + ".tga"

			tex = [def_globals.xml_get(tex, "map"), texture_path + "\\" + texture_name]
			textures.append(tex)
		
		new_mat = CreateMaterialGeneric(self, context, mat_name)
		AddTexturesToMaterials(new_mat, textures)

	pass


def RecreateMaterialFromXml(self, context):
	'''

	'''
	import os
	import xml.etree.ElementTree as ET

	active_obj = bpy.context.active_object
	mat = active_obj.active_material

	blend_folder = os.path.dirname(bpy.data.filepath)

	materials = []

	tree = ET.parse(def_globals.MODELS_XML)
	root = tree.getroot()

	for mod in root.iter('Model'):
		path_model = def_globals.xml_get(mod, "path")
		path_mat = def_globals.xml_get(mod, "mtl_path").lower().replace("/", "\\")

		path = os.path.split(path_model)[0]
		name = os.path.split(path_model)[1]

		if (not path in blend_folder): continue
		
		for collection in bpy.data.collections:
			for obj in collection.objects:
				if (active_obj != obj): continue
				
				for obj in collection.objects:
					if (obj.name.startswith("_export_")): # find exporter helper
						materials = GetXmlMat(path_mat)
						break

	# create materials.
	CreateMaterialsFromXml(self, context, materials)

	pass


class UNIGINETOOLS_OT_RecreateMaterialFromXml(bpy.types.Operator):
	bl_label = "Recreate material from xml"
	bl_idname = "uniginetools.recreate_material_from_xml"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		RecreateMaterialFromXml(self, context)
		
		self.report({'INFO'}, "recreated")

		return {'FINISHED'}


# -----------------------------------------------------------------------------------------
# Materials.
# -----------------------------------------------------------------------------------------
def CreateMaterialGeneric(self, context, name = ""):
	'''
	Find material by name or create.
	Create material node tree.
	'''

	import os

	textures_path = GetDefaultTexFolder()

	obj = bpy.context.active_object
	
	mat = None
	if (name == ""):
		mat = obj.active_material
	else:
		mat = bpy.data.materials.get(name)	

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
	UNIGINETOOLS_OT_RecreateMaterialFromXml,
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
