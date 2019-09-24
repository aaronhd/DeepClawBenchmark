# Copyright (c) 2019 by liuxiaobo. All Rights Reserved.
# !/usr/bin/python
# coding=utf-8
import socket
import time
import struct
import math
import urx
import numpy as np

class URController:
    def __init__(self,robot_ip = "192.168.31.10", port = 30003):
        self.__robot_ip = robot_ip
        self.__port = port
        self.PICK_Z = 0.16
        self.PLACE_Z = 0.172
        self.calibration_tool = ''
        # self.robot = urx.Robot("192.168.31.10")
        # self.robot.get_pose()
        # self.urmonitor = self.robot.get_realtime_monitor()
        # self.goHome()
        # time.sleep(5)

    def get_pos(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((self.__robot_ip, self.__port))
            s.send("get_state()"+"\n")
            time.sleep(0.1)
            packet_1 = s.recv(444)

            packet_12 = s.recv(8)
            packet_12 = packet_12.encode("hex") #convert the data from \x hex notation to plain hex
            x = str(packet_12)
            x = struct.unpack('!d', packet_12.decode('hex'))[0]
            # print("X = ", x * 1000)

            packet_13 = s.recv(8)
            packet_13 = packet_13.encode("hex") #convert the data from \x hex notation to plain hex
            y = str(packet_13)
            y = struct.unpack('!d', packet_13.decode('hex'))[0]
            # print("Y = ", y * 1000)

            packet_14 = s.recv(8)
            packet_14 = packet_14.encode("hex") #convert the data from \x hex notation to plain hex
            z = str(packet_14)
            z = struct.unpack('!d', packet_14.decode('hex'))[0]
            # print("Z = ", z * 1000)

            packet_15 = s.recv(8)
            packet_15 = packet_15.encode("hex") #convert the data from \x hex notation to plain hex
            Rx = str(packet_15)
            Rx = struct.unpack('!d', packet_15.decode('hex'))[0]
            # print "Rx = ", Rx

            packet_16 = s.recv(8)
            packet_16 = packet_16.encode("hex") #convert the data from \x hex notation to plain hex
            Ry = str(packet_16)
            Ry = struct.unpack('!d', packet_16.decode('hex'))[0]
            # print "Ry = ", Ry

            packet_17 = s.recv(8)
            packet_17 = packet_17.encode("hex") #convert the data from \x hex notation to plain hex
            Rz = str(packet_17)
            Rz = struct.unpack('!d', packet_17.decode('hex'))[0]
            # print "Rz = ", Rz
            beta = (1-2*3.14/math.sqrt(Rx*Rx+Ry*Ry+Rz*Rz))
            Rx = Rx * beta
            Ry = Ry * beta
            Rz = Rz * beta
            pose = np.zeros(6)
            # pose[0] = x*1000.0
            # pose[1] = y*1000.0
            # pose[2] = z*1000.0
            pose[0] = x
            pose[1] = y
            pose[2] = z
            pose[3] = Rx
            pose[4] = Ry
            pose[5] = Rz
            return pose
            # print("Rx = ", Rx)
            # print("Ry = ", Ry)
            # print("Rz = ", Rz)
            s.close()
        except socket.error as socketerror:
            print("Error: ", socketerror)
    #
    # def get_pos(self):
    #     pose = self.urmonitor.tcf_pose()
    #     return pose

    def goHome(self):
        print('homing...')
        self.move([[0.0986, -0.54, 0.2], [3.14, 0, 0]])
        # self.move([[-61.3, -103.53, -139.63], [-26.82, 90, 27.77]], useJoint=True)
    
    def move(self, goal_pose, a=0.5, v=0.6,useJoint = False):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((self.__robot_ip, self.__port))
        # time.sleep(0.05)

        goal_position = goal_pose[0]
        goal_orientation = goal_pose[1]

        if(useJoint==False):
            # s.send ("movej(p[ %f, %f, %f, %f, %f, %f], a = %f, v = %f)\n" %(x/1000.0,y/1000.0,z/1000.0,Rx,Ry,Rz,a,v))
            x, y, z = goal_position[0], goal_position[1], goal_position[2]
            Rx, Ry, Rz = self.rpy2rotation(goal_orientation[0], goal_orientation[1], goal_orientation[2])
            s.send ("movej(p[ %f, %f, %f, %f, %f, %f], a = %f, v = %f)\n" %(x,y,z,Rx,Ry,Rz,a,v))
            self.verifyPostion([x, y, z, Rx, Ry, Rz])
        else:
            #radian of each joint
            x, y, z = goal_position[0], goal_position[1], goal_position[2]
            Rx, Ry, Rz = goal_orientation[0], goal_orientation[1], goal_orientation[2]
            s.send ("movej([ %f, %f, %f, %f, %f, %f], a = %f, v = %f)\n" %(x*3.14159/180.0,y*3.14159/180.0,z*3.14159/180.0,Rx*3.14159/180.0,Ry*3.14159/180.0,Rz*3.14159/180.0,a,v))
        time.sleep(0.2)
        s.close()

    def openGripper(self):
        pass

    def closeGripper(self):
        pass

    def verifyPostion(self, targetPosition):
        delay_time = True
        cnt = 0
        timeGap = 1
        while(delay_time and cnt < 100):
            currentPose = self.get_pos()
            # print(targetPosition)
            # print(currentPose)
            dpose = np.zeros(6)
            inv_dpose = np.zeros(6)
            dpose[0] = abs(currentPose[0]-targetPosition[0])
            dpose[1] = abs(currentPose[1]-targetPosition[1])
            dpose[2] = abs(currentPose[2]-targetPosition[2])
            dpose[3] = abs(currentPose[3]-targetPosition[3])
            dpose[4] = abs(currentPose[4]-targetPosition[4])
            dpose[5] = abs(currentPose[5]-targetPosition[5])

            inv_dpose[0] = abs(currentPose[0]-targetPosition[0])
            inv_dpose[1] = abs(currentPose[1]-targetPosition[1])
            inv_dpose[2] = abs(currentPose[2]-targetPosition[2])
            inv_dpose[3] = abs(-currentPose[3]-targetPosition[3])
            inv_dpose[4] = abs(-currentPose[4]-targetPosition[4])
            inv_dpose[5] = abs(-currentPose[5]-targetPosition[5])

            if (max(dpose) < 0.01 or max(inv_dpose) < 0.01):
                delay_time = False
                return True
            else:
                time.sleep(timeGap)
                cnt = cnt + 1
            if(cnt*timeGap >= 20):
                print("Time Out!")
                return False

    def rpy2rotation(self, roll, pitch, yaw):
        yawMatrix = np.matrix([
            [math.cos(yaw), -math.sin(yaw), 0],
            [math.sin(yaw), math.cos(yaw), 0],
            [0, 0, 1]
        ])

        pitchMatrix = np.matrix([
            [math.cos(pitch), 0, math.sin(pitch)],
            [0, 1, 0],
            [-math.sin(pitch), 0, math.cos(pitch)]
        ])

        rollMatrix = np.matrix([
            [1, 0, 0],
            [0, math.cos(roll), -math.sin(roll)],
            [0, math.sin(roll), math.cos(roll)]
        ])

        R = yawMatrix * pitchMatrix * rollMatrix
        theta = math.acos(((R[0, 0] + R[1, 1] + R[2, 2]) - 1) / 2)
        multi = 1 / (2 * math.sin(theta))
        rx = multi * (R[2, 1] - R[1, 2]) * theta
        ry = multi * (R[0, 2] - R[2, 0]) * theta
        rz = multi * (R[1, 0] - R[0, 1]) * theta
        rotation = np.zeros(3)
        rotation[0] = rx
        rotation[1] = ry
        rotation[2] = rz
        return rotation

if __name__ == '__main__':
    ip = "192.168.1.10"
    port = 30003
    robotController = URController(ip,port)
    home_tcp_position = [91.02, -87.85, -138.34, -44.5, 90, -0.0,True]
    robotController.movej(home_tcp_position[0], home_tcp_position[1], home_tcp_position[2], home_tcp_position[3], home_tcp_position[4], home_tcp_position[5], 0.4, 0.6,True)
    time.sleep(0.5)
    robotController.verifyPostion(home_tcp_position)
