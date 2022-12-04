import sys
import re
import docker_operator
import utils


class Images(object):
    def __init__(self):
        self.yaml_file = utils.ConfFile('config.yaml')
        self.yaml_info_list = self.yaml_file.read_yaml()
        self.ssh_len = len(self.yaml_info_list['node'])
        for i in range(self.ssh_len):
            self.ssh_obj = utils.SSHconn(host=self.yaml_info_list['node'][i]['ip'],
                                         username=self.yaml_info_list['node'][i]['username'],
                                         password=self.yaml_info_list['node'][i]['password'])
        self.docker_cmds = docker_operator.Docker()

    def save_images(self):
        save_path = sys.path[0] + '/save_images'
        name_result = self.docker_cmds.check_images_name()
        tag_result = self.docker_cmds.check_images_tag()
        id_result = self.docker_cmds.check_images_id()
        print("Start saving the images")
        for i in range(len(id_result)):
            author_list = re.findall(r'(.+(?=/))', str(name_result[i]))
            name_list = re.findall(r'((?<=/).+)', str(name_result[i]))
            if len(author_list) != 0:
                author_list = author_list[0]
                name_list = name_list[0]
                self.docker_cmds.save_images(id_result[i], save_path, name_list, tag_result[i], author_list)

            else:
                name_list = name_result[i]
                self.docker_cmds.save_images(id_result[i], save_path, name_list, tag_result[i])
            list1 = [':']
            images_list = []
            for i in range(0, len(name_result)):
                images_list.append(name_list[i] + list1[0] + tag_result[i])
                utils.save_imageflile('save', images_list)
                print('All images have saved')

    def load_images(self):
        local_path = sys.path[0] + '/save_images'
        remote_path = 'save_images'
        self.controller_node.upload(local_path, remote_path)
if __name__ == '__main__':
    Images().save_images()