using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class VideoExperimentBehaviour : MonoBehaviour {
    public int ServerPort = 40000;
    public GameObject video1;
    public GameObject video2;
    public GameObject video3;
    public GameObject video4;
    public GameObject video5;
    public GameObject video6;

    private TcpIpServer tcp_server;
    private UnityEngine.Video.VideoPlayer video1Player;
    private UnityEngine.Video.VideoPlayer video2Player;
    private UnityEngine.Video.VideoPlayer video3Player;
    private UnityEngine.Video.VideoPlayer video4Player;
    private UnityEngine.Video.VideoPlayer video5Player;
    private UnityEngine.Video.VideoPlayer video6Player;

    private bool video1_remoteplay = false;
    private bool video2_remoteplay = false;
    private bool video3_remoteplay = false;
    private bool video4_remoteplay = false;
    private bool video5_remoteplay = false;
    private bool video6_remoteplay = false;



    // Use this for initialization
    void Start () {
        // Create TCP Server and Block until Client is connected
        tcp_server = new TcpIpServer("0.0.0.0", ServerPort);
        video1Player = video1.GetComponent<UnityEngine.Video.VideoPlayer>();
        video2Player = video2.GetComponent<UnityEngine.Video.VideoPlayer>();
        video3Player = video3.GetComponent<UnityEngine.Video.VideoPlayer>();
        video4Player = video4.GetComponent<UnityEngine.Video.VideoPlayer>();
        video5Player = video5.GetComponent<UnityEngine.Video.VideoPlayer>();
        video6Player = video6.GetComponent<UnityEngine.Video.VideoPlayer>();

        video1Player.Prepare();
        video2Player.Prepare();
        video3Player.Prepare();
        video4Player.Prepare();
        video5Player.Prepare();
        video6Player.Prepare();

        
    
    }

    // Update is called once per frame
    void Update () {
        if (this.tcp_server.IsDataAvailable())
        {
            int command = this.tcp_server.ReadCommand();
            Debug.Log("Command: " + command.ToString());
            switch (command)
            {
                case 1:
                    print("Play Video1");
                    video1Player.Play();
                    video1_remoteplay = true;
                    break;

                case 2:
                    print("Play Video2");
                    video2Player.Play();
                    video2_remoteplay = true;
                    break;
                case 3:
                    print("Play Video3");
                    video3Player.Play();
                    video3_remoteplay = true;
                    break;

                case 4:
                    print("Play Video4");
                    video4Player.Play();
                    video4_remoteplay = true;
                    break;
                case 5:
                    print("Play Video5");
                    video5Player.Play();
                    video5_remoteplay = true;
                    break;

                case 6:
                    print("Play Video6");
                    video6Player.Play();
                    video6_remoteplay = true;
                    break;
                    
                case 66:
                    Application.Quit();
                    break;

            }
        }

        if (video1_remoteplay & !video1Player.isPlaying)
        {
            video1_remoteplay = false;
            tcp_server.WriteInt32(11);
            print("Trigger for Video 1 end");
            video1Player.Stop();
        }

        if (video2_remoteplay & !video2Player.isPlaying)
        {
            video2_remoteplay = false;
            tcp_server.WriteInt32(12);
            print("Trigger for Video 2 end");
            video2Player.Stop();
        }

        if (video3_remoteplay & !video3Player.isPlaying)
        {
            video3_remoteplay = false;
            tcp_server.WriteInt32(13);
            print("Trigger for Video 3 end");
            video3Player.Stop();
        }

        if (video4_remoteplay & !video4Player.isPlaying)
        {
            video4_remoteplay = false;
            tcp_server.WriteInt32(14);
            print("Trigger for Video 4 end");
            video4Player.Stop();
        }

        if (video5_remoteplay & !video5Player.isPlaying)
        {
            video5_remoteplay = false;
            tcp_server.WriteInt32(15);
            print("Trigger for Video 5 end");
            video5Player.Stop();
        }

        if (video6_remoteplay & !video6Player.isPlaying)
        {
            video6_remoteplay = false;
            tcp_server.WriteInt32(16);
            print("Trigger for Video 6 end");
            video6Player.Stop();
        }


    }
}
