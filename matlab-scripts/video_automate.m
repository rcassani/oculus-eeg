% Automates the SSVEP experiments
clear all
close all
clc

%% Parameters

video1 = 1;
video2 = 2;
time_between = 5;

mules_path = 'C:\Program Files (x86)\MuSAE_Lab\MuLES\mules.exe';
videoplayer_path = 'D:\Users\cassani\Documents\GitHub\oculus-eeg\ssvep_server.exe';

% Number of DEVICE in MuLES config.ini file
mules_device = 'DEVICE03';

%% Execute other software
%Allows to run a program using Command Line (without showing command line)
runtime = java.lang.Runtime.getRuntime();

% Execute MuLES
runtime.exec( [mules_path, ' -- "', mules_device, '"', ' PORT=30000 LOG=T TCP=T &']);

% Execute Unity SSVEP executable
% runtime.exec([ssvep_path, ' &']);
% pause(10);

%% Create TCP connections
% TCP Client for MuLES
mules = MulesClient('localhost', 30000);

%% TCP Client for Unity
unity = tcpip('localhost', 40000, 'NetworkRole', 'client');
unity.Timeout = 60000;
unity.OutputBufferSize = 5000;
fopen(unity);

%% Wait for Unity App
pause(3);

%% Video experiment

tone(500,500);
% Send command to Unity
fwrite(unity, video1, 'int32');
% Send trigger to MuLES
mules.sendtrigger(video1);
% Waits until the video is ended
video1_end = fread(unity, 1, 'int32');
% Send trigger to MuLES
mules.sendtrigger(video1_end);

pause(time_between);  

tone(500,500);
% Send command to Unity
fwrite(unity, video2, 'int32');
% Send trigger to MuLES
mules.sendtrigger(video2);
% Waits until the video is ended
video2_end = fread(unity, 1, 'int32');
% Send trigger to MuLES
mules.sendtrigger(video2_end);

%% Send Kill signal
% Unity 
fwrite(unity, 66, 'int32')
% MuLES
mules.kill();

%% Close TCP connections
fclose(unity);