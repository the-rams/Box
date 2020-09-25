import os
import wget
import tarfile
import getopt
import sys
import yaml
import subprocess

path = "/var/lib/box"
base_path = path + "/base"
init_path = os.getcwd()


def box():


    if not os.path.exists(path):
        subprocess.call("sudo mkdir " + path, shell=True)
        subprocess.call("sudo chmod 777 " + path, shell=True)
    if not os.path.exists(base_path):
        subprocess.call("sudo mkdir " + base_path, shell=True)
        subprocess.call("sudo chmod 777 " + path, shell=True)
        os.chdir(base_path)
        subprocess.call("ls -l ../", shell=True)
        dirname = wget.download("https://github.com/debuerreotype/docker-debian-artifacts/raw/"
                        "3503997cf522377bc4e4967c7f0fcbcb18c69fc8/buster/slim/rootfs.tar.xz")
        tar = tarfile.open(dirname, "r:xz")
        tar.extractall()
        tar.close()
        try:
            os.remove(dirname)
        except OSError as e:
            print("Error: %s : %s" % (tar, e.strerror))


# subprocess.call("debootstrap --arch i386 stretch /var/lib/box htpp://deb.debian.org/debian",shell=True)
# subprocess.call("chroot /var/lib/box",shell=True)
# os.chroot("/var/lib/box")


def key():


    print(wget.download("https://www.mongodb.org/static/pgp/server-4.4.asc", out="tmp_key"))


def parse_yaml(yml_file):


    a_yaml_file = open(yml_file)
    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
    return parsed_yaml_file


def create_env(conf_yaml, gnupg=None):


    os.chdir(init_path)
    conf = parse_yaml(conf_yaml)
    os.chdir(path)
    print("Prise en compte du fichier de conf: " + conf_yaml)
    if not os.path.isdir("./env"):
        print("Répertoire env non trouvé, création du repertoire env.")
    os.mkdir("./env")
    if not os.path.isdir("./env/" + conf["name"]):
        print("Création du repertoire " + conf["name"] + ".")
    os.mkdir("./env/" + conf["name"])
    path_env = path + "/env/" + conf["name"]

    os.chdir(path_env)
    dirname = wget.download("https://github.com/debuerreotype/docker-debian-artifacts/raw/"
                            "3503997cf522377bc4e4967c7f0fcbcb18c69fc8/buster/slim/rootfs.tar.xz")
    tar = tarfile.open(dirname, "r:xz")
    tar.extractall()
    tar.close()
    try:
        os.remove(dirname)
    except OSError as e:
      print("Error: %s : %s" % (tar, e.strerror))

    os.system("apt-get update && apt-get upgrade")
    os.system("sudo apt-get install gnupg")
    os.system("wget -qO - " + conf["repositories"][0]["key"] + " | sudo apt-key add -")
    os.system(
        "echo \"" + conf["repositories"][0]["repository"] + "\" | sudo tee /etc/apt/sources.list.d/" + conf["requirements"][
            0] + ".list")
    # os.system("echo \""+ conf["repositories"][0]["repository"] +"\" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list")
    os.system("apt-get update")
    os.system("sudo apt-get install -y " + conf["requirements"][0])
    print(conf["name"] + " installed.")

    os.system("cp /etc/hosts " + path_env + "/etc/hosts")
    os.system("cp /etc/resolv.conf " + path_env + "/etc/resolv.conf")
    os.system("sudo mount -t proc /proc " + path_env + "/proc")
    os.system("sudo mount -t sysfs /sys " + path_env + "/sys")
    os.system("sudo mount --bind /dev " + path_env + "/dev")
    os.system("sudo chroot " + path_env)
    print("Chroot done new root repertory set to" + conf["name"] + ".")


    # print(conf["repositories"][0]["repository"])
    # key_repo = wget.download(conf["repositories"][0]["key"], out='./')
    # print(key_repo)

    # gpg = gnupg.GPG(gnupghome='/etc/apt/trusted.gpg')
    # key_data = open(key_repo).read()
    # import_result = gpg.import_keys(key_data)
    # pprint(import_result.results)


def build_image(conf_yaml):


    path = "/var/lib/box/"
    if len(sys.argv) >= 2 and sys.argv[0] == "box" and sys.argv[1] == "build":
        fileBuild = sys.argv[2]

    path_to_list = "/etc/apt/sources.list.d/mongodb-org-4.4.list"
    conf = parse_yaml(conf_yaml)

    with open(path_to_list, "a") as file_list:
        file_list.write(conf["repositories"][0]["key"])

    if not os.path.exists(path):
        os.makedirs(path + conf["repositories"][0]["name"], mode=0o751)

box()
create_env("mongo.yml")


def create_alias():


    subprocess.call("echo \"alias box='sudo python3 \"" + init_path + "\"/main.py'\" >> ~/.bashrc && exec bash",
                    shell=True)

# box()
