import bpy

import tools

import sys
sys.path.append("c:/GITs/MigrateCryAssetsToUnigine/")


TMP_EXPORT_ASSETS_PATH = "d:/CRY_MIGRATE/___TMP_EXPORT/"
MODELS_XML = TMP_EXPORT_ASSETS_PATH + 'models_list.xml'
MATERIALS_XML = TMP_EXPORT_ASSETS_PATH + 'materials_list.xml'

def xml_get(node, attr):
	'''
	Get attribute from xml node.
	Return value or ''.
	'''

	res = node.get(attr)

	if (res == None): return ""
	return res

def convert_suffixes_to_unigine(filename):
	new_filename = ""

	if (filename.endswith("_diff")):
		base_filename = filename[:-5]
		new_filename = base_filename + "_alb"

	if (filename.endswith("_ddna")):
		base_filename = filename[:-5]
		new_filename = base_filename + "_n"
	
	if (filename.endswith("_spec")):
		base_filename = filename[:-5]
		new_filename = base_filename + "_s"

	if (filename.endswith("_mask")):
		base_filename = filename[:-5]
		new_filename = base_filename + "_mask"
	
	if (filename.endswith("_detail")):
		base_filename = filename[:-7]
		new_filename = base_filename + "_detail"
		pass
	
	if (filename.endswith("_sss")):
		base_filename = filename[:-4]
		new_filename = base_filename + "_sss"

	if (filename.endswith("_displ")):
		base_filename = filename[:-6]
		new_filename = base_filename + "_h"

	return new_filename

# -----------------------------------------------------------------------------------------
# Materials from xml.
# -----------------------------------------------------------------------------------------

def GetBlenderFileFolder():
	import os

	blend_folder = os.path.dirname(bpy.data.filepath)
	blend_folder = blend_folder[blend_folder.find("models"):]

	return blend_folder.lower()



def AssignTexture(node, tex_type, tex_path):
	import os

	def UpdateTextureNode(texture_path):
		texture_name = os.path.split(texture_path)[1]

		if (os.path.exists(texture_path)):
			if (bpy.data.images.get(texture_name) == None): bpy.data.images.load(filepath = texture_path)
			
			node.image = bpy.data.images.get(texture_name)
			node.image.update()

		pass

	texture_path = os.path.join(tools.DESTINATION_ASSETS_PATH, tex_path)

	if (node.name == "Albedo" and tex_type == "Diffuse"):
		UpdateTextureNode(texture_path)
	
	if (node.name == "Normals" and tex_type == "Bumpmap"):
		UpdateTextureNode(texture_path)

	if (node.name == "Shading" and tex_type == "Diffuse"):
		# found shading by albedo texture name.
		texture_path = texture_path.replace("_alb", "_sh")
		UpdateTextureNode(texture_path)
		


def AddTexturesToMaterials(mat, textures):
	mat_nodes = mat.node_tree.nodes

	for n in mat_nodes:
		for tex in textures:
			AssignTexture(n, tex[0], tex[1])

	pass



def CreateMaterialsFromXml(self, context, materials):
	import os
	import xml.etree.ElementTree as ET

	for path, mat in materials.items():
		mat_name = xml_get(mat, "name")

		mat_name = os.path.split(path)[1].replace(".mtl", "")
		# print("Mat name: " + str(mat_name))
		textures = []

		for tex in mat.iter('Texture'):
			texture_path_orig = xml_get(tex, "file")
			
			texture_path = os.path.split(texture_path_orig)[0]
			texture_name = os.path.split(texture_path_orig)[1]
			
			texture_name = texture_name.replace(".tif", "").replace(".tga", "")
			texture_name = convert_suffixes_to_unigine(texture_name)
			texture_name = texture_name + ".tga"

			tex = [xml_get(tex, "map"), texture_path + "\\" + texture_name]
			textures.append(tex)
		
		new_mat = tools.CreateMaterialGeneric(self, context, obj = None, name = mat_name)
		AddTexturesToMaterials(new_mat, textures)

	pass


def RecreateMaterialFromXml(self, context):
	'''

	'''
	import os
	import xml.etree.ElementTree as ET

	active_obj = bpy.context.active_object
	mat = active_obj.active_material

	blend_folder = GetBlenderFileFolder()

	materials = {}

	tree = ET.parse(MODELS_XML)
	root = tree.getroot()

	print("====================== FOUND MATS ======================")
	print("========================================================\n")

	materials = {}

	mat_tree = ET.parse(MATERIALS_XML)
	mat_root = mat_tree.getroot()

	for mat in mat_root.iter('Material'):
		path_mat = xml_get(mat, "mtl_file").lower().replace("/", "\\")

		if (not blend_folder in path_mat): continue
		if (path_mat in materials.keys()): continue

		print("Found mat: " + path_mat)
		materials[path_mat] =  mat


	print("\n========================================================")

	# create materials.
	CreateMaterialsFromXml(self, context, materials)

	pass


class UNIGINETOOLS_OT_RecreateMaterialFromXml(bpy.types.Operator):
	bl_label = "Recreate material from xml"
	bl_idname = "uniginetools.recreate_material_from_xml"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		RecreateMaterialFromXml(self, context)

		# try assign most matched material
		for obj in bpy.context.selected_objects:
			for mat in bpy.data.materials:
				if (mat.name.lower() in obj.name.lower()): obj.active_material = mat
		
		self.report({'INFO'}, "recreated")

		return {'FINISHED'}


# -----------------------------------------------------------------------------------------
# Register/Unregister.
# -----------------------------------------------------------------------------------------
classes = (
	UNIGINETOOLS_OT_RecreateMaterialFromXml,
)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)
	pass


def unregister():
	from bpy.utils import unregister_class
	for cls in classes:
		unregister_class(cls)
	pass