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

bl_info = {
    "name": "CleanCadData",
    "author": "Dan Pool (dpdp)",
    "version": (0,0,3),
    "blender": (2, 80,0),
    "description": "Cleans up meshes and materials imported from some solid modellers",
    "location": "View3D > Object > Clean Cad Data",    
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}


import bpy
import bmesh
from bpy.types import Operator, AddonPreferences
from bpy.props import FloatProperty


class CleanCadData(AddonPreferences):
    
    bl_idname = __name__

    anglelimit = FloatProperty(
            name="Angle Limit",
            description="Angle limit used for merging faces",
            default=0.00174533,
            subtype='ANGLE'
            )
    weldthreshold = FloatProperty(
            name="Weld Threshold",
            description="Threshold for welding vertices",
            default=0.0005,
            )
    smangle = FloatProperty(
            name="AutoSmooth Angle",
            description="Smoothing angle for the autosmoothed (is that a word?) mesh",
            default=0.15708,
            subtype='ANGLE'
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Set defaults for your CAD cleaning")
        layout.prop(self, "anglelimit")
        layout.prop(self, "weldthreshold")
        layout.prop(self, "smangle")


class OBJECT_OT_clean_cad_data(Operator):
    """Weld and clean up imported cad meshes"""
    bl_idname = "object.clean_cad_data"
    bl_label = "Clean Cad Data"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        user_preferences = context.preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        #remove split normals and set smoothing angle
        for obj in bpy.context.selected_objects:
            print(obj.name)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.context.object.data.auto_smooth_angle = addon_prefs.smangle
            bpy.ops.object.shade_smooth()
        
        #remove doubles and quadrify the mesh
        meshes = [o.data for o in context.selected_objects if o.type == 'MESH']

        bm = bmesh.new()

        for m in meshes:
            print(len(m.vertices))
            bm.from_mesh(m)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=addon_prefs.weldthreshold)
            bmesh.ops.dissolve_limit(bm, angle_limit=addon_prefs.anglelimit, verts=bm.verts, edges=bm.edges)
            bm.to_mesh(m)
            m.update()
            bm.clear()
        bm.free()
            
        #remove duplicate materials
        for ob in bpy.context.view_layer.objects:
            for slot in ob.material_slots:
                self.fixup_slot(slot)

        return {'FINISHED'}
    
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


# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_clean_cad_data)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    bpy.utils.register_class(CleanCadData)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_clean_cad_data)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(CleanCadData)
    
def menu_func(self, context):
	#self.layout.separator()
	self.layout.operator(OBJECT_OT_clean_cad_data.bl_idname)

if __name__ == "__main__":
    register()