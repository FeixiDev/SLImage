import utils
class Docker(object):
    def check_images_name(self, ssh_conn=None):
        cmd = "docker images |  awk '{print $1}'"
        result = utils.exec_cmd(cmd, ssh_conn)
        return result

    def check_images_tag(self, ssh_conn=None):
        cmd = "docker images |  awk '{print $2}'"
        result = utils.exec_cmd(cmd, ssh_conn)
        return result

    def check_images_id(self, ssh_conn=None):
        cmd = "docker images |  awk '{print $3}'"
        result = utils.exec_cmd(cmd, ssh_conn)
        return result

    def save_images(self, id, file_path, name, tag, author='', ssh_conn=None):
        if author == '':
            cmd = f'docker save {id} -o {file_path}/{name}:{tag}.tar'
        else:
            cmd = f'docker save {id} -o {file_path}/{author}:{name}:{tag}.tar'

        result = utils.exec_cmd(cmd, ssh_conn)
        return result

    def load_images(self, image_name, ssh_conn=None):
        cmd = f'docker load -i {image_name}'
        result = utils.exec_cmd(cmd, ssh_conn)
        return result

