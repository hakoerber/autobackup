import time
import subprocess

import idgenerator
import fdmanager

class NetworkConnection(object):
    """Abstract base class representing a network connection."""
    
    def __init__(self, host, user, port):
        raise NotImplementedError()
    
    
    def connect(self, timeout, remote_shell):
        """
        Connects to the host as <user> and starts a shell specified by 
        <remote_shell>. Raises a timeout error if <timeout> (in milliseconds) 
        exceeded.
        :param timeout: Timeout after which an error is raised.
        :type timeout: int
        :param remote_shell: Remote shell that is used to execute the commands.
        :type remote_shell: string"""
        raise NotImplementedError()
    
    
    def disconnect(self):
        """Disconnects the connection immediately."""
        raise NotImplementedError()
    
    
    def execute(self, command, timeout):
        """
        Executes a <command> on the remote host as user <user>. Raises a 
        timeout error if the command did not finish after <timeout> 
        milliseconds.
        :param command: The command to execute on the remote host.
        :type command: string
        :param timeout: Timeout after which an error is raised.
        :type timeout: int
        """
        raise NotImplementedError()
    
    
    def is_connected(self):
        """
        Returns a bool that specifies whether the connection is established.
        :returns: True if a connection is established, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError()
        

class SSHNetworkConnection(NetworkConnection):
    
    def __init__(self, host, user, port):
        super(SSHNetworkConnection, self).__init__(host, user, port)
        self.port = port
        self.host = host
        self.user = user
        
        self.ssh_process = None
        
        
    def __del__(self):
        pass
        # At this point, the object may already be deleted and disconnect may 
        # not be found.
        #self.diconnect()
    
    
    def connect(self, timeout, remote_shell):
        if self.ssh_process != None:
            return 
         
        connection_id = idgenerator.generate_id(20)
        
        args = ["ssh", \
                "-o", "StrictHostKeyChecking=yes", \
                "-p", str(self.port), \
                "-q", \
                "-x", \
                "-l", self.user, \
                self.host.ip, \
                # Double quotes will automatically be added by 
                # subprocess.list2cmdline()
                'echo {0} ; {1}'.format(connection_id, remote_shell)]
                                       
        self.ssh_process = subprocess.Popen(args, shell=False, bufsize=-1, \
                                             stdout=subprocess.PIPE, \
                                             stderr=subprocess.PIPE, \
                                             stdin=subprocess.PIPE)        
        
        # We will poll the process output once every 100 ms 
        POLL_INTERVAL = 100
        max_polls = timeout / POLL_INTERVAL
        poll = 0
        
        # 0: stdout, 1: stderr
        stdpipe = (self.ssh_process.stdout, self.ssh_process.stderr)
        output = [[], []]
        lines = [[], []]
        
        # Unblock pipes so read() and readline() does not block
        for i in 0, 1:
            fdmanager.unblock_file_descriptor(stdpipe[i])
        
        connected = False

        # Now we will wait for a line in stdout starting with connection_id or 
        # abort when timeout is exceeded
        while True:
            poll += 1
            
            if poll >= max_polls:
                self.disconnect()
                raise Exception("timeout")
                        
            for i in 0, 1:
                lines[i] = fdmanager.read_all(stdpipe[i])
                                
            for i in 0, 1:
                for line in lines[i].split('\n'):
                    if line:
                        output[i].append(line)

            for line in lines[0].split('\n'):
                if line.startswith(connection_id):
                    # Connection established
                    connected = True
                    
            if connected:
                break
            
            time.sleep(POLL_INTERVAL/1000.0)
            
        for i in 0, 1:
            output[i].append(fdmanager.read_all(stdpipe[i]))
            output[i] = "".join(output[i])
            
        if output[1]:
            raise Exception(
                "Some error occured, stderr:\n{0}".format(output[1]))
        
        return (output[0], output[1])
    
             
    def disconnect(self):
        if self.ssh_process != None:
            self.ssh_process.terminate()
            self.ssh_process = None    
    
    
    def execute(self, command, timeout):
        command_id = idgenerator.generate_id(20)
        stdpipe = (self.ssh_process.stdout, self.ssh_process.stderr)
        
        # Flush streams as precaution
        for i in 0, 1:
            stdpipe[i].flush()
                         
        output = [[], []]
        lines = [[], []]
        
        last_line = None
        finished = False
        
        POLL_INTERVAL = 100
        max_polls = timeout / POLL_INTERVAL
        polls = 0
 
        command = '{0} ; echo {1}@$?\n'.format(subprocess.list2cmdline(command),
                                               command_id)
        self.ssh_process.stdin.write(command)
        self.ssh_process.stdin.flush()
        
        while True:
            polls += 1

            if polls >= max_polls:
                raise Exception("timeout")
                                    
            for i in 0, 1:
                lines[i] = fdmanager.read_all(stdpipe[i])
                            
            for i in 0, 1:
                for line in lines[i].split('\n'):
                    if i == 0 and line.startswith(command_id):
                        last_line = line
                        finished = True
                    elif line:
                        output[i].append(line)
                    
            if finished:
                break
            time.sleep(POLL_INTERVAL/1000.0)
            
        for i in 0, 1:
            output[i].append(fdmanager.read_all(stdpipe[i]))
            output[i] = '\n'.join(output[i])
            
        exit_code = last_line.split('@')[1]
                            
        return(exit_code, output[0], output[1])


    def is_connected(self):
        return self.ssh_process != None
