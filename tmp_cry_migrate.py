import bpy

import tools

import sys
sys.path.append("c:/GITs/MigrateCryAssetsToUnigine/")

import def_globals


# -----------------------------------------------------------------------------------------
# Materials from xml.
# -----------------------------------------------------------------------------------------

def GetBlenderFileFolder():
	import os

	blend_folder = os.path.dirname(bpy.data.filepath)
	blend_folder = blend_folder[blend_folder.find("models"):]

	return blend_folder.lower()


def GetXmlMat(ref_path):
	import os
	import xml.etree.ElementTree as ET

	materials = {}

	mat_tree = ET.parse(def_globals.MATERIALS_XML)
	mat_root = mat_tree.getroot()

	blend_folder = GetBlenderFileFolder()

	for mat in mat_root.iter('Material'):
		path_mat = def_globals.xml_get(mat, "mtl_file").lower().replace("/", "\\")

		if (not blend_folder in path_mat): continue
		if (path_mat in materials.keys()): continue

		if (ref_path in path_mat):
			print("Found mat: " + path_mat)
			materials[path_mat] =  mat
	
	# print("Keys: " + str(list(materials.keys())))

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
	mat_nodes = mat.node_tree.nodes

	for n in mat_nodes:
		for tex in textures:
			AssignTexture(n, tex[0], tex[1])

	pass



def CreateMaterialsFromXml(self, context, materials):
	import os
	import xml.etree.ElementTree as ET

	for path, mat in materials.items():
		mat_name = def_globals.xml_get(mat, "name")

		mat_name = os.path.split(path)[1].replace(".mtl", "")
		# print("Mat name: " + str(mat_name))
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

	tree = ET.parse(def_globals.MODELS_XML)
	root = tree.getroot()

	print("====================== FOUND MATS ======================")
	print("========================================================\n")

	for mod in root.iter('Model'):
		path_model = def_globals.xml_get(mod, "path")
		path_mat = def_globals.xml_get(mod, "mtl_path").lower().replace("/", "\\")

		path = os.path.split(path_model)[0]
		name = os.path.split(path_model)[1]

		if (not path.lower() in blend_folder): continue

		if (path_mat.startswith(".\\")):
			path_mat = path_mat[2:]

		found_mats = GetXmlMat(path_mat)
		materials = {**materials, **found_mats}


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