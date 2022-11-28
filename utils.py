import paramiko
import subprocess
import logging
import datetime
import sys


def exec_cmd(cmd, image_name, images, conn=None):
    local_obj = LocalProcess()
    if conn:
        result = conn.exec_cmd(cmd)
    else:
        result = local_obj.exec_cmd(cmd)
    result = result.decode() if isinstance(result, bytes) else result
    log_data = f'{image_name} - {result}'
    Log().logger.info(log_data)
    if result['st']:
        pass
        # f_result = result['rt'].rstrip('\n')
    if result['st'] is False:
        sys.exit()
    return result['rt']


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

class LocalProcess(object):
    def exec_cmd(self,command):
        """
        命令执行
        """
        sub_conn = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if sub_conn.returcode == 0:
            result = sub_conn.stdout
            return {"st": True, "rt": result}
        else:
            print(f"Can't to execute command: {command}")
            err = sub_conn.stderr
            print(f"Error message:{err}")
            return {"st": False, "rt": err}

class Log(object):
    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            Log._instance = super().__new__(cls)
            Log._instance.logger = logging.getLogger()
            Log._instance.logger.setLevel(logging.INFO)
            Log.set_handler(Log._instance.logger)
        return Log._instance

    @staticmethod
    def set_handler(logger):
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_name = str(now_time) + '.log'
        fh = logging.FileHandler(file_name, mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)