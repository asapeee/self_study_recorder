import subprocess

if __name__ == '__main__':
    subprocess.run(['flask', 'host="0.0.0.0"', 'run'])