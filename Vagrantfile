# -*- mode: ruby -*-

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

$provision_script = <<EOF
set -e
echo "Installing deps..."
apt-get install -y sox python-pip normalize-audio
sudo -u vagrant /vagrant/compile-and-install-lame.sh
pip install -e /vagrant
EOF

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "trusty64"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

  config.vm.synced_folder "files", "/home/vagrant/files"

  config.vm.provision "shell", inline: $provision_script

end
