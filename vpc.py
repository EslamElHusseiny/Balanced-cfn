#!/usr/bin/python
from troposphere import FindInMap, GetAtt, Join
from troposphere import Parameter, Output, Ref, Select, Tags, Template
import troposphere.ec2 as ec2
  
  
template = Template()
  
keyname_param = template.add_parameter(Parameter(
    "KeyName",
    Description="Name of an existing EC2 KeyPair to enable SSH "
                "access to the instance",
    Type="String",
))
  
vpcid_param = template.add_parameter(Parameter(
    "VpcId",
    Description="VpcId of your existing Virtual Private Cloud (VPC)",
    Type="String",
))
  
zk1_subnetid_param = template.add_parameter(Parameter(
    "SubnetId",
    Description="SubnetId of an existing subnet (for the primary network) in "
                "your Virtual Private Cloud (VPC)" "access to the instance",
    Type="String",
))

sshlocation_param = template.add_parameter(Parameter(
    "SSHLocation",
    Description="The IP address range that can be used to SSH to the "
                "EC2 instances",
    Type="String",
    MinLength="9",
    MaxLength="18",
    Default="0.0.0.0/0",
    AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})"
                   "/(\\d{1,2})",
    ConstraintDescription="must be a valid IP CIDR range of the "
                          "form x.x.x.x/x."
))
  
template.add_mapping('RegionMap', {
    "us-east-1": {"AMI": "ami-76817c1e"},
    "us-west-1": {"AMI": "ami-f0d3d4b5"},
    "us-west-2": {"AMI": "ami-d13845e1"},
    "eu-west-1": {"AMI": "ami-892fe1fe"}
})
### Security Groups Stuff ###
###########  To Be Implemented later  ####################
kafka_sg = template.add_resource(ec2.SecurityGroup(
    "KafkaSecurityGroup",
    VpcId=Ref(vpcid_param),
    GroupDescription="Enable SSH, Kafka access via ports 22, bla bla bla",
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp=Ref(sshlocation_param),
        ),
    ],
))
###########  EOTBIL  ####################  

zk_sg = template.add_resource(ec2.SecurityGroup(
    "ZooKeeperSecurityGroup",
    VpcId=Ref(vpcid_param),
    GroupDescription="Enable SSH, ZooKeeper access via ports 22, 2888, 3888, and 2181",
    SecurityGroupIngress=[
	ec2.SecurityGroupRule(
            FromPort="22",
	    ToPort="22",
    	    IpProtocol="tcp",
	    CidrIp=Ref(sshlocation_param),
	),
    ],
))

template.add_resource(ec2.SecurityGroupIngress(
    "SecurityGroupIngress1",
    GroupId=Ref(zk_sg),
    SourceSecurityGroupId=Ref(zk_sg),
    FromPort="2888",
    ToPort="2888",
    IpProtocol="tcp",
))
    
template.add_resource(ec2.SecurityGroupIngress(
    "SecurityGroupIngress2",
    GroupId=Ref(zk_sg),
    SourceSecurityGroupId=Ref(zk_sg),
    FromPort="3888",
    ToPort="3888",
    IpProtocol="tcp",
))

template.add_resource(ec2.SecurityGroupIngress(
    "SecurityGroupIngress3",
    GroupId=Ref(zk_sg),
    SourceSecurityGroupId=Ref(kafka_sg),
    FromPort="2181",
    ToPort="2181",
    IpProtocol="tcp",
))
### End of Security Groups Stuff ###

### Ec2 instances ###
zk1_ec2_instance = template.add_resource(ec2.Instance(
    "EC2Instance",
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    KeyName=Ref(keyname_param),
    SecurityGroupIds=[Ref(zk_sg),],
    SubnetId=Ref(zk1_subnetid_param),
    InstanceType="t2.micro",
    Tags=Tags(Name="ZooKeeper Instance 1",),
    PrivateIpAddress="10.0.0.55",
))
### END of Ec2 instances ###

### Outputs ###  
template.add_output([
    Output(
        "InstanceId",
        Description="InstanceId of the newly created EC2 instance",
        Value=Ref(zk1_ec2_instance),
    ),
])
### End of outputs ###
  
print(template.to_json())
