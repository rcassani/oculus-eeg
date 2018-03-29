% Automates the SSVEP experiments
clear all
close all
clc

%% Parameters
time_open = 30;
time_blink = 30;
time_closed = 30;

mules_path = 'C:\Program Files (x86)\MuSAE_Lab\MuLES\mules.exe';
ssvep_path = 'D:\Users\cassani\Documents\GitHub\oculus-eeg\ssvep_server.exe';

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
% TCP Client for Unity
unity = tcpip('localhost', 40000, 'NetworkRole', 'client');
unity.OutputBufferSize = 5000;
fopen(unity);

%% Wait for Unity App
pause(3);

%% Phase 1, Open Eyes
command = 10;
% Send audio command
[y,Fs] = audioread('./support/open.mp3');
sound(y,Fs);
tone(500,500);

% Send command to Unity
fwrite(unity, command, 'int32')
pause(5);

% Send trigger to MuLES
mules.sendtrigger(command);

% Wait X seconds
pause(time_open);

% Send trigger to MuLES
mules.sendtrigger(command);


%% Phase 2, Blinking SSVEP
command = 20;
% Send audio command
[y,Fs] = audioread('./support/blink.mp3');
sound(y,Fs);
tone(500,500);

% Send command to Unity
fwrite(unity, command, 'int32')
pause(5);

% Send trigger to MuLES
mules.sendtrigger(command);

% Wait X seconds
pause(time_open);

% Send trigger to MuLES
mules.sendtrigger(command);


%% Phase 3, Close Eyes
command = 30;
% Send audio command
[y,Fs] = audioread('./support/closed.mp3');
sound(y,Fs);
tone(500,500);

% Send command to Unity
fwrite(unity, command, 'int32')
pause(5);

% Send trigger to MuLES
mules.sendtrigger(command);

% Wait X seconds
pause(time_open);

% Send trigger to MuLES
mules.sendtrigger(command);


%% Send Kill signal
% Unity 
fwrite(unity, 66, 'int32')
% MuLES
mules.kill();

%% Close TCP connections
fclose(unity);