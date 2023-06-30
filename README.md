# pyreader
python testing framework that uses files found by crawling a S3 bucket

installation:
- wget https://bootstrap.pypa.io/pip/3.6/get-pip.py
- python3 ./get-pip.py
- pip install aws-requests-auth
- pip install regex

## Running besstandalone using the Docker container build
Summary: Configure Docker so it can be used by a non-root user, if
that's not already the case. Start the container with just the BES and
run besstandalone. To access stuff in S3, given that the bucket is
protected, add credentials using the ENV_CREDS feature of the BES's
CredentialsManager.

Note: This assumes in places paths that are set on the ngap-test.opendap.org.
YMMV.

### Configure Docker for non-root use
1. Make a 'docker' group using the addgroup command, run as root.
(`sudo addgroup docker`)
2. Add non-root users to the group (`sudo adduser -aG <user> docker`)
3. If you need to do this, log out and log back in.
4. To test to see if you need to do this, or to see if after doing it,
the change worked, run 'docker run hello-world' as a non-root user.

### Start the container
Use the command `docker run` with the options:
```bash
-d -h besd -p 10022:10022 --name besd \
-v /home/centos/pyreader:/user/share/pyreader:Z \
```
Where -d will run the container as detached, -h sets the hostname, -p
will 'publish' a TCP port from the container to the host, --name
provides a name that can be used to refere to the running container
from other Docker commands, -v maps a directory on the host computer
to a directory inside the container. The special ':Z' on SE (security
enhanced) Linux will cause Docker to effectively run
```bash
chcon -Rt svirt_sandbox_file_t /usr/share/pyreader
```
which means that the container can access the mapped host directory
without extra work given that the host is using SE Linux.

The full command to start the container on SE linux looks like:
```bash
docker run -d -h besd -p 10022:10022 --name besd \
-v /home/centos/pyreader:/usr/share/pyreader:Z \
opendap/besd:snapshot
```

For OSX or Linux with SE Linux features absent/disabled, drop the
trailing ```:Z``` on the volume mount. If you want the current
directory to be the host's directory for the /usr/share/pyreader mount
point, you can use ```$(pwd):/usr/share...```.

### Testing the running container
Use 'docker exec -it besd bash' to get a shell running inside the
container started using 'docker run...' above. You can play around and
see how the directory mapping works.

### Stop the running container
Use `docker rm -f besd` to stop the container. YMMV on whether you
need the '-f'.

### See what containers are running
Use `docker ps -a` to see all the running containers. You do not need
the '-a' option to see the containers started by your user.

### Passing in AWS credentials
The BES CredentialsManager uses four envirnment variables (or a
configuration file, but this explains the env var feature) to hold the
AWS key id and secret. These are CMAC_URL, CMAC_REGION, CMAKE_ID and
CMAC_ACCESS_KEY. The first two are not 'secret' but the second two
are. The CMAC_URL provides a URL prefix associated with the
credentials. The other credentails will only be used for URLs that
start with this prefix. The CMAC_REGION seems odd because S3 is really
not in a specific region, but when am AWS 'signature' is formed, the
region is part of the signature, so we need to know it.

For pyreader these two env vars should now (5/31/23) be set to:
```bash
CMAC_URL=https://s3-module-test-bucket.s3.us-west-2.amazonaws.com/ \
CMAC_REGION=us-west-2
```
The CMAC_ID is the AWS_ACCESS_KEY_ID and CMAC_ACCESS_KEY is the
AWS_SECRET_ACCESS_KEY.

### How to run besstandalone in the container from the host
TL;DR `docker exec -it -e ... besd besstandalone -c <conf file> -i <command file>`

#### details
The basic command to run a program in a detached running container
(whcih is how the bes container was started above) is with the 'exec'
command. The options -it say to run the program as interactive and
using a tty. A series of -e (aka --env) options are used to pass
various environment variables into the contaiiner. For this command,
these should be:
```bash
--env CMAC_URL=s3-module-test-bucket.s3.us-west-2.amazonaws.com/ \
--env CMAC_REGION=us-west-2 \
--env CMAC_ID=$AWS_ACCESS_KEY_ID \
--env CMAC_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
```
Where the $AWS... env vars are set in the host's environment.

OR

If you have the env vars CMAC\_URL, ... set in your current
environment, the options can be shortened to just --env CMAC\_URL.
That will copy the current value of that var into the container's
environment.

Because we mapped /home/centos/pyreader on the host computer to
/usr/share/pyreader in the container, when the command runs in the
container, the files in /home/centos/pyreader will appear to the
command to be in /usr/share/pyreader. Thus, the file with BES
configureation keys (pyreader-bes-docker.conf) will have the full
pathanme /usr/share/pyreader/pyreader-bes-docker.conf and the various
bes command files that are in /home/centos/pyreader/bescmds with have
the full path /usr/share/pyreader/bescmds/...

#### See s3_reader_cmd.sh
The bash script `s3-reader-cmd.sh` packages all of this. It's pretty
brittle, but it illustrates the point about how to run besstandalone.

