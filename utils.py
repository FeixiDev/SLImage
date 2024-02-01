import atexit
import paramiko
import subprocess
import logging
import datetime
import sys
import yaml
import socket
import os


def get_host_ip():
    """
    查询本机ip地址
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def exec_cmd(cmd, conn=None):
    local_obj = LocalProcess()
    if conn:
        result = conn.exec_cmd(cmd)
    else:
        result = local_obj.exec_cmd(cmd)
    result = result.decode() if isinstance(result, bytes) else result
    log_data = f'{get_host_ip()} - {cmd} - {result}'
    Log().logger.info(log_data)
    if isinstance(result, dict):
        result = result.get('rt', '').rstrip('\n')
    else:
        print(f"Debug: Result is not a dictionary. Type: {type(result)}")
    return result

def save_imageflile(operate, image_list=None):
    """
    保存images清单
    """
    if image_list != None:
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        if operate == 'save':
            file_name = str(now_time) + '-save.txt'
        elif operate == 'load':
            file_name = str(now_time) + '-load.txt'
        file_path = sys.path[0] + f'/{file_name}'
        image_file = open(file_path, 'w')
        image_list.append('\n')
        image_file.writelines([line+'\n' for line in image_list])
        image_file.close()
        return None
    else:
        print()
def is_exists(path, function):
    """
    检查路径是否存在
    """
    path = path.replace('\\', '/')
    try:
        function(path)
    except Exception as error:
        return False
    else:
        return True



class SSHconn(object):
    def __init__(self, host, port=22, username="root", password=None, timeout=8):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.timeout = timeout
        self.sshconnection = None
        self.ssh_conn()

    def ssh_conn(self):
        """
        SSH连接
        """
        try:
            conn = paramiko.SSHClient()
            conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            conn.connect(hostname=self._host,
                         username=self._username,
                         port=self._port,
                         password=self._password,
                         timeout=self.timeout,
                         look_for_keys=False,
                         allow_agent=False)
            self.sshconnection = conn
        except paramiko.AuthenticationException:
            print(f" Error SSH connection message of {self._host}")
        except Exception as e:
            print(f" Failed to connect {self._host}")

    def exec_cmd(self, command):
        """
        命令执行
        """
        if self.sshconnection:
            stdin, stdout, stderr = self.sshconnection.exec_command(command)
            result = stdout.read()
            result = result.decode() if isinstance(result, bytes) else result
            if result is not None:
                return {"st": True, "rt": result}

            err = stderr.read()
            if err is not None:
                return {"st": False, "rt": err}


    def upload(self,local, remote):
        """
        sftp上传文件
        """
        transport = paramiko.Transport(self._host, self._port)
        transport.connect(username=self._username, password=self._password)
        sftp_file = paramiko.SFTPClient.from_transport(transport)

        def copy(local, remote):
            if is_exists(remote, function=sftp_file.chdir):
                filename = os.path.basename(os.path.normpath(local))
                remote = os.path.join(remote, filename).replace('\\', '/')
            if os.path.isdir(local):
                is_exists(remote, function=sftp_file.mkdir)
                for file in os.listdir(local):
                    localfile = os.path.join(local, file).replace('\\', '/')
                    copy(sftp=sftp_file, local=localfile, remote=remote)
            if os.path.isfile(local):
                try:
                    sftp_file.put(local, remote)
                except Exception as error:
                    print(error)
                    print('[put]', local, '==>', remote, 'FAILED')
                else:
                    print('[put]', local, '==>', remote, 'SUCCESSED')
        if not is_exists(local, function=os.stat):
            print("'" + local + "': No such file or directory in local")
            return False
        remote_parent = os.path.dirname(os.path.normpath(remote))
        if not is_exists(remote_parent, function=sftp_file.chdir):
            print("'" + remote + "': No such file or directory in remote")
            return False
        copy(sftp=sftp_file, local=local, remote=remote)


class LocalProcess(object):
    def exec_cmd(self, command):
        """
        命令执行
        """
        sub_conn = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if sub_conn.returncode == 0:
            result = sub_conn.stdout
            result = result.decode() if isinstance(result, bytes) else result
            return {"st": True, "rt": result.strip('\n')}
        else:
            print(f"Can't to execute command: {command}")
            err = sub_conn.stderr
            print(f"Error message:{err}")
            return {"st": False, "rt": err}


class ConfFile(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def read_yaml(self):
        """
        读yaml文件
        """
        try:
            if self.file_path and os.path.isfile(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    yaml_file = yaml.load(f, Loader=yaml.FullLoader)
                return yaml_file
            else:
                return None
        # except FileNotFoundError:
        #     print("File not found")
        except TypeError:
            print("Error in the type of file .")

    def update_yaml(self, yaml_dict):
        """
        更新yaml文件
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_dict, f, default_flow_style=False)
        except FileNotFoundError:
            print("File not found")
        except TypeError:
            print("Error in the type of file .")


class Log(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.logger = logging.getLogger()
            cls._instance.logger.setLevel(logging.INFO)
            cls._instance.set_handler()
            atexit.register(cls._instance.close_handler)  # 注册关闭处理程序的方法
        return cls._instance

    def set_handler(self):
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        log_file_name = f"SLImage_{now_date}.log"
    
        # Check if the log file already exists
        if not hasattr(self, 'log_date') or now_date != self.log_date:
            self.log_date = now_date
            log_file_name = f"SLImage_{now_date}.log"
            fh = logging.FileHandler(log_file_name, mode='a')
            fh.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def close_handler(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            if isinstance(handler, logging.FileHandler):
                # 添加分隔线到日志的最后一行
                handler.stream.write('\n' + '-' * 50 + ' End of Log ' + '-' * 50 + '\n')
                handler.flush()
                handler.close()
                self.logger.removeHandler(handler)
