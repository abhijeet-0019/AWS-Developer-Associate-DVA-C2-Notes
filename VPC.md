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




## VIRTUAL PRIVATE CLOUD - AWS

### Request Flow: User → AWS Application
**Flow Path**: `Internet → IGW → Public Subnet → Load Balancer → Route Tables → Security Groups → Application`

---

## 🔴 Internet Gateway (IGW)
### Definition
- **Horizontally scaled**, redundant, and highly available VPC component
- Allows communication between VPC instances and the internet
- **One VPC = One IGW** (1:1 relationship)

### Key Points
- No bandwidth constraints
- Does **NOT** perform NAT for instances with private IPs
- Must be attached to VPC to function
- Route table must have route pointing to IGW for internet access

### Exam Traps ⚠️
- **Confusion**: IGW vs NAT Gateway
  - **IGW**: Allows instances with **public IPs** to access internet
  - **NAT Gateway**: Allows instances with **private IPs** to access internet (outbound only)

---

## 🔵 Public vs Private Subnets

### Public Subnet
- Has a route to **Internet Gateway (0.0.0.0/0 → IGW)**
- Instances can have public IPs
- Resources are accessible from internet (if Security Group allows)

### Private Subnet
- **NO direct route** to Internet Gateway
- Uses **NAT Gateway/Instance** for outbound internet access
- More secure for databases, application servers

### Critical Exam Point 🎯
**What makes a subnet "public"?**
- **NOT** the subnet itself
- The **Route Table** associated with it must have a route to IGW

**Example Route Table Entry:**
```
Destination       Target
10.0.0.0/16      local
0.0.0.0/0        igw-xxxxx  ← This makes it public
```

---

## ⚖️ Load Balancer in VPC

### Types (Exam Focus)
1. **Application Load Balancer (ALB)** - Layer 7 (HTTP/HTTPS)
   - Path-based routing: `/api` → API servers, `/images` → Image servers
   - Host-based routing: `api.example.com` vs `www.example.com`
   - WebSocket and HTTP/2 support
   
2. **Network Load Balancer (NLB)** - Layer 4 (TCP/UDP)
   - Ultra-low latency
   - Handles millions of requests per second
   - Static IP support
   
3. **Gateway Load Balancer (GWLB)** - Layer 3 (IP packets)
   - For third-party virtual appliances

### Subnet Requirements ⚠️
- **ALB/NLB must be in at least 2 Availability Zones**
- Must be deployed in **public subnets** (if internet-facing)
- Internal load balancers use private subnets

**Common Confusion:**
- Q: Can ALB be in private subnet?
- A: Yes, for **internal** load balancers routing traffic within VPC

---

## 🛣️ Route Tables

### Definition
- Contains rules (routes) to determine where network traffic is directed
- Each subnet must be associated with a route table

### Key Concepts
- **Main Route Table**: Default for VPC, auto-applied to subnets without explicit association
- **Custom Route Tables**: Created for specific routing needs

### Route Priority
- **Most specific route wins** (longest prefix match)
  ```
  Destination       Target         Priority
  10.0.1.0/24      local          ← More specific (wins)
  10.0.0.0/16      local
  0.0.0.0/0        igw-xxxxx      ← Least specific (default)
  ```

### Exam Scenarios 🎯

**Scenario 1: Public Subnet Route Table**
```
Destination       Target
10.0.0.0/16      local          # VPC CIDR - internal traffic
0.0.0.0/0        igw-xxxxx      # Internet traffic
```

**Scenario 2: Private Subnet Route Table**
```
Destination       Target
10.0.0.0/16      local             # VPC CIDR
0.0.0.0/0        nat-xxxxx         # Internet via NAT Gateway
```

**Scenario 3: VPC Peering**
```
Destination       Target
10.0.0.0/16      local             # This VPC
172.31.0.0/16    pcx-xxxxx         # Peered VPC
0.0.0.0/0        igw-xxxxx         # Internet
```

---

## 🔒 Security Groups (SG) vs Network ACLs (NACL)

### ⚠️ MOST CRITICAL EXAM TOPIC - Know This Cold!

| Feature | Security Groups (SG) | Network ACLs (NACL) |
|---------|---------------------|---------------------|
| **Level** | Instance level | Subnet level |
| **State** | **STATEFUL** (return traffic auto-allowed) | **STATELESS** (must explicitly allow return traffic) |
| **Rules** | ALLOW rules only | ALLOW and DENY rules |
| **Rule Processing** | All rules evaluated | Rules processed in order (lowest number first) |
| **Default** | All inbound DENIED, all outbound ALLOWED | Default NACL: ALL allowed |
| **Application** | Must be explicitly assigned to instance | Automatically applies to all instances in subnet |
| **Rule Limits** | 60 inbound + 60 outbound per SG | 20 rules per NACL (soft limit) |

---

### 🔴 Security Groups - Deep Dive

#### Key Characteristics
- **Stateful**: If you allow inbound request, outbound response is automatically allowed
- **Whitelist only**: Cannot create DENY rules
- **Default**: Deny all inbound, allow all outbound

#### Practical Example
```yaml
Security Group: web-server-sg
Inbound Rules:
  - Type: HTTP, Protocol: TCP, Port: 80, Source: 0.0.0.0/0
  - Type: HTTPS, Protocol: TCP, Port: 443, Source: 0.0.0.0/0
  - Type: SSH, Protocol: TCP, Port: 22, Source: 203.0.113.0/24

Outbound Rules:
  - Type: All traffic, Protocol: All, Port: All, Destination: 0.0.0.0/0
```

**What this means:**
- Web traffic from anywhere can reach server (port 80/443)
- SSH only from specific IP range (203.0.113.0/24)
- Server can initiate connections to anywhere
- **Return traffic for all inbound requests automatically allowed (STATEFUL)**

#### Reference Other Security Groups 🎯
```yaml
Security Group: app-server-sg
Inbound Rules:
  - Type: Custom TCP, Port: 8080, Source: alb-sg  ← References another SG!
  
# This means: Only traffic from resources with "alb-sg" can access port 8080
```

**Exam Tip**: This pattern is common for layered security architecture!

---

### 🔵 Network ACLs - Deep Dive

#### Key Characteristics
- **Stateless**: Must explicitly allow both request AND response traffic
- **Numbered rules**: Evaluated in order (Rule #100 before #200)
- **Default NACL**: Allows all inbound/outbound traffic
- **Custom NACL**: Denies all traffic by default until you add rules

#### Rule Processing 🎯
```yaml
NACL Rules (Inbound):
Rule #   Type      Protocol   Port    Source         Action
100      HTTP      TCP        80      0.0.0.0/0      ALLOW
200      HTTPS     TCP        443     0.0.0.0/0      ALLOW
300      SSH       TCP        22      203.0.113.0/24 ALLOW
*        ALL       ALL        ALL     0.0.0.0/0      DENY
```

**Processing**: Rules checked from lowest to highest. First match wins!
- Rule #100 matches → ALLOW (stops processing)
- If no match, continues to next rule
- `*` is implicit DENY at the end

#### Ephemeral Ports - CRITICAL Concept ⚠️

**Problem**: For STATELESS NACLs, you must allow return traffic

**Example Scenario:**
1. User makes request to web server on port 80
2. Server responds from port 80 to user's **ephemeral port** (1024-65535)
3. You must allow outbound traffic on ephemeral ports!

```yaml
NACL Rules for Public Subnet:
Inbound:
  Rule #100: HTTP, TCP, 80, 0.0.0.0/0, ALLOW
  Rule #110: HTTPS, TCP, 443, 0.0.0.0/0, ALLOW
  Rule #120: Return traffic, TCP, 1024-65535, 0.0.0.0/0, ALLOW  ← Ephemeral ports!
  Rule #*: ALL, ALL, ALL, 0.0.0.0/0, DENY

Outbound:
  Rule #100: HTTP, TCP, 80, 0.0.0.0/0, ALLOW
  Rule #110: HTTPS, TCP, 443, 0.0.0.0/0, ALLOW
  Rule #120: Ephemeral ports, TCP, 1024-65535, 0.0.0.0/0, ALLOW  ← Required!
  Rule #*: ALL, ALL, ALL, 0.0.0.0/0, DENY
```

**Exam Question Pattern 🔥:**
> "Users cannot access your web application even though Security Groups are configured correctly. What could be the issue?"
> 
> **Answer**: NACL blocking traffic OR Ephemeral ports not allowed in NACL

---

### 🔥 SG vs NACL: Exam Scenarios

#### Scenario 1: Blocking Specific IP Address
**Question**: You need to block a specific malicious IP (203.0.113.50) from accessing your application.

**Solution**: 
- ✅ **Use NACL**: Create DENY rule for that IP with low rule number
- ❌ **Cannot use Security Group**: SG only supports ALLOW rules

```yaml
NACL Inbound Rules:
Rule #50: ALL, ALL, ALL, 203.0.113.50/32, DENY     ← Blocks malicious IP
Rule #100: ALL, ALL, ALL, 0.0.0.0/0, ALLOW
```

---

#### Scenario 2: Instance Can't Connect to RDS Database
**Troubleshooting Checklist:**
1. ✅ Check RDS Security Group - Does it allow inbound from application SG?
2. ✅ Check Application Security Group - Does it allow outbound to RDS?
3. ✅ Check Subnet NACLs - Both subnets allowing required traffic?
4. ✅ Check Route Tables - Can subnets communicate?

**Common Issue**: RDS in private subnet, NACL denying ephemeral port responses

---

#### Scenario 3: Layered Security (Best Practice)
```
Internet (0.0.0.0/0)
    ↓
[NACL - Public Subnet] ← Broad filtering (DENY malicious IPs)
    ↓
[Security Group - ALB] ← Allow 80/443 from internet
    ↓
[NACL - Private Subnet] ← Allow traffic from public subnet
    ↓
[Security Group - App Server] ← Allow 8080 from ALB SG only
    ↓
[Security Group - RDS] ← Allow 3306 from App Server SG only
```

**Exam Favorite**: "What's the most secure way to allow application servers to access database?"
- ✅ **Reference app server SG in RDS SG** (not IP addresses)

---

## 📊 Complete Request Flow Example

### Architecture
```
User PC (Internet)
    ↓
Internet Gateway (IGW)
    ↓
Public Subnet (10.0.1.0/24)
├── NACL Rules: Allow 80/443 + ephemeral ports
└── Load Balancer (ALB)
    └── SG: Allow 80/443 from 0.0.0.0/0
        ↓
Private Subnet (10.0.2.0/24)
├── NACL Rules: Allow 8080 from public subnet + ephemeral
└── Application Servers
    └── SG: Allow 8080 from ALB-SG
        ↓
Private Subnet (10.0.3.0/24)
├── NACL Rules: Allow 3306 from app subnet + ephemeral
└── RDS Database
    └── SG: Allow 3306 from App-Server-SG
```

### Step-by-Step Flow 🔄

1. **User Request** (198.51.100.25:52000 → ALB:443)
   ```
   User browser → DNS resolution → ALB public IP
   ```

2. **Internet Gateway**
   - Receives packet from internet
   - Routes to VPC based on destination IP
   - No NAT (public IP preserved)

3. **Public Subnet - Inbound NACL Check** ✓
   ```yaml
   Rule #100: HTTPS, TCP, 443, 0.0.0.0/0, ALLOW ← Matches, ALLOW
   ```

4. **ALB Security Group - Inbound Check** ✓
   ```yaml
   Rule: HTTPS, TCP, 443, 0.0.0.0/0, ALLOW ← Matches, ALLOW
   ```

5. **ALB Processes Request**
   - SSL termination
   - Routes to target group (app servers in private subnet)
   - Health check ensures target is healthy

6. **Private Subnet - Inbound NACL Check** ✓
   ```yaml
   Rule #100: Custom TCP, 8080, 10.0.1.0/24, ALLOW ← From public subnet
   ```

7. **App Server Security Group - Inbound Check** ✓
   ```yaml
   Rule: Custom TCP, 8080, alb-sg, ALLOW ← From ALB SG
   ```

8. **Application Processes Request**
   - Needs database query
   - Connects to RDS on port 3306

9. **RDS Security Group - Inbound Check** ✓
   ```yaml
   Rule: MySQL, TCP, 3306, app-server-sg, ALLOW ← From App SG
   ```

10. **Return Path (Response)**
    - RDS → App Server: **SG is stateful** → Auto-allowed
    - App Server → ALB: **SG is stateful** → Auto-allowed
    - NACL checks (stateless):
      ```yaml
      # Private subnet outbound NACL
      Rule #100: Ephemeral, TCP, 1024-65535, 10.0.1.0/24, ALLOW
      
      # Public subnet inbound NACL (return from app)
      Rule #120: Ephemeral, TCP, 1024-65535, 10.0.2.0/24, ALLOW
      
      # Public subnet outbound NACL (to internet)
      Rule #100: HTTPS, TCP, 443, 0.0.0.0/0, ALLOW
      
      # Note: Ephemeral ports critical for NACL return traffic!
      ```

---

## 🎯 Exam Tips & Common Confusions

### Confusion #1: "My subnet isn't accessible from internet"
**Checklist:**
- ✅ Route table has route to IGW (0.0.0.0/0 → igw-xxx)?
- ✅ Instance has public IP or Elastic IP?
- ✅ Security Group allows traffic?
- ✅ NACL allows inbound AND outbound (stateless)?
- ✅ IGW attached to VPC?

### Confusion #2: "Security Group vs NACL - When to use what?"
**Rule of Thumb:**
- **Security Groups**: Primary defense, instance-level control
- **NACLs**: Secondary defense, subnet-level control, DENY specific IPs
- **Best Practice**: Use both (defense in depth)

### Confusion #3: "NAT Gateway vs Internet Gateway"
| Feature | Internet Gateway | NAT Gateway |
|---------|-----------------|-------------|
| **Purpose** | Internet access for public IPs | Internet access for private IPs |
| **Direction** | Bidirectional | Outbound only |
| **Cost** | Free | Charged per hour + data processed |
| **Placement** | VPC level | Public subnet |
| **Availability** | Highly available by default | Deploy in multiple AZs for HA |
| **Instances** | Must have public/Elastic IP | Uses private IPs |

### Confusion #4: "Default VPC vs Custom VPC"
**Default VPC:**
- Created automatically in each region
- CIDR: 172.31.0.0/16
- Public subnet in each AZ
- IGW attached
- All instances get public IPs by default

**Custom VPC:**
- You define CIDR block
- You create subnets
- You attach IGW (if needed)
- Public IPs not assigned by default

**Exam Tip**: You can have **1 default VPC** + **up to 5 custom VPCs per region** (soft limit)

### Confusion #5: "VPC Peering Transitivity"
**CRITICAL**: VPC peering is **NOT transitive**

```
VPC-A ↔ VPC-B ↔ VPC-C
```

❌ VPC-A **cannot** talk to VPC-C through VPC-B
✅ Must create direct peering: VPC-A ↔ VPC-C

**Why?**: Security isolation, prevents unintended access

---

## 🔥 High-Frequency Exam Questions

### Q1: Stateful vs Stateless - Pick the Difference
**Security Groups**: 
- ✅ Stateful - return traffic automatically allowed
- ✅ If inbound rule allows port 80, response automatically allowed

**NACLs**:
- ✅ Stateless - must explicitly allow both directions
- ✅ Must allow ephemeral ports for return traffic (1024-65535)

### Q2: Blocking Malicious IP
**Scenario**: Block specific IP from accessing your application
- ❌ Cannot use Security Group (no DENY rules)
- ✅ Use NACL with DENY rule

### Q3: Public Subnet Requirements
To make a subnet public, you need:
1. ✅ IGW attached to VPC
2. ✅ Route table with 0.0.0.0/0 → IGW
3. ✅ Instance must have public/Elastic IP
4. ✅ Security Group allows traffic
5. ✅ NACL allows traffic

### Q4: Load Balancer Placement
- **Internet-facing ALB**: Must be in **public subnets** across ≥2 AZs
- **Internal ALB**: Can be in **private subnets**
- **Targets (EC2)**: Can be in **private subnets** even for internet-facing ALB

### Q5: NAT Gateway Best Practices
For high availability:
- ✅ Deploy NAT Gateway in **each AZ**
- ✅ Each private subnet's route table points to NAT Gateway in **same AZ**
- ❌ Don't share one NAT Gateway across all AZs (single point of failure)

---

## 💡 Quick Reference - Security Decision Tree

```
Need to block specific IP?
    └→ Use NACL (DENY rule)

Instance-level control?
    └→ Use Security Group

Subnet-level control?
    └→ Use NACL

Stateful processing needed?
    └→ Use Security Group

Need DENY rules?
    └→ Use NACL (SG can't DENY)

Referencing other security groups?
    └→ Use Security Group (NACL uses CIDR only)

Order matters for rules?
    └→ Use NACL (numbered rules processed in order)

All rules evaluated?
    └→ Use Security Group (evaluates all rules)
```

---

## 📝 Must-Remember for Exam

1. **SG = Stateful, NACL = Stateless** (asked in every exam!)
2. **SG = ALLOW only, NACL = ALLOW + DENY**
3. **Public subnet = Route table with IGW** (not the subnet itself)
4. **One VPC = One IGW** (1:1 relationship)
5. **NACL rules processed in order** (lowest number first)
6. **Ephemeral ports (1024-65535)** required for NACL return traffic
7. **VPC peering is NOT transitive**
8. **Security Groups can reference other SGs** (best practice for layered architecture)
9. **NAT Gateway in public subnet** for private instance internet access
10. **Default NACL = ALL allowed**, Custom NACL = ALL denied initially


## Practicals || TODO
- How to create a subnet in a home Wi-Fi network?
