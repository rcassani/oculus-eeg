% Automates the SSVEP experiments
clear all
close all
clc

%% Parameters
time_step = 2;

nn =  90;
nw = 135;
ww = 180;
sw = 225;
ss = 270;
se = 315;
ee =   0;
ne =  45;
cc = 777;

mules_path = 'C:\Program Files (x86)\MuSAE_Lab\MuLES\mules.exe';
eog_path = 'C:\Users\student\Documents\GitHub\oculus-eeg\unity-app\Builds\ssvep\ssvep_server.exe';

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
unity.OutputBufferSize = 5000;
fopen(unity);

%% Wait for Unity App
pause(3);

%% EOG experiment

tone(500,500);

steps = [nn, ss, ww, ee];
for n_step = 1 : numel(steps)
    step = steps(n_step);
    % Send command to Unity
    fwrite(unity, step, 'int32');
    % Send trigger to MuLES
    mules.sendtrigger(round(step/45)+1);
    pause(time_step);  
    % Send command to Unity
    fwrite(unity, cc, 'int32');
    % Send trigger to MuLES
    mules.sendtrigger(round(step/45)+1);
    pause(time_step);  
end

%% Send Kill signal
% Unity 
fwrite(unity, 660, 'int32')
% MuLES
mules.kill();

%% Close TCP connections
fclose(unity);