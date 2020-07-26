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


#Scriptname & version: Cardboy0's Softbody supporter for non-animated models - V.1.0  (I often forget to actually update this number so don't trust it)
#Author: Cardboy0 (https://twitter.com/cardboy0)
#Made for Blender 2.83



#################################
###########DESCRIPTION###########

#For a more detailed description or guide on how to use, visit the (NSFW) online manual: https://docs.google.com/document/d/1rpJIQqvXcGL9UN-JYzqRKVHk8xaMxgCKM0UYLyqDW_A/edit

#You can download the newest version of this scipt at https://github.com/Cardboy0/Softbody-supporter-for-non-animated-models , and older versions at https://github.com/Cardboy0/Softbody-supporter-for-non-animated-models/tree/older-versions .

#This is a script that will help people who want to use softbody simulations on their (non-animated!) models, for instance a humanoid in a specific pose. Mainly intended for belly-bulge fetish pornography. If you try to just use a softbody modifier on your model without this script you will soon realise that it does not work properly at all. There are things you have to do to fix that, and this script does exactly those things. It will create 3 new objects in a seperate collection, with one of those called "belly_SB". Only use that for any softbody baking; the resulting shape will be transfered to a copy of your original object. Do not delete any added objects or modifiers, since they need each other to work.


#################################
########QUICK-START GUIDE########
#1. Put your model into the desired position
#2. Give it a new Vertex Group, call it "SB belly". Select all vertices of the belly you want to deform and assign them with a weight of 0.7 . Do not assign any other vertices
#3. Give your model a Softbody modifier and hide it. It's position in the modifier stack doesn't matter.
#4. In the softbody properties, change the following:
#       Goal    : enabled
#               -> Vertex Group: "SB belly"
#       Edges   : enabled
#               -> Collision Face: enabled
#5. Head over to the "Scripting" Workspace inside your Blender project.
#6. In the text editor that's in the middle, open this script.
#7. Select your model.
#8. Save your file.
#9. In the text editor at the top right, press the "Run Script" button.
#10. Wait for the script to finish
#11. Three new objects will have been added to your scene:
#       a. A copy of your model with some additional modifiers. I don't wanna mess with your actual original model so I created a copy instead.
#       b. An object called "VWP reference object", showing only the belly of your model. Hide it but don't delete it.
#       c. "belly_SB". This is the object you should use for any actual softbody baking. It's shape will be transfered to the copy (a.).
#12. Add a new object to your scene (like a sphere), give it a collision modifier, set outer and inner thickness to 0.02 and have it run into your belly.
#13. Bake your softbody simulation.
#14. Result might look ugly. To fix, the copy (a.) has been given a new Corrective Smooth modifier. You just need to unhide it. 




#################################
#############CHANGELOG###########
#
# 1.01  
#       - SB_belly will not be created at World Origin (if the armature has been moved in object mode) anymore.
# 1.0
#       - Original version.









############################################################################################################################################################################
############################################################################################################################################################################
import bpy
import statistics

C = bpy.context
D = bpy.data
O = bpy.ops



#lets you select a list of objects (need to input the actual classes instead of their names), and also optionally choose the object you want to be active. By default it sets the first item in the list as active. The optional active object doesn't have to be in the list to be set as active, but then it still won't be selected.
#will deselect all other objects
#example: select_objects([Suzanne,Cube,Suzanne.001],Suzanne.004)
def select_objects(object_list, active_object = None):
    O.object.select_all(action='DESELECT')
    if object_list == [] and active_object == None:
        return "no objects to select"
    for i in object_list:
        i.select_set(True)
    if active_object == None:
        C.view_layer.objects.active = object_list[0]
    else:
        C.view_layer.objects.active = active_object

        
#applies the specified modifiers (use the actual names of the modifiers) of the specified object. The order in which the modifiers are applied is equal to their order in the list -> the first one gets applied first. It uses a context-override so it doesn't select/deselect any objects. Setting invert to True means that it will apply all modifiers of the object that are *not* in the given modifier list, however it will take the default mod-stack order. Choosing an empty list means it will apply all modifiers. If delete_hidden is set to True, it will delete, instead of apply, a modifier if it is set to hidden.
#example: apply_modifiers('Cube.001',["Wireframe.001","Subdivision"])
def apply_modifiers(object, modifier_list = [], invert = False, delete_hidden = False):                    #had a problem with the context override, for future reference: if you want to do stuff with "active_object", you also have to change "object" to that object.
    override = C.copy()
    override['active_object'] = object
    override['object']= object
    if modifier_list == []:
        modifier_list = list(object.modifiers.keys())
    if invert == True:
        h_modifier_list = list(object.modifiers.keys())
        for i in modifier_list:
            if i in h_modifier_list:
                h_modifier_list.remove(i)
        modifier_list = h_modifier_list
    if delete_hidden == True:
        for i in modifier_list:
            if i in object.modifiers.keys():
                if object.modifiers[i].show_viewport == True:
                    try:
                        O.object.modifier_apply(override, apply_as='DATA', modifier = i)
                    except RuntimeError:
                        print("OOPS! MODIFIER", i, "IS DISABLED! IT WILL BE DELETED") #trying to apply a disabled modifiier leads to an error message, but I didn't figure out how to check if it's disabled. Thus, we'll have to deal with the error instead.
                        print("ERROR TYPE IS", sys.exc_info()[0])
                        O.object.modifier_remove(modifier = i)   
                elif object.modifiers[i].show_viewport == False:
                    O.object.modifier_remove(modifier = i)
    elif delete_hidden == False:
        for i in modifier_list:
            if i in object.modifiers.keys():
                O.object.modifier_apply(override, apply_as='DATA', modifier = i)


#checks if there already are any collections inside the target_collection that start with the collection_name (so it can detect e.g. myCollection.001 if you search for any myCollection). Returns the first found collection, or False if none were found. Checks child collections of child collections as well, and so on.
#example: check_collections('Collec', bpy.context.scene.collection) #(bpy.context.scene.collection is the master-collection of your scene, it contains all other collections)
def check_collections (collection_name, target_collection): 
    if list(target_collection.children) == []:
        return False
    for i in target_collection.children:
        if i.name.startswith(collection_name):
            print(i)
            return i
    return(check_collections(collection_name, i))
#maybe it will lead to problems if the collection is also linked to other scenes/ collections, but I dont care about that for now.


#creates a collection with the collection_name inside the parent_collection. If you don't want duplicates to be created ("Collection.001" instead of "Collection" because there already is a "Collection") set avoid_duplicates as True. It will return the found duplicate - if there is one, otherwise it'll create a new one as normal.
#example: create_collection('third_Collection', parent_collection = bpy.data.collections['second_Collection'], avoid_duplicates = True)
def create_collection (collection_name, parent_collection = C.scene.collection, avoid_duplicates = False):
    if avoid_duplicates == False:
        new_collection = D.collections.new (name=collection_name)
        parent_collection.children.link(new_collection)
    elif avoid_duplicates == True:
        found_collection = check_collections(collection_name, parent_collection)
        print(found_collection)
        if found_collection == False:
            new_collection = D.collections.new (name=collection_name)
            parent_collection.children.link(new_collection)
        else:
            new_collection = found_collection
    return new_collection


#links and unlinks specified objects to the specified collections. To prevent bugs the objects should all share the same collections
#example: link_objects(bpy.context.selected_objects, bpy.context.scene.collection.children['New_Collection'], [bpy.context.scene.collection.children['Old_Collection']])
def link_objects(objects, link_to, unlink_to = []): #unlink_to needs to be a list (collections to unlink), None (unlink no collection), or not be specified at all (unlink all collections). link_to only uses one collection, so no list.
    if unlink_to == []:
        unlink_to = objects[0].users_collection    
    elif unlink_to == None:
        unlink_to = []
    
    for i in objects:
        for x in unlink_to:
            x.objects.unlink(i)
        link_to.objects.link(i)    

#########################################################################
#########################################################################
#########################################################################
O.object.mode_set_with_submode(mode='EDIT',  mesh_select_mode = {"VERT"} ) #Setting the default selection mode to vertex.
O.object.mode_set(mode='OBJECT')
trashcan = []


Obj_origreal = C.object
O.object.duplicate() #messing with the actual original object just feels wrong
Obj_orig = C.object
Obj_orig.name = Obj_origreal.name + " copy"

O.object.duplicate()
Obj_bellySB = C.object  #this is going to be an object where almost all vertices that aren't in the SB goal VG will have been deleted to speed up calculation time. This is the object you should use to actually bake any softbody simulations.
Obj_bellySB.name = "belly_SB"
for i in Obj_bellySB.modifiers:
    if i.type == "SOFT_BODY":
        Mod_SB_belly = i
        break
Mod_SB_belly.show_viewport = False
#got this whole depthgrapth stuff from the "func_object_duplicate_flatten_modifiers" function of "Corrective Shape Keys" add-on by the authors "Ivo Grigull (loolarge), Tal Trachtman", "Tokikake". It's basically only 3 lines  but I still feel like I should credit them.
depthgraph = C.evaluated_depsgraph_get()                    #gets depthgraph of current scene
ID_applmods = Obj_bellySB.evaluated_get(depthgraph)            #gets ID of object in that depthgraph
Mesh_applmods = D.meshes.new_from_object(ID_applmods)       #creates a new, actual mesh. Objects can switch to that mesh like any other, but we can't do that since we would lose any vertex weights.
select_objects([Obj_bellySB])
Obj_bellySB.shape_key_clear()      #modifiers can't be applied when the object has shapekeys
apply_modifiers(object = Obj_bellySB, modifier_list = [Mod_SB_belly.name], invert = True, delete_hidden = True)
for i, e in zip(Obj_bellySB.data.vertices, Mesh_applmods.vertices):
    i.co = e.co
#O.object.parent_clear(type='CLEAR_KEEP_TRANSFORM') #at least for the Mass Effect "Liara" model from Rigid3D the model doesn't seem to be able to keep the transforms, so we'll have to keep the parent.
O.object.transform_apply(location=True, rotation=True, scale=True)
Obj_bellySB.animation_data_clear() #deletes all keyframes
VG_goal_name    = Mod_SB_belly.settings.vertex_group_goal #the mod itself only returns a string instead of the required VG-type
VG_goal         = Obj_bellySB.vertex_groups[VG_goal_name]
Mod_datatransfer = Obj_bellySB.modifiers.new("transfer VGs","DATA_TRANSFER")
Mod_VGedit       = Obj_bellySB.modifiers.new("remove 0 weights","VERTEX_WEIGHT_EDIT") #data transfer mod assigns unassigned verts with a weight of 0
Mod_datatransfer.object = Obj_orig  #source object
Mod_datatransfer.use_vert_data = True
Mod_datatransfer.data_types_verts = {'VGROUP_WEIGHTS'}
Mod_datatransfer.vert_mapping = 'TOPOLOGY'
Mod_VGedit.vertex_group = VG_goal.name
Mod_VGedit.use_remove = True
Mod_VGedit.remove_threshold = 0.00000001
apply_modifiers(Obj_bellySB, modifier_list = [Mod_datatransfer.name, Mod_VGedit.name])



Obj_bellySB.vertex_groups.active = VG_goal
bpy.ops.object.vertex_group_copy()
VG_editgoal       = Obj_bellySB.vertex_groups[-1] #we do it like this so we won't have to deal with copying each vertex weight difficultly
VG_editgoal.name  = VG_goal.name + " edited"

Mod_SB_belly.settings.vertex_group_goal = VG_editgoal.name
Mod_SB_belly.settings.mass            = 0   #heavily suggested values for your SB mod. Mass of 0k prevents any gravity happening, and max and default goal values of 1 are needed to keep the object in place (see "anchor vertices" in this script below)
Mod_SB_belly.settings.goal_default    = 1
Mod_SB_belly.settings.goal_max        = 1



for i in Obj_orig.modifiers:
    if i.type == "SUBSURF" and i.show_viewport == True:
        print("Active Subdivision Surface modifier found, script will have to give all verts of SB goal the same median weight.")
        ind_weights = []
        weights = []
        VG_goal_origobj = Obj_orig.vertex_groups[Obj_orig.soft_body.vertex_group_goal]
        for e in Obj_orig.data.vertices:
            e = e.index
            try:
                w = VG_goal_origobj.weight(e)
                ind_weights += [[e, w]]
                weights += [w]
            except RuntimeError:
                None
                #print("vertex not assigned to VG")
        weight_median = statistics.median(weights) 
        Obj_bellySB.vertex_groups.active = VG_editgoal
        O.object.mode_set(mode='EDIT')
        O.mesh.select_all(action='DESELECT')
        O.object.vertex_group_select()
        C.scene.tool_settings.vertex_group_weight = weight_median
        O.object.vertex_group_assign()
        O.object.mode_set(mode='OBJECT')
        
        break
        

###giving a copy of the SB goal VG anchor vertices. "Anchor" because with the right values, these vertices will not deform in any way through the softbody sim. Also they will keep the belly from being pushed around in space. ###All vertices that are not in this new VG will be deleted, as they are useless to our softbody sim and only slow down the calculation.
select_objects([Obj_bellySB])
Obj_bellySB.vertex_groups.active = VG_editgoal
O.object.mode_set(mode='EDIT')
O.mesh.select_all(action='DESELECT')
O.object.vertex_group_select()
O.mesh.select_more()
O.object.vertex_group_deselect()
C.scene.tool_settings.vertex_group_weight = 1
O.object.vertex_group_assign()
O.object.vertex_group_select()
O.mesh.select_all(action='INVERT')
O.mesh.delete(type='VERT')
O.object.mode_set(mode='OBJECT')



O.object.duplicate()
Obj_vwpref = C.object
Obj_vwpref.name = "VWP reference object"



VG_vwp = Obj_orig.vertex_groups.new(name = "VWP VG")
vert_indices = []
for i in Obj_orig.data.vertices:
    vert_indices += [i.index]
VG_vwp.add(vert_indices, 1.0, "ADD")    #for some reason when we assign 0.0 it gives weird results
Mod_vwp = Obj_orig.modifiers.new("get VG for surface deform mod","VERTEX_WEIGHT_PROXIMITY")

Mod_vwp.vertex_group = VG_vwp.name
Mod_vwp.target = Obj_vwpref
Mod_vwp.proximity_mode = 'GEOMETRY'
Mod_vwp.proximity_geometry = {'VERTEX'}
Mod_vwp.max_dist = 0
Mod_vwp.min_dist = 1e-08


select_objects([Obj_orig])
Mod_surfdef = Obj_orig.modifiers.new("transfer isolated belly animation","SURFACE_DEFORM")
Mod_surfdef.target = Obj_bellySB
Mod_surfdef.vertex_group = VG_vwp.name
bpy.ops.object.surfacedeform_bind(modifier = Mod_surfdef.name)



#This one isn't actually needed, just added it for comfort.
Mod_cs = Obj_orig.modifiers.new("Corrective Smooth","CORRECTIVE_SMOOTH")
Mod_surfdef.show_viewport = False
Mod_cs.rest_source = "BIND"
O.object.correctivesmooth_bind(modifier = Mod_cs.name)
Mod_cs.show_viewport = False
Mod_surfdef.show_viewport = True



Coll_main = create_collection('Prepared_Softbodies', avoid_duplicates = True)
Coll_sub  = create_collection('Block', parent_collection = Coll_main, avoid_duplicates = False)
link_objects([Obj_orig, Obj_bellySB, Obj_vwpref], Coll_sub)



Mod_SB_belly.show_viewport = True
Obj_vwpref.hide_set(True)
Obj_origreal.hide_set(True)
select_objects(trashcan)
O.object.delete(use_global=False)
