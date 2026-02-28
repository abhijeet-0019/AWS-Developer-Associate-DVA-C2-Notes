# VPC Notes

## Subnet
- **Definition**: Splitting a network to ensure specific teams/users can access a particular set of network addresses, enhancing data security.
- **Advantages**: Security, privacy, isolation.
- **Types**: Private and Public.
- **Key Points**:
  - When creating a VPC, IP addresses are requested.
  - Subnets have a **CIDR range**, which determines the number of available IP addresses.
  - CIDR examples:
    - `/24` → 256 IPs
    - `/28` → 16 IPs
    - `/16` → 65,536 IPs
  - Use CIDR calculators for precise calculations.

## Ports
- **Purpose**: Bind applications to specific ports within a VPC.
- **Key Points**:
  - Multiple applications in a VPC can be bound to different ports.
  - To access an application, you need:
    - **IP Address**
    - **Port Number**

## OSI Model
- **Overview**: Logical layers representing steps in data communication.
- **Process**:
  1. **DNS Resolution**: Request goes through local cache, router, ISP, and DNS resolution.
  2. **TCP Handshake**: Three-way handshake between server and requester (SYN → SYN/ACK → ACK).
  3. **Layered Communication**:
     - **L7: Application Layer**: Request initiation.
     - **L6: Presentation Layer**: Data encryption/formatting.
     - **L5: Session Layer**: Session creation between browser and server.
       - *Above three layers operate at the browser level.*
     - **L4: Transport Layer**: Data segmentation, protocol identification (TCP/UDP).
     - **L3: Network Layer**: Data packets routed through multiple hops.
     - **L2: Data Link Layer**: Data transformed from packets to frames, MAC info added.
     - **L1: Physical Layer**: Data transmitted via optical/electronic cables.




## Practicals || TODO
- How to create a subnet in a home Wi-Fi network?
