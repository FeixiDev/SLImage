import os
import sys
import re
import docker_operator
import utils
from pathlib import Path


class Images(object):
    def __init__(self):
        self.yaml_file = utils.ConfFile('SLImage_config.yaml')
        self.yaml_info_list = self.yaml_file.read_yaml()
        self.ssh_obj = None
        self.docker_cmds = docker_operator.Docker()
        if self.yaml_info_list:
            self.ssh_len = len(self.yaml_info_list['node'])
            for i in range(self.ssh_len):
                self.ssh_obj = utils.SSHconn(host=self.yaml_info_list['node'][i]['ip'],
                                            username=self.yaml_info_list['node'][i]['username'],
                                            password=self.yaml_info_list['node'][i]['password'])
        

    def save_images(self):
        current_directory = os.path.dirname(os.path.realpath(sys.argv[0]))
        save_path = os.path.join(current_directory, "save_images")
        name_result = self.docker_cmds.check_images_name()
        tag_result = self.docker_cmds.check_images_tag()
        id_result = self.docker_cmds.check_images_id()
        # print(f"name_result: {name_result}")
        # print(f"tag_result: {tag_result}")
        # print(f"id_result: {id_result}")
        print("Start saving the images")

        name_result = name_result.splitlines()[1:]
        tag_result = tag_result.splitlines()[1:]
        id_result = id_result.splitlines()[1:]

        list1 = [':']
        images_list = []

        for id_result, name_result, tag_result in zip(id_result, name_result, tag_result):
            # author_list = re.findall(r'(.+(?=/))', str(name_result[i]))
            # author_list = None
            # print(f"author_list: {author_list}")
            # name_list = re.findall(r'((?<=/).+)', str(name_result[i]))
            name = name_result.rsplit('/', 1)[-1]
            # print(f"name_list: {name}")
            # if len(author_list) != 0:
            #     author_list = author_list[0]
            #     # name_list = name_list[0]
            #     self.docker_cmds.save_images(id_result, save_path, name_list, tag_result, author_list)
            #     # docker save 5384b1650507 -o ./save_images/kube-proxy:v1.20.5.tar
            # else:
                # name_list = name_result[i]
            self.docker_cmds.save_images(id_result, save_path, name, tag_result)
            
            # for i in range(0, len(name_result)):
            images_list.append(name + list1[0] + tag_result)
        utils.save_imageflile('save', images_list)
        print('All images have saved')

    def save_as_tar(self, tar_name, image_name):
        current_directory = os.path.dirname(os.path.realpath(sys.argv[0]))
        save_path = os.path.join(current_directory, "save_images")
        name_result = self.docker_cmds.check_images_name()
        id_result = self.docker_cmds.check_images_id()

        name_result = name_result.splitlines()[1:]
        id_result = id_result.splitlines()[1:]

        if image_name:
            print(f"Start saving {image_name} images as tar: {tar_name}.tar")
            merged_dict = {}
            for name, _id in zip(name_result, id_result):
                # If image_name is specified and not in the current name, skip to the next iteration
                if image_name and image_name not in name:
                    continue
                # Add the elements to the dictionary
                merged_dict[name] = {'id': _id}
            image_ids_str = ' '.join(info['id'] for info in merged_dict.values())
        else:
            print(f"Start saving all images as tar: {tar_name}.tar")
            
            image_ids_str = ' '.join(id_result)
            # print(f"image_ids_str: {image_ids_str}")

        self.docker_cmds.save_images(image_ids_str, save_path, tar_name)
        images_list = []
        images_list.append(tar_name + '.tar')

        # Use tar_file_path as the destination file for saving images
        utils.save_imageflile('save', images_list)

        print(f'All images have been saved as tar: {tar_name}.tar')

    def load_images(self):
        local_path = sys.path[0] + '/save_images'
        remote_path = 'save_images'
        file_path = Path(remote_path)
        try:
            print("Transferring images to nodes")
            self.controller_node.upload(local_path, remote_path)
        except:
            print("Images transfer failed")
        try:
            file_path.resolve()
        except FileNotFoundError:
            print("save_images does not exist")

        images_name = os.listdir(sys.path[0]+'/save_images')
        print("Start loading the images")
        for i in range(len(images_name)):
            self.docker_cmds.load_images(images_name[i], self.ssh_obj)
        name_result = self.docker_cmds.check_images_name(self.ssh_obj)
        if name_result == images_name:
            print('All images have loaded')
            utils.exec_cmd("rm save_images", self.ssh_obj)
        else:
            print(sys.path[0]+"/save_images")


