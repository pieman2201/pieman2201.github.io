# Disabling the dGPU on my XPS 15 9570

I'm compiling the list of steps I followed here, partly so that I remember what I did, and also so that anyone else encountering the same irritation might find this concise-ish solution.

For some background, my XPS 15 has Intel graphics alongside an Nvidia GTX 1050 Ti mobile GPU. I don't do anything graphically demanding under Arch Linux, so I sought to disable the GPU for the sake of longer battery life. I tried the recommended solution on the Arch wiki, but unfortunately my GPU would turn on seemingly at random; the only thing I could do was run `systemctl suspend` and hope that the GPU would stay off upon resuming. This was clearly frustrating, so I decided to figure out a more effective solution.

After a fair amount of searching, I ended up with a set of modifications as follows. I took most of this from a [helpful post on the Dell subreddit](https://old.reddit.com/r/Dell/comments/d3dizj).

1. Install acpi_call (`yay -S acpi_call` or `acpi_call-lts`)
2. Create a file `/etc/modules-load.d/acpi_call.conf` with the contents:

    ```bash
    acpi_call
    ```
3. Create a file `/etc/modprobe.d/blacklist.conf` with the contents:

    ```
    install nouveau /bin/true
    blacklist nouveau
    ```
4. Create a file `/etc/tmpfiles.d/acpi_call.conf` with the contents:

    ```
    w /proc/acpi/call - - - - \\_SB.PCI0.PEG0.PEGP._OFF
    ```
5. Create a file `/etc/tmpfiles.d/remove_gpu.conf` with the contents:

    ```
    w /sys/bus/pci/devices/0000\:01\:00.0/remove - - - - 1
    ```
6. Create a file `/etc/systemd/system/root-resume.service` with the contents:

    ```
    [Unit]
    Description=Local system resume actions
    After=suspend.target

    [Service]
    Type=simple
    ExecStart=/usr/bin/sh -c "echo '\_SB.PCI0.PEG0.PEGP._OFF' > /proc/acpi/call"

    [Install]
    WantedBy=suspend.target
    ```
7. Enable/start the service with `systemctl enable` and `systemctl start`
8. Install powertop (`yay -S powertop`)
9. Run `powertop` while unplugged from the wall, and check the discharge rate (mine was ~12W at idle whenever my GPU was on)
10. Reboot
11. Run `powertop` again to observe significantly lower discharge rates (mine was ~5W at idle after disablingt the GPU)

When the computer boots, the GPU is turned off through acpi_call (this also happens whenever the system resumes from sleep). Furthermore, on boot, the device is removed from the Linux's list of connected PCI devices; as a result, the device won't show up anymore in `lspci`. This part solved a problem I had where certain programs would somehow cause the GPU to awaken (e.g. Mathematica, Zoom).

This fix has been very solid for me thus far, at least on the current LTS kernel (5.10.35). I use i8kutils for my fan control, and I'd often notice that my temperature thresholds would be ignored by the computer. I think this is because of a bug/feature in Dell's BIOS where the fan automatically kicks in when the dGPU is active; even with the dell-bios-fan-control utility, I couldn't override this behavior. Now, I haven't noticed my fans spinning unwantedly at all
