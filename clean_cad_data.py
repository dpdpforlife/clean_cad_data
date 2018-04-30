# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
#  (c) 2018 Dan Pool (dpdp) parts based on work by meta-androcto AF: Materials Specials which features parts based on work by Saidenka, Materials Utils by MichaleW Materials Conversion: Silvio Falcinelli#
import bpy

bl_info = {
    "name": "CleanCadData",
    "author": "Dan Pool (dpdp)",
    "version": (0,0,1),
    "blender": (2, 79,0),
    "description": "Welds and cleans up then merges material base names for meshes imported from some solid modellers",
    "location": "View3D > Object > Clean Cad Data",    
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"}

class CleanCadData(bpy.types.Operator):
    """Weld and clean up imported cad meshes"""
    bl_idname = "object.clean_cad_data"
    bl_label = "Clean Cad Data"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (	(len(context.selected_objects) > 0) 
            and (context.mode == 'OBJECT')	)	
	
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            print(obj.name)
            bpy.context.scene.objects.active = obj
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.tris_convert_to_quads()
            bpy.ops.mesh.dissolve_limited()
            bpy.ops.object.editmode_toggle()
            bpy.context.object.data.auto_smooth_angle = 0.15708
        for ob in bpy.context.scene.objects:
            for slot in ob.material_slots:
                self.fixup_slot(slot)
        return {'FINISHED'}
	#Start Meta Androcto code as included in his addon
	#AF: Materials Specials - http://wiki.blender.org/index.php/Extensions:2.6
    def split_name(self, material):
        name = material.name
        
        if not '.' in name:
            return name, None
        
        base, suffix = name.rsplit('.', 1)
        try:
            num = int(suffix, 10)
        except ValueError:
            # Not a numeric suffix
            return name, None
        
        return base, suffix
    
    def fixup_slot(self, slot):
        if not slot.material:
            return
        
        base, suffix = self.split_name(slot.material)
        if suffix is None:
            return

        try:
            base_mat = bpy.data.materials[base]
        except KeyError:
            print('Base material %r not found' % base)
            return
        
        slot.material = base_mat
    #End Meta Androcto code as included in his addon

def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

def menu_func(self, context):
	#self.layout.separator()
	self.layout.operator(CleanCadData.bl_idname)
	
if __name__ == "__main__":
    register()