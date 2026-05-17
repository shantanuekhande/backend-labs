# AWS EC2 System Optimization & Troubleshooting Guide
## VS Code Remote-SSH Resource Exhaustion & Memory Management

When working with memory-constrained cloud environments, such as AWS EC2 Free Tier `t2.micro` or `t3.micro` instances with only 1 GiB of RAM, running remote development tools alongside application services can quickly exhaust memory.

This guide explains why a normal SSH terminal usually stays stable while VS Code Remote-SSH may crash, how the Linux kernel handles memory pressure, and how adding swap space can reduce these failures.

---

## 1. Why a Normal SSH Terminal Works Fine

When you connect to an EC2 instance using a normal terminal command like:

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

that session is very lightweight.

A normal SSH terminal mainly runs:

- the `sshd` process
- a shell such as `bash`
- simple text input/output over the SSH connection

The memory usage is usually very small, often around **10–15 MiB**. Because of this, the terminal can stay connected even when the server is under heavy memory pressure.

In simple words: a terminal is mostly just sending and receiving text. It does not need a big background runtime.

---

## 2. Why VS Code Remote-SSH Uses Much More Memory

VS Code Remote-SSH is very different from a plain SSH terminal.

When you connect using VS Code Remote-SSH, VS Code installs and runs a **VS Code Server** on the EC2 instance. This server runs on a headless Node.js runtime and supports many IDE features directly from the remote machine.

```text
+------------------+          SSH Tunnel           +----------------------------+
|                  | ============================> | AWS EC2 Instance (1 GiB)   |
| Local Computer   |                               |                            |
| VS Code IDE      | <============================ | VS Code Remote Server      |
|                  |  file sync, extensions, IPC   | Node.js runtime            |
+------------------+                               +----------------------------+
                                                       |
                                                       v
                                             Uses additional RAM
                                             for indexing, extensions,
                                             language servers, and sync
```

VS Code Remote-SSH may run several background components:

- **Workspace indexing:** tracks project files and changes.
- **Extension host:** runs extensions such as Python, Docker, linters, autocomplete, and language servers.
- **File watchers:** monitor file changes in the remote project.
- **IPC and sync processes:** keep the local VS Code UI connected with the remote server.

This can easily consume **hundreds of MiB of RAM**, especially when working with Docker, Django, PostgreSQL, or large project folders.

So even if your EC2 instance looks fine with normal SSH, VS Code may push it over the memory limit.

---

## 3. What Happens When RAM Is Exhausted

A small EC2 instance with 1 GiB RAM may already be running several memory-consuming processes:

- Ubuntu system services
- Docker daemon
- Django app process
- PostgreSQL container
- Nginx container
- VS Code Remote Server
- language server extensions

When total memory demand becomes higher than available RAM, Linux tries to protect the system from freezing completely.

It does this using the **OOM Killer**.

OOM means **Out Of Memory**.

The OOM Killer checks running processes and kills one or more of them to free memory. It often targets processes that are consuming a lot of RAM. In this case, the VS Code Remote Server or its Node.js process may become the target.

That is why this can happen:

```text
Normal SSH terminal      -> still connected
VS Code Remote-SSH       -> disconnected or crashed
EC2 server itself        -> still running
```

The server did not necessarily shut down. Most likely, Linux killed the memory-heavy VS Code process.

---

## 4. Solution: Add Swap Space

Swap is disk space that Linux can use as overflow memory when physical RAM is full.

It is not as fast as real RAM, because disk is slower than memory. But on a small EC2 instance, swap can prevent sudden crashes by giving Linux extra breathing room.

For a 1 GiB RAM instance, adding a **2 GiB swap file** is a practical setup.

---

## 5. Commands to Add a 2 GiB Swap File

### Step 1: Create the swap file

```bash
sudo fallocate -l 2G /swapfile
```

This creates a 2 GiB file at `/swapfile`.

`fallocate` is fast because it reserves disk space directly instead of writing zeroes byte by byte.

---

### Step 2: Secure the swap file

```bash
sudo chmod 600 /swapfile
```

This makes the file readable and writable only by the root user.

This is important because swap may contain memory data from running processes. You do not want normal users or processes to read it.

---

### Step 3: Format the file as swap

```bash
sudo mkswap /swapfile
```

This prepares the file so Linux can use it as swap memory.

---

### Step 4: Enable swap

```bash
sudo swapon /swapfile
```

This activates the swap file immediately.

---

### Step 5: Make swap permanent after reboot

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

This adds the swap file to `/etc/fstab`, so Linux automatically enables it whenever the EC2 instance restarts.

---

## 6. Verify Swap Is Enabled

Use this command:

```bash
free -h
```

You should see output similar to:

```text
               total        used        free      shared  buff/cache   available
Mem:           965Mi        ...         ...       ...     ...          ...
Swap:          2.0Gi        0B          2.0Gi
```

You can also check with:

```bash
swapon --show
```

Expected output:

```text
NAME       TYPE  SIZE USED PRIO
/swapfile  file  2G   0B   -2
```

---

## 7. How to Remove Swap Later

If you later upgrade to a larger EC2 instance, such as one with 2 GiB or 4 GiB RAM, you may choose to remove the swap file.

### Step 1: Disable swap

```bash
sudo swapoff /swapfile
```

This stops Linux from using the file as swap.

---

### Step 2: Delete the swap file

```bash
sudo rm /swapfile
```

This removes the 2 GiB file and frees disk space.

---

### Step 3: Remove the permanent entry from `/etc/fstab`

```bash
sudo sed -i '/\/swapfile none swap sw 0 0/d' /etc/fstab
```

This removes the swap entry so the system does not try to mount a missing swap file after reboot.

---

## 8. Resource Comparison

| Metric | Normal SSH Terminal | VS Code Remote-SSH |
|---|---|---|
| Average memory usage | Very low, often around 10–15 MiB | Much higher, often hundreds of MiB |
| Main runtime | `sshd` + shell | Remote Node.js server |
| Background activity | Minimal | Indexing, extensions, file watchers |
| OOM risk | Low | Higher on 1 GiB RAM servers |
| Best use case | Server commands and quick debugging | Full remote IDE workflow |

---

## 9. Practical Recommendation

For small EC2 instances, especially `t2.micro` or `t3.micro`, use this setup:

- Add a 2 GiB swap file.
- Avoid running too many heavy VS Code extensions remotely.
- Stop unused Docker containers.
- Use normal SSH for quick server work.
- Use VS Code Remote-SSH only when you need full IDE features.

Swap does not make the instance powerful, but it helps prevent sudden crashes caused by memory spikes.

---

## 10. Final Mental Model

Think of it like this:

```text
RAM  = fast working table
Swap = slower backup table

Without swap:
If RAM becomes full, Linux may kill a process.

With swap:
Linux gets extra overflow space, so processes are less likely to be killed immediately.
```

So the reason VS Code crashes while SSH survives is not because SSH is more reliable as a network protocol. It is because VS Code Remote-SSH runs a much heavier remote server process on your EC2 instance.
