# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/trusty64"

  config.vm.network "forwarded_port", guest: 8000, host: 8000, host_ip: "0.0.0.0", guest_ip: "0.0.0.0"
  config.vm.network "forwarded_port", guest: 5555, host: 5555, host_ip: "localhost", guest_ip: "localhost"

  config.vm.network "private_network", ip: "192.168.10.14"
  config.vm.synced_folder ".", "/home/vagrant/quarterly_report_project", type: "nfs"

  config.vm.provision :shell, privileged: false, path: "bootstrap.sh"
  config.vm.provision :shell, privileged: false, path: "startup.sh", run: "always"
end
