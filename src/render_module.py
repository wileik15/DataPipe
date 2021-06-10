import bpy
from pathlib import Path
import time

from .scene_module import BlendScene


class Renderer:

    def __init__(self, camera: object):

        self.camera = camera

        self.view_layers_list = camera.projector.pattern_names_list

        self.output_nodes_list = self.create_render_node_tree()

        self.render_path = ''


    def create_render_node_tree(self):
        
        print("\n\n#####################\nCREATING NODE TREE\n#####################\n\n")
        x_coord = 0
        y_coord = 0

        delta_y = -110
        delta_x = 300

        bpy.context.scene.use_nodes = True
        node_tree = bpy.context.scene.node_tree
        node_tree.nodes.clear() #Clear auto created nodes
        links = node_tree.links


        out_node_list = []

        native_layer = bpy.context.scene.view_layers['native_layer']

        #Set viewlayer render options
        native_layer.use_pass_z = True
        native_layer.use_pass_normal = True
        native_layer.use_pass_object_index = True

        render_node = node_tree.nodes.new(type="CompositorNodeRLayers") #Add a render layer node
        render_node.layer = native_layer.name
        render_node.name = "render_node_native_layer"
        render_node.location = x_coord, y_coord

        x_coord += delta_x

        #RGB image node
        rgb_out_node = out_node = node_tree.nodes.new(type="CompositorNodeOutputFile")
        rgb_out_node.name = 'rgb_output_node'
        rgb_out_node.format.file_format = 'PNG'
        rgb_out_node.location = x_coord, y_coord
        rgb_out_node.inputs[0].name = 'rgb_image'
        
        out_node_list.append(rgb_out_node) #Add rgb output node to out_node_list

        rgb_link = links.new(input=rgb_out_node.inputs[0], output=render_node.outputs[0]) #Link to render layer node
        
        y_coord += delta_y

        #Depth image node
        depth_out_node = node_tree.nodes.new(type="CompositorNodeOutputFile")
        depth_out_node.name = 'depth_output_node'
        depth_out_node.format.file_format = 'OPEN_EXR'
        depth_out_node.location = x_coord, y_coord
        depth_out_node.inputs[0].name = 'depth_image'

        out_node_list.append(depth_out_node) #Add depth output node to out_node_list

        depth_link = links.new(input=depth_out_node.inputs[0], output=render_node.outputs[2]) #Link to render layer node

        y_coord += delta_y

        #Normals image node
        normals_out_node = node_tree.nodes.new(type="CompositorNodeOutputFile")
        normals_out_node.name = 'normals_output_node'
        normals_out_node.format.file_format = 'PNG'
        normals_out_node.location = x_coord, y_coord
        normals_out_node.inputs[0].name = 'normals_image'

        out_node_list.append(normals_out_node) #Add normals output node to out_node_list

        normals_link = links.new(input=normals_out_node.inputs[0], output=render_node.outputs[3]) #Link to render layer node

        y_coord += delta_y

        #Masked image node
        mask_out_node = node_tree.nodes.new(type="CompositorNodeOutputFile")
        mask_out_node.name = 'mask_output_node'
        mask_out_node.format.file_format = 'OPEN_EXR'
        mask_out_node.location = x_coord, y_coord
        mask_out_node.inputs[0].name = 'masked_image'

        out_node_list.append(mask_out_node) #Add mask output node to out_node_list

        mask_link = links.new(input=mask_out_node.inputs[0], output=render_node.outputs[4]) #Link to render layer node

        x_coord = -500
        y_coord = 0
        delta_y = -400

        if self.camera.is_structured_light: #Create render nodes for structured light view layers

            for layer_name in self.view_layers_list:
                
                render_node = node_tree.nodes.new(type="CompositorNodeRLayers") #Add a render layer node
                render_node.layer = layer_name
                render_node.name = "render_node_{}".format(layer_name)
                render_node.location = x_coord, y_coord

                out_node = node_tree.nodes.new(type="CompositorNodeOutputFile")
                out_node.name = "output_node_{}".format(layer_name)
                out_node.location = x_coord + delta_x, y_coord
                out_node.format.file_format = 'PNG'
                out_node.inputs[0].name = layer_name

                out_node_list.append(out_node)

                out_link = links.new(input=out_node.inputs[0], output=render_node.outputs[0])

                y_coord += delta_y

        return out_node_list
    
    def set_output_paths(self, scene: BlendScene, render_num):

        scene_path = scene.output_path

        render_dir_name = 'render.{:04d}'.format(render_num)
        render_path = Path.joinpath(scene_path, Path(render_dir_name))
        
        render_path.mkdir()
        render_path = str(render_path)

        self.render_path = render_path

        for out_node in self.output_nodes_list:

            path_string = "{}/{}".format(render_path, out_node.inputs[0].name)
            path = Path(path_string)
            out_node.base_path =  str(path) #Set render path for nodes
        
    
    def render_results(self):
        render_start = time.time()
        bpy.ops.render.render(use_viewport=True)
        render_end = time.time()
        print("Rendertime: {:.4f}".format(render_end-render_start))